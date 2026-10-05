import logging
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)

async def check_user_subscription(bot: Bot, user_id: int, channel_id: str | int) -> tuple[bool, str | None]:
    """
    Foydalanuvchi ko'rsatilgan kanalga a'zo ekanligini tekshiradi.
    
    Qaytaradi:
        (is_subscribed: bool, error_code: str | None)
        - is_subscribed: True (agar a'zo bo'lsa), False (a'zo bo'lmasa yoki xato yuz bersa)
        - error_code: None, 'not_member', 'bot_not_admin', yoki 'error'
    """
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        # creator, administrator, member - bular obuna bo'lgan hisoblanadi
        if member.status in ("creator", "administrator", "member", "restricted"):
            return True, None
        else:
            return False, "not_member"
    except TelegramAPIError as e:
        error_msg = str(e).lower()
        logger.warning(f"Obunani tekshirishda xatolik yuz berdi (user_id={user_id}, channel={channel_id}): {e}")
        
        if "chat not found" in error_msg:
            logger.error(
                f"Kanal topilmadi: {channel_id}. Iltimos, .env faylida CHANNEL_ID to'g'ri yozilganini "
                f"va bot kanalga administrator qilib qo'shilganini tekshiring!"
            )
            return False, "bot_not_admin"
        elif "user not found" in error_msg:
            # Ba'zi hollarda foydalanuvchi kanalda yo'q bo'lsa 'user not found' qaytishi mumkin
            return False, "not_member"
        else:
            return False, "api_error"
    except Exception as e:
        logger.error(f"Kutilmagan xatolik obuna tekshirishda: {e}", exc_info=True)
        return False, "error"
