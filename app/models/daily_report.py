from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False, unique=True, index=True)
    total_messages = Column(Integer, default=0, nullable=False)
    total_orders = Column(Integer, default=0, nullable=False)
    total_invoices = Column(Integer, default=0, nullable=False)
    total_revenue = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    summary = Column(Text, nullable=True)
    sent_via = Column(String(50), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    automation_logs = relationship("AutomationLog", back_populates="daily_report")
