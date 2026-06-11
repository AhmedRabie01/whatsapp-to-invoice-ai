from decimal import Decimal
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, get_db
from app.main import app
from app.models import Product


def build_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def seed_products(session) -> None:
    session.add_all(
        [
            Product(
                sku="MED-PANADOL",
                name="Panadol 500mg",
                category="pharmacy",
                unit_price=Decimal("12.50"),
                unit_type="box",
            ),
            Product(
                sku="MED-VITC",
                name="Vitamin C 1000mg",
                category="pharmacy",
                unit_price=Decimal("24.00"),
                unit_type="box",
            ),
            Product(
                sku="MNT-AC-DIAG",
                name="AC Diagnostic Visit",
                category="maintenance",
                unit_price=Decimal("180.00"),
                unit_type="service",
            ),
        ]
    )
    session.commit()


def test_order_workflow_endpoint_creates_draft_document() -> None:
    TestingSessionLocal = build_test_db()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    seed_session = TestingSessionLocal()
    seed_products(seed_session)
    seed_session.close()

    client = TestClient(app)
    response = client.post(
        "/orders/from-message",
        json={
            "message_text": "AC not working in Al Ain, need someone tomorrow.",
            "customer_name": "Ahmed Demo",
            "customer_phone": "+971500000999",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["extraction"]["intent"] == "maintenance_request"
    assert data["matched_items"][0]["sku"] == "MNT-AC-DIAG"
    assert data["pricing"]["total_amount"] == "180.00"
    assert data["document"]["document_type"] == "invoice"
    assert len(data["generated_tasks"]) >= 2
    assert data["generated_tasks"][0]["task_type"] in {
        "service_coordination",
        "customer_follow_up",
        "missing_contact",
        "manual_review",
    }
    titles = {task["title"] for task in data["generated_tasks"]}
    assert "Confirm technician availability" in titles
    assert "Ahmed Demo" in data["invoice_html"]
