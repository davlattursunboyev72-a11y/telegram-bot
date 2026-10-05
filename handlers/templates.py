import os
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

import config
from data.templates_info import get_templates, get_template_file_paths
from utils.sub_checker import check_user_subscription
from keyboards.inline import (
    get_templates_keyboard,
    get_template_action_keyboard,
    get_subscription_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

async def verify_sub_or_notify(bot: Bot, user_id: int, target) -> bool:
    """
    Har qanday harakatdan oldin foydalanuvchi obunasini tekshiruvchi yordamchi funksiya.
    Agar obuna bo'lmasa, ogohlantirish xabarini yuboradi.
    """
    is_subscribed, _ = await check_user_subscription(
        bot=bot,
        user_id=user_id,
        channel_id=config.CHANNEL_ID
    )
    
    if not is_subscribed:
        sub_text = (
            f"⚠️ <b>Shablonlardan foydalanish uchun avval kanalimizga obuna bo'ling:</b>\n"
            f"👉 <a href='{config.CHANNEL_URL}'>{config.CHANNEL_NAME}</a>\n\n"
            f"Obuna bo'lgach, «🔄 Obunani tekshirish» tugmasini bosing:"
        )
        if isinstance(target, CallbackQuery):
            await target.answer("❌ Avval kanalimizga a'zo bo'ling!", show_alert=True)
            await target.message.answer(
                text=sub_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_subscription_keyboard(config.CHANNEL_URL)
            )
        elif isinstance(target, Message):
            await target.answer(
                text=sub_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_subscription_keyboard(config.CHANNEL_URL)
            )
        return False
    return True

@router.message(F.text == "🎬 Edit shablonlar")
@router.message(Command("templates"))
async def show_templates_menu(message: Message, bot: Bot):
    """
    '🎬 Edit shablonlar' tugmasi yoki /templates komandasi bosilganda
    shablonlar ro'yxatini chiqaradi.
    """
    user_id = message.from_user.id
    if not await verify_sub_or_notify(bot, user_id, message):
        return

    text = (
        "🎬 <b>Yazaki Editz — Maxsus Shablonlar Ro'yxati</b>\n\n"
        "Quyidagi ro'yxatdan o'zingizga kerakli shablon yoki preset turini tanlang:\n"
        "Har bir bo'limda tayyor fayllar, XML presetlar va ishlatish yo'riqnomalari mavjud 👇"
    )
    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=get_templates_keyboard()
    )

@router.callback_query(F.data.startswith("tmpl_"))
async def show_template_detail(callback: CallbackQuery, bot: Bot):
    """
    Muayyan shablon tanlanganda uning tafsiloti va yuklab olish tugmalarini chiqaradi.
    """
    user_id = callback.from_user.id
    if not await verify_sub_or_notify(bot, user_id, callback):
        return

    tmpl_id = callback.data.replace("tmpl_", "", 1)
    templates = get_templates()
    tmpl_info = templates.get(tmpl_id)

    if not tmpl_info:
        await callback.answer("⚠️ Shablon topilmadi!", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            text=tmpl_info["description"],
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=get_template_action_keyboard(
                template_id=tmpl_id,
                links=tmpl_info.get("links", [])
            )
        )
        await callback.answer()
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.warning(f"Xabarni tahrirlashda xatolik: {e}")
            await callback.answer()

@router.callback_query(F.data == "back_to_templates")
async def back_to_templates_list(callback: CallbackQuery, bot: Bot):
    """
    Shablonlar ro'yxatiga qaytish.
    """
    user_id = callback.from_user.id
    if not await verify_sub_or_notify(bot, user_id, callback):
        return

    text = (
        "🎬 <b>Yazaki Editz — Maxsus Shablonlar Ro'yxati</b>\n\n"
        "Quyidagi ro'yxatdan o'zingizga kerakli shablon yoki preset turini tanlang:"
    )
    try:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=get_templates_keyboard()
        )
        await callback.answer()
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.warning(f"Ro'yxatga qaytishda xatolik: {e}")
            await callback.answer()

@router.callback_query(F.data.startswith("dl_"))
async def download_template_files(callback: CallbackQuery, bot: Bot):
    """
    Foydalanuvchi '📥 Fayllarni yuklab olish' tugmasini bosganda
    shablonga tegishli fayllarni jo'natadi.
    """
    user_id = callback.from_user.id
    if not await verify_sub_or_notify(bot, user_id, callback):
        return

    tmpl_id = callback.data.replace("dl_", "", 1)
    templates = get_templates()
    tmpl_info = templates.get(tmpl_id)

    if not tmpl_info:
        await callback.answer("⚠️ Shablon topilmadi!", show_alert=True)
        return

    await callback.answer("⏳ Fayllar tayyorlanmoqda, iltimos kuting...", show_alert=False)
    
    files = get_template_file_paths(tmpl_info)
    if not files:
        await callback.message.answer(
            f"ℹ️ <b>{tmpl_info['name']}</b> uchun alohida yuklanadigan fayl yo'q. "
            f"Yuqoridagi havola orqali to'g'ridan-to'g'ri foydalanishingiz mumkin.",
            parse_mode="HTML"
        )
        return

    sent_count = 0
    for file_path in files:
        try:
            if file_path.exists():
                file_size_mb = round(file_path.stat().st_size / (1024 * 1024), 1)
                
                # Agar fayl 49 MB dan katta bo'lsa (Telegram Bot API 50 MB cheklovi):
                if file_path.stat().st_size > 49 * 1024 * 1024:
                    large_msg = (
                        f"📱 <b>{tmpl_info['name']}</b>\n\n"
                        f"ℹ️ Ushbu fayl hajmi <b>{file_size_mb} MB</b> bo'lgani sababli (Telegram botlar uchun 50 MB cheklov mavjud), "
                        f"uni rasmiy kanalimiz orqali yoki quyidagi havoladan yuklab olishingiz mumkin:\n\n"
                        f"👉 <a href='{config.CHANNEL_URL}'>📢 Rasmiy kanalimizdan yuklab olish</a>\n"
                        f"🌐 <a href='http://localhost:5000/download/{file_path.name}'>📥 Localhost orqali yuklash</a>"
                    )
                    await callback.message.answer(
                        text=large_msg,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                    sent_count += 1
                    continue

                input_file = FSInputFile(
                    path=str(file_path),
                    filename=file_path.name
                )
                caption = (
                    f"📁 <b>{tmpl_info['name']}</b>\n"
                    f"✨ <i>Yazaki Editz</i> tomonidan taqdim etildi.\n"
                    f"Kanalimiz: {config.CHANNEL_URL}"
                )
                await bot.send_document(
                    chat_id=user_id,
                    document=input_file,
                    caption=caption,
                    parse_mode="HTML"
                )
                sent_count += 1
            else:
                logger.warning(f"Fayl topilmadi: {file_path}")
        except Exception as e:
            logger.error(f"Fayl yuborishda xatolik ({file_path}): {e}", exc_info=True)

    if sent_count > 0:
        await callback.message.answer(
            f"✅ <b>{tmpl_info['name']}</b> bo'yicha jami <b>{sent_count}</b> ta fayl yuborildi!\n\n"
            f"Marhamat, yuklab olib montajlaringizda bemalol foydalaning. Yana boshqa shablonlar kerak bo'lsa, "
            f"quyidagi tugmani bosing:",
            parse_mode="HTML",
            reply_markup=get_templates_keyboard()
        )
    else:
        await callback.message.answer(
            "⚠️ Fayllarni yuborishda texnik xatolik yuz berdi. Tez orada tuzatiladi!",
            parse_mode="HTML"
        )
