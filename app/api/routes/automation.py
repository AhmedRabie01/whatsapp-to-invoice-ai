from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_n8n_secret
from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    AutomationDailyReportRequest,
    AutomationDailyReportResponse,
    AutomationLogRead,
    DailyReportRead,
)
from app.services.email_service import EmailService
from app.services.report_generation import ReportGenerationService

router = APIRouter(prefix="/automation", tags=["automation"])


@router.post(
    "/daily-report",
    response_model=AutomationDailyReportResponse,
    dependencies=[Depends(verify_n8n_secret)],
)
def trigger_daily_report(
    request: AutomationDailyReportRequest,
    db: Session = Depends(get_db),
) -> AutomationDailyReportResponse:
    repository = ReportRepository(db)
    report_service = ReportGenerationService(repository)

    report, open_tasks = report_service.generate_daily_report(request.report_date or date.today())

    automation_logs = [
        repository.create_automation_log(
            daily_report_id=report.id,
            event_type="daily_report_automation_trigger",
            status="received",
            target_system="n8n",
            payload=(
                f"report_date={(request.report_date or date.today()).isoformat()},"
                f"send_email={request.send_email},recipient={request.recipient_email or '-'}"
            ),
            response_message="Automation trigger accepted.",
        )
    ]

    email_sent = False
    if request.send_email:
        if not request.recipient_email:
            db.rollback()
            raise HTTPException(status_code=400, detail="recipient_email is required when send_email is true.")

        email_service = EmailService()
        subject = f"Daily SME Workflow Report - {report.report_date.isoformat()}"
        body = report_service.build_email_body(report=report, open_tasks=open_tasks)
        response_message = email_service.send_report_email(
            recipient_email=request.recipient_email,
            subject=subject,
            body=body,
        )
        repository.mark_report_sent(report=report, sent_via="smtp")
        automation_logs.append(
            repository.create_automation_log(
                daily_report_id=report.id,
                event_type="daily_report_email_dispatch",
                status="sent",
                target_system="smtp",
                payload=f"recipient={request.recipient_email}",
                response_message=response_message,
            )
        )
        email_sent = True

    db.commit()
    return AutomationDailyReportResponse(
        report=DailyReportRead.model_validate(report),
        open_tasks=open_tasks,
        email_sent=email_sent,
        automation_logs=[AutomationLogRead.model_validate(log) for log in automation_logs],
    )
