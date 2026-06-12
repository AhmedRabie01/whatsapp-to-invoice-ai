from datetime import datetime
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
from app.models import Customer, Invoice, Message, Order, Task


def build_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def seed_report_data(session) -> None:
    customer = Customer(full_name="API Report Demo", phone="+971500000333")
    message = Message(
        customer=customer,
        content="AC not working in Al Ain, need someone tomorrow.",
        intent="maintenance_request",
        status="processed",
        confidence_score=0.92,
        created_at=datetime(2026, 6, 11, 9, 0, 0),
    )
    order = Order(
        customer=customer,
        source_message=message,
        order_type="order",
        subtotal=Decimal("180.00"),
        delivery_fee=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("180.00"),
        created_at=datetime(2026, 6, 11, 9, 5, 0),
    )
    invoice = Invoice(
        order=order,
        invoice_number="INV-20260611-0001",
        document_type="invoice",
        total_amount=Decimal("180.00"),
        subtotal=Decimal("180.00"),
        created_at=datetime(2026, 6, 11, 9, 6, 0),
    )
    task = Task(
        customer=customer,
        order=order,
        message=message,
        task_type="service_coordination",
        title="Confirm technician availability",
        priority="high",
        status="open",
    )
    session.add_all([customer, message, order, invoice, task])
    session.commit()


def test_generate_daily_report_endpoint_returns_aggregate() -> None:
    TestingSessionLocal = build_test_db()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    seed_session = TestingSessionLocal()
    seed_report_data(seed_session)
    seed_session.close()

    client = TestClient(app)
    response = client.post("/reports/generate", json={"report_date": "2026-06-11"})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["report"]["total_messages"] == 1
    assert data["report"]["total_orders"] == 1
    assert data["report"]["total_invoices"] == 1
    assert data["open_tasks"] == 1


def test_automation_daily_report_endpoint_logs_trigger() -> None:
    TestingSessionLocal = build_test_db()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    seed_session = TestingSessionLocal()
    seed_report_data(seed_session)
    seed_session.close()

    client = TestClient(app)
    response = client.post(
        "/automation/daily-report",
        headers={"x-webhook-secret": "change-this-secret"},
        json={
            "report_date": "2026-06-11",
            "send_email": False,
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["email_sent"] is False
    assert len(data["automation_logs"]) == 1
    assert data["automation_logs"][0]["target_system"] == "n8n"
