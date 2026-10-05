from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu Reply klaviaturasi."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎬 Edit shablonlar"),
            ],
            [
                KeyboardButton(text="📢 Kanalimiz"),
                KeyboardButton(text="ℹ️ Bot haqida"),
            ]
        ],
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Quyidagi bo'limlardan birini tanlang..."
    )
    return keyboard
