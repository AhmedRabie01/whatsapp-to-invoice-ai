from abc import ABC, abstractmethod

from app.schemas.ai import MessageExtractionRequest, MessageExtractionResponse


class AIProvider(ABC):
    provider_name: str

    @abstractmethod
    def extract_message_data(
        self, request: MessageExtractionRequest
    ) -> MessageExtractionResponse:
        raise NotImplementedError
