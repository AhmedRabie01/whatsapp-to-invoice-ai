from app.ai.providers.base import AIProvider
from app.ai.providers.factory import get_ai_provider
from app.schemas.ai import MessageExtractionRequest, MessageExtractionResponse


class MessageProcessingService:
    def __init__(self, provider: AIProvider | None = None) -> None:
        self.provider = provider or get_ai_provider()

    def process_message(
        self, request: MessageExtractionRequest
    ) -> MessageExtractionResponse:
        return self.provider.extract_message_data(request)
