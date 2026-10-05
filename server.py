import os
import sys
import collections
import logging
import asyncio
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from data.templates_info import (
    get_templates,
    add_template,
    delete_template
)
from handlers import setup_routers

logger = logging.getLogger("web")

# Oxirgi 100 ta log xabarlarini xotirada saqlash uchun buffer
log_buffer = collections.deque(maxlen=100)

class BufferLogHandler(logging.Handler):
    """Loglarni xotiradagi log_buffer ga yozuvchi maxsus handler."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_buffer.append(msg)
        except Exception:
            pass

# Root loggerga buffer handlerni qo'shish
buffer_handler = BufferLogHandler()
buffer_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logging.getLogger().addHandler(buffer_handler)


class BotManager:
    """Telegram Bot hayot tsiklini boshqaruvchi sinf."""
    def __init__(self):
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.polling_task: asyncio.Task | None = None
        self.status: str = "stopped"  # "running", "stopped", "unconfigured", "error"
        self.error_message: str | None = None
        self.bot_info: dict | None = None

    async def start(self):
        """Botni ishga tushirish."""
        if self.status == "running":
            logger.info("Bot allaqachon ishlayapti.")
            return

        if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            self.status = "unconfigured"
            self.error_message = "BOT_TOKEN kiritilmagan"
            logger.warning("Bot token kiritilmagan. Iltimos, veb-paneldan token kiriting.")
            return

        try:
            logger.info("Botga ulanish o'rnatilmoqda...")
            self.bot = Bot(
                token=config.BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            # Bot ma'lumotlarini tekshirish
            me = await self.bot.get_me()
            self.bot_info = {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name
            }
            logger.info(f"Bot ulandi: @{me.username} ({me.first_name})")

            # Dispatcher tayyorlash
            self.dp = Dispatcher()
            self.dp.include_router(setup_routers())

            # Webhookni tozalash va pollingni boshlash
            await self.bot.delete_webhook(drop_pending_updates=True)
            self.polling_task = asyncio.create_task(self._run_polling())
            self.status = "running"
            self.error_message = None
            logger.info("Telegram Bot muvaffaqiyatli ishga tushdi va xabarlarni qabul qilmoqda!")

        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            logger.error(f"Botni ishga tushirishda xatolik: {e}", exc_info=True)
            if self.bot:
                try:
                    await self.bot.session.close()
                except Exception:
                    pass

    async def _run_polling(self):
        """Orqa fonda polling rejimini bajarish."""
        try:
            await self.dp.start_polling(self.bot)
        except asyncio.CancelledError:
            logger.info("Polling to'xtatildi.")
        except Exception as e:
            logger.error(f"Polling paytida kutilmagan xatolik: {e}", exc_info=True)
            self.status = "error"
            self.error_message = str(e)

    async def stop(self):
        """Botni to'xtatish."""
        logger.info("Bot to'xtatilmoqda...")
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        if self.bot:
            try:
                await self.bot.session.close()
            except Exception as e:
                logger.warning(f"Bot sessiyasini yopishda xatolik: {e}")
            self.bot = None

        self.status = "stopped"
        logger.info("Bot to'xtatildi.")

    async def restart(self):
        """Botni qayta yuklash."""
        await self.stop()
        # Yangilangan sozlamalarni yuklash
        import importlib
        from dotenv import load_dotenv
        load_dotenv(config.BASE_DIR / ".env", override=True)
        importlib.reload(config)
        await self.start()


# Global bot menejeri
bot_manager = BotManager()


# ==========================================
# Veb Marshrutlar (Web Routes)
# ==========================================

async def handle_index(request: web.Request) -> web.Response:
    """Asosiy localhost boshqaruv paneli sahifasi."""
    html_path = config.BASE_DIR / "web" / "templates" / "dashboard.html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type="text/html")
    except Exception as e:
        return web.Response(text=f"Sahifani ochishda xatolik: {e}", status=500)

async def handle_api_status(request: web.Request) -> web.Response:
    """Bot holati va ma'lumotlarini JSON formatida qaytarish."""
    templates = get_templates()
    data = {
        "status": bot_manager.status,
        "error_message": bot_manager.error_message,
        "bot_username": bot_manager.bot_info.get("username") if bot_manager.bot_info else None,
        "bot_name": bot_manager.bot_info.get("first_name") if bot_manager.bot_info else None,
        "bot_token": config.BOT_TOKEN if config.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" else "",
        "channel_id": str(config.CHANNEL_ID),
        "channel_url": config.CHANNEL_URL,
        "channel_name": config.CHANNEL_NAME,
        "templates_count": len(templates),
        "templates": templates,
        "logs": list(log_buffer)[-50:]
    }
    return web.json_response(data)

