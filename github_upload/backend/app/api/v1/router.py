from fastapi import APIRouter
from app.api.v1.webhook import router as webhook_router
from app.api.v1.auth import router as auth_router
from app.api.v1.products import router as products_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.admin.assets import router as admin_assets_router
from app.api.v1.admin.batch_push import router as admin_push_router
from app.api.v1.admin.tags import router as admin_tags_router
from app.api.v1.admin.agents import router as admin_agents_router
from app.api.v1.admin.templates import router as admin_templates_router

api_router = APIRouter()

api_router.include_router(webhook_router)
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(notifications_router)
api_router.include_router(admin_assets_router)
api_router.include_router(admin_push_router)
api_router.include_router(admin_tags_router)
api_router.include_router(admin_agents_router)
api_router.include_router(admin_templates_router)

