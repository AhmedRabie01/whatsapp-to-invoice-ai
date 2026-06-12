from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from dashboard.data_access import DashboardDataAccess

router = APIRouter(tags=["ui"])

FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"


@router.get("/ui")
def ui_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@router.get("/ui/data")
def ui_data(db: Session = Depends(get_db)) -> dict[str, object]:
    access = DashboardDataAccess(db)
    return access.get_dashboard_payload()
