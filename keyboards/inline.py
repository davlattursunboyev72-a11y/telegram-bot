from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.templates_info import get_templates

def get_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Majburiy obuna kanali havolasi va tekshirish tugmasi."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga a'zo bo'lish",
                    url=channel_url
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Obunani tekshirish",
                    callback_data="check_sub"
                )
            ]
        ]
    )
    return keyboard

def get_templates_keyboard() -> InlineKeyboardMarkup:
    """Barcha mavjud shablonlar ro'yxati inline klaviaturasi."""
    buttons = []
    templates = get_templates()
    
    for tmpl_id, tmpl_info in templates.items():
        buttons.append([
            InlineKeyboardButton(
                text=tmpl_info["name"],
                callback_data=f"tmpl_{tmpl_id}"
            )
        ])
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_template_action_keyboard(template_id: str, links: list = None) -> InlineKeyboardMarkup:
    """Bitta shablon uchun yuklab olish va havola tugmalari."""
    buttons = []
    
    # Tashqi havolalar (masalan, CapCut veb havolasi)
    if links:
        for link in links:
            buttons.append([
                InlineKeyboardButton(
                    text=link["text"],
                    url=link["url"]
                )
            ])
            
    # Faylni to'g'ridan-to'g'ri yuklab olish tugmasi
    buttons.append([
        InlineKeyboardButton(
            text="📥 Fayllarni yuklab olish",
            callback_data=f"dl_{template_id}"
        )
    ])
    
    # Orqaga qaytish tugmasi
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Shablonlar ro'yxatiga qaytish",
            callback_data="back_to_templates"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
