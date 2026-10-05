import html
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

import config
from utils.sub_checker import check_user_subscription
from keyboards.reply import get_main_menu_keyboard
from keyboards.inline import get_subscription_keyboard

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    """
    /start buyrug'i uchun handler.
    Foydalanuvchi kanalga a'zo bo'lgan-bo'lmaganini tekshiradi:
    - Obuna bo'lsa: qutlov va asosiy menyuni chiqaradi.
    - Obuna bo'lmasa: kanal havolasi va tekshirish tugmasini chiqaradi.
    """
    user = message.from_user
    user_name = html.escape(user.full_name if user else "Foydalanuvchi")
    
    try:
        is_subscribed, error_code = await check_user_subscription(
            bot=bot,
            user_id=user.id,
            channel_id=config.CHANNEL_ID
        )
        
        if is_subscribed:
            welcome_text = (
                f"👋 Assalomu alaykum, <b>{user_name}</b>!\n\n"
                f"🎬 <b>Yazaki Editz</b> rasmiy botiga xush kelibsiz! ✨\n\n"
                f"Bu yerda siz montaj va video editlar uchun kerakli barcha "
                f"zamonaviy shablonlar, XML presetlar, rang sozlamalari (LUT) "
                f"hamda ovoz effektlarini bepul yuklab olishingiz mumkin.\n\n"
                f"Davom etish uchun quyidagi menyudan kerakli bo'limni tanlang:"
            )
            await message.answer(
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            sub_required_text = (
                f"👋 Assalomu alaykum, <b>{user_name}</b>!\n\n"
                f"⚠️ <b>Botdan to'liq foydalanish uchun avval rasmiy kanalimizga a'zo bo'ling:</b>\n"
                f"👉 <a href='{config.CHANNEL_URL}'>{config.CHANNEL_NAME}</a>\n\n"
                f"Kanalga a'zo bo'lgach, quyidagi <b>«🔄 Obunani tekshirish»</b> tugmasini bosing:"
            )
            await message.answer(
                text=sub_required_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=get_subscription_keyboard(config.CHANNEL_URL)
            )
    except Exception as e:
        logger.error(f"/start komandasini bajarishda xatolik: {e}", exc_info=True)
        await message.answer(
            "⚠️ Tizimda kutilmagan xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."
        )

@router.callback_query(F.data == "check_sub")
async def process_sub_check(callback: CallbackQuery, bot: Bot):
    """
    'Obunani tekshirish' inline tugmasi bosilganda ishga tushadi.
    """
    user = callback.from_user
    user_name = html.escape(user.full_name if user else "Foydalanuvchi")
    
    try:
        is_subscribed, error_code = await check_user_subscription(
            bot=bot,
            user_id=user.id,
            channel_id=config.CHANNEL_ID
        )
        
        if is_subscribed:
            await callback.answer("✅ Rahmat! Obunangiz muvaffaqiyatli tasdiqlandi.", show_alert=False)
            
            # Eski obuna xabarini o'chirish yoki o'zgartirish
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass
            
            welcome_text = (
                f"🎉 <b>Tabriklaymiz, {user_name}!</b>\n\n"
                f"Siz <b>Yazaki Editz</b> a'zosiga aylandingiz. "
                f"Endi botning barcha imkoniyatlaridan bemalol foydalanishingiz mumkin.\n\n"
                f"Quyidagi <b>«🎬 Edit shablonlar»</b> tugmasini bosib fayllarni yuklab oling!"
            )
            await callback.message.answer(
                text=welcome_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await callback.answer(
                "❌ Siz hali kanalga obuna bo'lmadingiz!\nIltimos, avval kanalga a'zo bo'ling.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Obunani tekshirish callback'ida xatolik: {e}", exc_info=True)
        await callback.answer("⚠️ Tekshirishda xatolik yuz berdi. Qayta urinib ko'ring.", show_alert=True)

@router.message(F.text == "📢 Kanalimiz")
async def show_channel_info(message: Message):
    """Kanal haqida ma'lumot va havola."""
    text = (
        f"📢 <b>Bizning rasmiy kanalimiz:</b>\n\n"
        f"Kanalda eng yangi montaj darslari, trend musiqalar va eksklyuziv materiallar e'lon qilinadi.\n\n"
        f"👉 Kanalga o'tish: <a href='{config.CHANNEL_URL}'>{config.CHANNEL_NAME}</a>"
    )
    await message.answer(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.message(F.text == "ℹ️ Bot haqida")
async def show_about_bot(message: Message):
    """Bot haqida ma'lumot."""
    text = (
        f"🎬 <b>Yazaki Editz Bot v1.0</b>\n\n"
        f"Bu bot montajchilar (video editors) uchun quyidagi qulayliklarni taqdim etadi:\n"
        f"• Alight Motion XML presetlari\n"
        f"• CapCut trend shablonlari\n"
        f"• Rang korreksiyasi (Cinematic LUTs)\n"
        f"• Trend sound effektlar (SFX)\n\n"
        f"Savol va takliflar uchun rasmiy kanalimizga murojaat qilishingiz mumkin: {config.CHANNEL_URL}"
    )
    await message.answer(text=text, parse_mode="HTML", disable_web_page_preview=True)