async def handle_api_settings(request: web.Request) -> web.Response:
    """Sozlamalarni saqlash va botni yangilash."""
    try:
        body = await request.json()
        new_token = body.get("bot_token", "").strip()
        new_channel_id = body.get("channel_id", "").strip()
        new_channel_url = body.get("channel_url", "").strip()
        new_channel_name = body.get("channel_name", "").strip()

        if not new_token:
            return web.json_response({"success": False, "error": "Bot token kiritilishi shart!"}, status=400)

        # .env faylini yangilash
        env_path = config.BASE_DIR / ".env"
        env_content = (
            f"# Yazaki Editz Konfiguratsiyasi\n"
            f"BOT_TOKEN={new_token}\n"
            f"CHANNEL_ID={new_channel_id}\n"
            f"CHANNEL_URL={new_channel_url}\n"
            f"CHANNEL_NAME={new_channel_name}\n"
        )
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        logger.info(".env sozlamalari veb-panel orqali yangilandi!")
        # Botni qayta ishga tushirish
        asyncio.create_task(bot_manager.restart())
        return web.json_response({"success": True, "message": "Sozlamalar saqlandi va bot yangilanmoqda."})

    except Exception as e:
        logger.error(f"Sozlamalarni saqlashda xatolik: {e}", exc_info=True)
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def handle_api_restart(request: web.Request) -> web.Response:
    """Botni qayta yuklash API."""
    try:
        asyncio.create_task(bot_manager.restart())
        return web.json_response({"success": True, "message": "Bot qayta ishga tushirilmoqda..."})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def handle_api_templates_add(request: web.Request) -> web.Response:
    """Yangi shablon va fayl qo'shish."""
    try:
        post_data = await request.post()
        tmpl_id = post_data.get("id", "").strip()
        tmpl_name = post_data.get("name", "").strip()
        tmpl_cat = post_data.get("category", "Alight Motion").strip()
        tmpl_desc = post_data.get("description", "").strip()
        tmpl_link = post_data.get("link", "").strip()

        if not tmpl_id or not tmpl_name:
            return web.json_response({"success": False, "error": "ID va Nomi to'ldirilishi shart!"}, status=400)

        uploaded_files = []
        file_field = post_data.get("file")
        if file_field and hasattr(file_field, "filename") and file_field.filename:
            filename = file_field.filename
            file_content = file_field.file.read()
            target_path = config.ASSETS_DIR / filename
            with open(target_path, "wb") as f:
                f.write(file_content)
            uploaded_files.append(filename)
            logger.info(f"Yangi fayl yuklandi: {filename}")

        links = []
        if tmpl_link:
            links.append({"text": "🔗 Ko'rish havolasi", "url": tmpl_link})

        new_tmpl = {
            "id": tmpl_id,
            "name": tmpl_name,
            "title": tmpl_name,
            "category": tmpl_cat,
            "description": tmpl_desc,
            "files": uploaded_files,
            "links": links
        }

        add_template(new_tmpl)
        logger.info(f"Yangi shablon qo'shildi: {tmpl_name} ({tmpl_id})")
        return web.json_response({"success": True, "message": "Shablon muvaffaqiyatli qo'shildi!"})

    except Exception as e:
        logger.error(f"Shablon qo'shishda xatolik: {e}", exc_info=True)
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def handle_api_templates_delete(request: web.Request) -> web.Response:
    """Shablonni o'chirish."""
    tmpl_id = request.match_info.get("id")
    if not tmpl_id:
        return web.json_response({"success": False, "error": "ID ko'rsatilmadi"}, status=400)

    success = delete_template(tmpl_id)
    if success:
        logger.info(f"Shablon o'chirildi: {tmpl_id}")
        return web.json_response({"success": True, "message": "Shablon o'chirildi."})
    else:
        return web.json_response({"success": False, "error": "Shablon topilmadi"}, status=404)

async def handle_download_file(request: web.Request) -> web.Response:
    """Faylni yuklab olish."""
    filename = request.match_info.get("filename")
    file_path = config.ASSETS_DIR / filename
    if not file_path.exists():
        return web.Response(text="Fayl topilmadi", status=404)

    return web.FileResponse(file_path)

def create_web_app() -> web.Application:
    """aiohttp veb ilovasini yaratish va marshrutlarni ulash."""
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/status", handle_api_status)
    app.router.add_post("/api/settings", handle_api_settings)
    app.router.add_post("/api/restart", handle_api_restart)
    app.router.add_post("/api/templates/add", handle_api_templates_add)
    app.router.add_delete("/api/templates/{id}", handle_api_templates_delete)
    app.router.add_get("/download/{filename}", handle_download_file)
    return app
