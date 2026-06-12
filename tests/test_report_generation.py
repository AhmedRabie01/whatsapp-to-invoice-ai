from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import Customer, Invoice, Message, Order, Task
from app.repositories.report_repository import ReportRepository
from app.services.report_generation import ReportGenerationService


def build_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_report_generation_creates_daily_summary() -> None:
    session = build_test_session()
    report_date = date(2026, 6, 11)

    customer = Customer(full_name="Report Demo", phone="+971500000222")
    message = Message(
        customer=customer,
        content="Need cleaning tomorrow in Dubai Marina.",
        intent="service_quote",
        status="processed",
        confidence_score=0.88,
        created_at=datetime(2026, 6, 11, 10, 0, 0),
    )
    order = Order(
        customer=customer,
        source_message=message,
        order_type="quotation",
        subtotal=Decimal("220.00"),
        delivery_fee=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("220.00"),
        created_at=datetime(2026, 6, 11, 10, 10, 0),
    )
    invoice = Invoice(
        order=order,
        invoice_number="QUO-20260611-0001",
        document_type="quotation",
        total_amount=Decimal("220.00"),
        subtotal=Decimal("220.00"),
        created_at=datetime(2026, 6, 11, 10, 11, 0),
    )
    task = Task(
        customer=customer,
        order=order,
        message=message,
        task_type="quotation_follow_up",
        title="Follow up on quotation approval",
        priority="medium",
        status="open",
    )

    session.add_all([customer, message, order, invoice, task])
    session.commit()

    service = ReportGenerationService(ReportRepository(session))
    report, open_tasks = service.generate_daily_report(report_date)

    assert report.report_date == report_date
    assert report.total_messages == 1
    assert report.total_orders == 1
    assert report.total_invoices == 1
    assert report.total_revenue == Decimal("220.00")
    assert open_tasks == 1
    assert "Processed 1 customer messages" in report.summary
