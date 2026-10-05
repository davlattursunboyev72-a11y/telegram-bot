import sys
import asyncio
import logging
from aiohttp import web

# Windows konsolida emojilar va UTF-8 belgilari xatosiz chiqishi uchun
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

import config
from web.server import create_web_app, bot_manager

HOST = "127.0.0.1"
PORT = 5000

async def main():
    """Asosiy ishga tushirish funksiyasi (Localhost Web Server + Telegram Bot)."""
    # aiohttp veb serverini tayyorlash
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print("\n" + "=" * 62)
    print("🎬 Yazaki Editz — Localhost Boshqaruv Paneli Faol!")
    print(f"🌐 Brauzeringizda oching: http://localhost:{PORT}")
    print(f"🔗 Muqobil havola:       http://{HOST}:{PORT}")
    print("=" * 62 + "\n")

    # Telegram botni ishga tushirish
    await bot_manager.start()

    # Dasturning to'xtovsiz ishlashini ta'minlash
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Server to'xtatilmoqda...")
        await bot_manager.stop()
        await runner.cleanup()
        logger.info("Barcha xizmatlar to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Dastur foydalanuvchi tomonidan to'xtatildi.")
