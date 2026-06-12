from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DailyReportBase(BaseModel):
    report_date: date
    total_messages: int = 0
    total_orders: int = 0
    total_invoices: int = 0
    total_revenue: Decimal = Decimal("0.00")
    summary: str | None = None
    sent_via: str | None = None
    sent_at: datetime | None = None


class DailyReportCreate(DailyReportBase):
    pass


class DailyReportRead(DailyReportBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AutomationLogBase(BaseModel):
    daily_report_id: int | None = None
    event_type: str
    status: str = "queued"
    target_system: str | None = None
    payload: str | None = None
    response_message: str | None = None


class AutomationLogCreate(AutomationLogBase):
    pass


class AutomationLogRead(AutomationLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyReportRequest(BaseModel):
    report_date: date | None = None


class DailyReportResponse(BaseModel):
    report: DailyReportRead
    open_tasks: int


class SendDailyReportRequest(BaseModel):
    report_date: date | None = None
    recipient_email: str


class SendDailyReportResponse(BaseModel):
    report: DailyReportRead
    open_tasks: int
    recipient_email: str
    email_sent: bool
    automation_log: AutomationLogRead


class AutomationDailyReportRequest(BaseModel):
    report_date: date | None = None
    recipient_email: str | None = None
    send_email: bool = True


class AutomationDailyReportResponse(BaseModel):
    report: DailyReportRead
    open_tasks: int
    email_sent: bool
    automation_logs: list[AutomationLogRead] = Field(default_factory=list)
