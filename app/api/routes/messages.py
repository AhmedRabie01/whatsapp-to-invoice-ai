from fastapi import APIRouter

from app.schemas.ai import MessageExtractionRequest, MessageExtractionResponse
from app.services.message_processing import MessageProcessingService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/extract", response_model=MessageExtractionResponse)
def extract_message(
    request: MessageExtractionRequest,
) -> MessageExtractionResponse:
    service = MessageProcessingService()
    return service.process_message(request)
