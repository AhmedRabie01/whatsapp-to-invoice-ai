from sqlalchemy.orm import Session

from app.models import Message
from app.schemas.ai import MessageExtractionResponse


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_processed_message(
        self,
        *,
        customer_id: int | None,
        channel: str,
        content: str,
        extraction: MessageExtractionResponse,
    ) -> Message:
        message = Message(
            customer_id=customer_id,
            channel=channel,
            direction="incoming",
            content=content,
            raw_language=None,
            intent=extraction.intent,
            structured_data=extraction.model_dump_json(),
            status="processed",
            confidence_score=extraction.confidence_score,
        )
        self.db.add(message)
        self.db.flush()
        return message
