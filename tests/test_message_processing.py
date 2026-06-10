from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.providers.mock_provider import MockAIProvider
from app.main import app
from app.schemas.ai import MessageExtractionRequest
from app.services.message_processing import MessageProcessingService

client = TestClient(app)


def test_mock_provider_extracts_product_order_details() -> None:
    provider = MockAIProvider()
    request = MessageExtractionRequest(
        message_text="محتاج 2 بانادول وعلبة فيتامين سي والتوصيل للعين بكرة"
    )

    result = provider.extract_message_data(request)

    assert result.intent == "product_order"
    assert result.location == "Al Ain"
    assert result.requested_date_text == "tomorrow"
    assert len(result.items_or_services) == 2
    assert result.items_or_services[0].quantity == 2
    assert result.confidence_score >= 0.85


def test_service_flags_missing_information_for_cleaning_quote() -> None:
    service = MessageProcessingService(provider=MockAIProvider())
    request = MessageExtractionRequest(
        message_text="I need cleaning for a 2-bedroom apartment. How much?"
    )

    result = service.process_message(request)

    assert result.intent == "service_quote"
    assert result.items_or_services[0].name == "2-bedroom apartment cleaning"
    assert "service location" in result.missing_information
    assert "service date" in result.missing_information
    assert result.suggested_next_action.startswith("Ask the customer to confirm:")


def test_message_extract_endpoint_returns_structured_response() -> None:
    response = client.post(
        "/messages/extract",
        json={
            "message_text": "AC not working in Al Ain, need someone tomorrow.",
            "channel": "whatsapp",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "maintenance_request"
    assert data["location"] == "Al Ain"
    assert data["requested_date_text"] == "tomorrow"
    assert data["items_or_services"][0]["name"] == "AC diagnostic visit"
    assert data["suggested_next_action"] == "Create a maintenance task and confirm technician availability."
