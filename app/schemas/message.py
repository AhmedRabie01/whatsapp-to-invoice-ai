from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    customer_id: int | None = None
    channel: str = "whatsapp"
    direction: str = "incoming"
    content: str
    raw_language: str | None = None
    intent: str | None = None
    structured_data: str | None = None
    status: str = "received"
    confidence_score: float | None = None


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
