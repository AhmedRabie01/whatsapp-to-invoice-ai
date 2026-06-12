from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_api_key
from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    AutomationLogRead,
    DailyReportRead,
    DailyReportRequest,
    DailyReportResponse,
    SendDailyReportRequest,
    SendDailyReportResponse,
)
from app.services.email_service import EmailService
from app.services.report_generation import ReportGenerationService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=DailyReportResponse)
def generate_daily_report(
    request: DailyReportRequest,
    db: Session = Depends(get_db),
) -> DailyReportResponse:
    repository = ReportRepository(db)
    service = ReportGenerationService(repository)
    report, open_tasks = service.generate_daily_report(request.report_date or date.today())
    db.commit()
    return DailyReportResponse(
        report=DailyReportRead.model_validate(report),
        open_tasks=open_tasks,
    )


@router.post("/send", response_model=SendDailyReportResponse, dependencies=[Depends(verify_api_key)])
def send_daily_report(
    request: SendDailyReportRequest,
    db: Session = Depends(get_db),
) -> SendDailyReportResponse:
    repository = ReportRepository(db)
    report_service = ReportGenerationService(repository)
    email_service = EmailService()

    report, open_tasks = report_service.generate_daily_report(request.report_date or date.today())
    subject = f"Daily SME Workflow Report - {report.report_date.isoformat()}"
    body = report_service.build_email_body(report=report, open_tasks=open_tasks)
    response_message = email_service.send_report_email(
        recipient_email=request.recipient_email,
        subject=subject,
        body=body,
    )
    repository.mark_report_sent(report=report, sent_via="smtp")
    automation_log = repository.create_automation_log(
        daily_report_id=report.id,
        event_type="daily_report_email_dispatch",
        status="sent",
        target_system="smtp",
        payload=f"recipient={request.recipient_email}",
        response_message=response_message,
    )
    db.commit()
    return SendDailyReportResponse(
        report=DailyReportRead.model_validate(report),
        open_tasks=open_tasks,
        recipient_email=request.recipient_email,
        email_sent=True,
        automation_log=AutomationLogRead.model_validate(automation_log),
    )
