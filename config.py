import os
from pathlib import Path
from dotenv import load_dotenv

# Loyihaning asosiy papkasi
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets" / "samples"

# .env faylini yuklash
load_dotenv(BASE_DIR / ".env", override=True)

# Konfiguratsiya o'zgaruvchilari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Kanal ID yoki @username
raw_channel_id = os.getenv("CHANNEL_ID", "@yazaki_edits").strip()
if raw_channel_id.startswith("-100") and raw_channel_id[1:].isdigit():
    CHANNEL_ID = int(raw_channel_id)
else:
    CHANNEL_ID = raw_channel_id

CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/yazaki_edits").strip()
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "Yazaki Edits Official").strip()

import sys

# Windows konsolida emojilar va UTF-8 belgilari xatosiz chiqishi uchun
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def validate_config() -> bool:
    """Konfiguratsiya to'g'ri to'ldirilganligini tekshirish."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n[!] XATOLIK: .env faylida BOT_TOKEN ko'rsatilmagan!")
        print("Iltimos, .env faylini ochib, @BotFather dan olingan bot tokeningizni kiriting.\n")
        return False
    return True
