from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AutomationLog, DailyReport, Invoice, Message, Order, Task


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_daily_totals(self, report_date: date) -> dict[str, Decimal | int]:
        start_of_day = datetime.combine(report_date, time.min)
        end_of_day = start_of_day + timedelta(days=1)

        total_messages = (
            self.db.query(func.count(Message.id))
            .filter(Message.created_at >= start_of_day, Message.created_at < end_of_day)
            .scalar()
            or 0
        )
        total_orders = (
            self.db.query(func.count(Order.id))
            .filter(Order.created_at >= start_of_day, Order.created_at < end_of_day)
            .scalar()
            or 0
        )
        total_invoices = (
            self.db.query(func.count(Invoice.id))
            .filter(Invoice.created_at >= start_of_day, Invoice.created_at < end_of_day)
            .scalar()
            or 0
        )
        total_revenue = (
            self.db.query(func.sum(Invoice.total_amount))
            .filter(Invoice.created_at >= start_of_day, Invoice.created_at < end_of_day)
            .scalar()
            or Decimal("0.00")
        )

        return {
            "total_messages": int(total_messages),
            "total_orders": int(total_orders),
            "total_invoices": int(total_invoices),
            "total_revenue": Decimal(total_revenue),
        }

    def get_open_task_count(self) -> int:
        return (
            self.db.query(func.count(Task.id))
            .filter(Task.status == "open")
            .scalar()
            or 0
        )

    def get_daily_report(self, report_date: date) -> DailyReport | None:
        return (
            self.db.query(DailyReport)
            .filter(DailyReport.report_date == report_date)
            .first()
        )

    def create_or_update_daily_report(
        self,
        *,
        report_date: date,
        total_messages: int,
        total_orders: int,
        total_invoices: int,
        total_revenue: Decimal,
        summary: str,
    ) -> DailyReport:
        report = self.get_daily_report(report_date)
        if report is None:
            report = DailyReport(report_date=report_date)
            self.db.add(report)

        report.total_messages = total_messages
        report.total_orders = total_orders
        report.total_invoices = total_invoices
        report.total_revenue = total_revenue
        report.summary = summary
        self.db.flush()
        self.db.refresh(report)
        return report

    def mark_report_sent(
        self,
        *,
        report: DailyReport,
        sent_via: str,
    ) -> DailyReport:
        report.sent_via = sent_via
        report.sent_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(report)
        return report

    def create_automation_log(
        self,
        *,
        daily_report_id: int | None,
        event_type: str,
        status: str,
        target_system: str,
        payload: str | None = None,
        response_message: str | None = None,
    ) -> AutomationLog:
        log = AutomationLog(
            daily_report_id=daily_report_id,
            event_type=event_type,
            status=status,
            target_system=target_system,
            payload=payload,
            response_message=response_message,
        )
        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)
        return log
