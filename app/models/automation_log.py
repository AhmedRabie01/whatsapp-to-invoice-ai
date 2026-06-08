from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class AutomationLog(Base):
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    daily_report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False)
    status = Column(String(50), default="queued", nullable=False)
    target_system = Column(String(100), nullable=True)
    payload = Column(Text, nullable=True)
    response_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    daily_report = relationship("DailyReport", back_populates="automation_logs")
