from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import Customer
from app.repositories.task_repository import TaskRepository
from app.schemas.ai import ExtractedItem, MessageExtractionResponse
from app.schemas.pricing import MatchedCatalogItem
from app.services.task_generation import TaskGenerationService


def build_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_task_generation_creates_common_and_cleaning_tasks() -> None:
    session = build_test_session()
    customer = Customer(full_name="Demo Customer", location="Dubai")
    session.add(customer)
    session.commit()
    session.refresh(customer)

    service = TaskGenerationService(TaskRepository(session))
    extraction = MessageExtractionResponse(
        provider_name="mock",
        original_message="I need cleaning for a 2-bedroom apartment. How much?",
        intent="service_quote",
        customer_need="Customer wants a cleaning quotation.",
        items_or_services=[
            ExtractedItem(
                name="2-bedroom apartment cleaning",
                quantity=1,
                item_type="service",
            )
        ],
        location=None,
        requested_date_text=None,
        missing_information=["service location", "service date"],
        confidence_score=0.78,
        suggested_next_action="Ask the customer to confirm: service location, service date.",
    )
    matched_items = [
        MatchedCatalogItem(
            product_id=1,
            sku="CLN-APT2",
            name="2 Bedroom Apartment Cleaning",
            requested_name="2-bedroom apartment cleaning",
            category="cleaning",
            quantity=1,
            unit_type="service",
            unit_price=Decimal("220.00"),
            line_total=Decimal("220.00"),
            match_score=0.95,
        )
    ]

    tasks = service.generate_tasks(
        customer=customer,
        order_id=11,
        message_id=12,
        extraction=extraction,
        matched_items=matched_items,
        unmatched_items=[],
        document_type="quotation",
        has_customer_phone=False,
    )

    titles = {task.title for task in tasks}

    assert "Collect customer phone number" in titles
    assert "Follow up on quotation approval" in titles
    assert "Send customer follow-up reply" in titles
    assert "Collect service location" in titles
    assert "Collect service date" in titles
