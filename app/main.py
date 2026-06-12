from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.automation import router as automation_router
from app.api.routes.health import router as health_router
from app.api.routes.messages import router as messages_router
from app.api.routes.orders import router as orders_router
from app.api.routes.reports import router as reports_router
from app.api.routes.ui import router as ui_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router)
app.include_router(messages_router)
app.include_router(orders_router)
app.include_router(reports_router)
app.include_router(automation_router)
app.include_router(ui_router)
app.mount("/assets", StaticFiles(directory="frontend"), name="assets")
