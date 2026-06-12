from datetime import date
from decimal import Decimal

from app.repositories.report_repository import ReportRepository


class ReportGenerationService:
    def __init__(self, repository: ReportRepository) -> None:
        self.repository = repository

    def generate_daily_report(self, report_date: date):
        totals = self.repository.get_daily_totals(report_date)
        open_tasks = self.repository.get_open_task_count()
        summary = self._build_summary(
            total_messages=totals["total_messages"],
            total_orders=totals["total_orders"],
            total_invoices=totals["total_invoices"],
            total_revenue=totals["total_revenue"],
            open_tasks=open_tasks,
        )
        report = self.repository.create_or_update_daily_report(
            report_date=report_date,
            total_messages=totals["total_messages"],
            total_orders=totals["total_orders"],
            total_invoices=totals["total_invoices"],
            total_revenue=totals["total_revenue"],
            summary=summary,
        )
        return report, open_tasks

    def build_email_body(self, *, report, open_tasks: int) -> str:
        return (
            f"Daily Report for {report.report_date.isoformat()}\n\n"
            f"Total messages: {report.total_messages}\n"
            f"Total orders: {report.total_orders}\n"
            f"Total documents: {report.total_invoices}\n"
            f"Total revenue (AED): {Decimal(report.total_revenue):.2f}\n"
            f"Open tasks: {open_tasks}\n\n"
            f"Summary:\n{report.summary or 'No summary available.'}\n"
        )

    def _build_summary(
        self,
        *,
        total_messages: int,
        total_orders: int,
        total_invoices: int,
        total_revenue: Decimal,
        open_tasks: int,
    ) -> str:
        return (
            f"Processed {total_messages} customer messages, created {total_orders} orders, "
            f"generated {total_invoices} commercial documents, collected AED {Decimal(total_revenue):.2f} "
            f"in document value, and left {open_tasks} open tasks for follow-up."
        )
