from app.ai.providers.base import AIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "mock":
        return MockAIProvider()

    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
