import json
import logging
from pathlib import Path
from config import BASE_DIR, ASSETS_DIR

logger = logging.getLogger(__name__)
STORAGE_FILE = BASE_DIR / "data" / "templates.json"

DEFAULT_TEMPLATES = {
    "shake_by_yazaki_nati_nati": {
        "id": "shake_by_yazaki_nati_nati",
        "name": "📄 shake by yazaki nati nati.xml",
        "title": "shake by yazaki nati nati.xml",
        "category": "Alight Motion XML",
        "description": (
            "🔥 **shake by yazaki nati nati.xml**\n\n"
            "Alight Motion dasturi uchun maxsus XML silkinish (shake) preseti.\n\n"
            "📥 **Qanday ishlatiladi:**\n"
            "1. Quyidagi «📥 Fayllarni yuklab olish» tugmasini bosing.\n"
            "2. Yuklangan `.xml` faylni Alight Motion ilovasiga import qiling!"
        ),
        "files": ["shake by yazaki nati nati.xml"],
        "links": []
    },
    "wave_shake_by_yazaki_amz": {
        "id": "wave_shake_by_yazaki_amz",
        "name": "🌊 Wave shake  by (yazaki_amz).xml",
        "title": "Wave shake  by (yazaki_amz).xml",
        "category": "Alight Motion XML",
        "description": (
            "🌊 **Wave shake  by (yazaki_amz).xml**\n\n"
            "Alight Motion uchun to'lqinsimon (wave) silkinish preseti.\n\n"
            "📥 **Qanday ishlatiladi:**\n"
            "1. Quyidagi «📥 Fayllarni yuklab olish» tugmasini bosing.\n"
            "2. Faylni yuklab olib, Alight Motion loyihangizga import qiling!"
        ),
        "files": ["Wave shake  by (yazaki_amz).xml"],
        "links": []
    },
    "shakes_by_yazaki_amz": {
        "id": "shakes_by_yazaki_amz",
        "name": "💥 𝗦𝗵𝗮𝗸𝗲𝘀 by - [yazaki_amz).xml",
        "title": "𝗦𝗵𝗮𝗸𝗲𝘀 by - [yazaki_amz).xml",
        "category": "Alight Motion XML",
        "description": (
            "💥 **𝗦𝗵𝗮𝗸𝗲𝘀 by - [yazaki_amz).xml**\n\n"
            "Alight Motion uchun sara silkinish effektlari XML to'plami.\n\n"
            "📥 Quyidagi tugma orqali faylni yuklab oling va Alight Motion ilovasida oching!"
        ),
        "files": ["𝗦𝗵𝗮𝗸𝗲𝘀 by - [yazaki_amz).xml"],
        "links": []
    },
    "shake_by_yazaki_amz": {
        "id": "shake_by_yazaki_amz",
        "name": "⚡ Shake by (yazaki_amz.xml",
        "title": "Shake by (yazaki_amz.xml",
        "category": "Alight Motion XML",
        "description": (
            "⚡ **Shake by (yazaki_amz.xml**\n\n"
            "Musiqa ritmiga va basga mos tushuvchi shake effekti preseti.\n\n"
            "📥 Faylni yuklab olib, Alight Motion ilovasiga import qiling!"
        ),
        "files": ["Shake by (yazaki_amz.xml"],
        "links": []
    },
    "amzp_ori_apk": {
        "id": "amzp_ori_apk",
        "name": "📱 AMZP_ORI_10AUG (1).apk",
        "title": "AMZP_ORI_10AUG (1).apk",
        "category": "Ilova / APK",
        "description": (
            "📱 **AMZP_ORI_10AUG (1).apk**\n\n"
            "Barcha XML presetlarni to'liq qo'llab-quvvatlovchi, suv belgisiz (no watermark) "
            "Alight Motion Pro ilovasi.\n\n"
            "📥 Quyidagi tugma orqali ilovani yuklab oling va o'rnating!"
        ),
        "files": ["AMZP_ORI_10AUG (1).apk"],
        "links": [
            {"text": "📢 Kanalimizdan yuklab olish", "url": "https://t.me/yazaki_edits"},
            {"text": "🌐 Localhost orqali yuklash", "url": "http://localhost:5000/download/AMZP_ORI_10AUG%20(1).apk"}
        ]
    }
}

def load_templates() -> dict:
    """Shablonlar bazasini yuklaydi. Agar fayl bo'lmasa, default nusxani yaratadi."""
    if not STORAGE_FILE.exists():
        save_templates(DEFAULT_TEMPLATES)
        return DEFAULT_TEMPLATES.copy()
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"Shablonlar faylini o'qishda xatolik: {e}", exc_info=True)
        return DEFAULT_TEMPLATES.copy()

def save_templates(templates: dict):
    """Shablonlarni JSON faylga saqlaydi."""
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Shablonlarni saqlashda xatolik: {e}", exc_info=True)

def add_template(template_data: dict) -> bool:
    """Yangi shablon qo'shish."""
    templates = load_templates()
    tmpl_id = template_data.get("id")
    if not tmpl_id:
        return False
    templates[tmpl_id] = template_data
    save_templates(templates)
    return True

def delete_template(template_id: str) -> bool:
    """Shablonni o'chirish."""
    templates = load_templates()
    if template_id in templates:
        del templates[template_id]
        save_templates(templates)
        return True
    return False

def get_template_file_paths(template: dict) -> list[Path]:
    """Shablonga biriktirilgan fayllarning to'liq yo'lini qaytaradi."""
    paths = []
    for fname in template.get("files", []):
        file_path = ASSETS_DIR / fname
        paths.append(file_path)
    return paths
