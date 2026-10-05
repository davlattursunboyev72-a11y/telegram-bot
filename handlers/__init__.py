from aiogram import Router
from .start import router as start_router
from .templates import router as templates_router

def setup_routers() -> Router:
    """Asosiy routerga barcha routerlarni ulash."""
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(templates_router)
    return main_router
