from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    channel = Column(String(50), default="whatsapp", nullable=False)
    direction = Column(String(50), default="incoming", nullable=False)
    content = Column(Text, nullable=False)
    raw_language = Column(String(50), nullable=True)
    intent = Column(String(100), nullable=True)
    structured_data = Column(Text, nullable=True)
    status = Column(String(50), default="received", nullable=False)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="messages")
