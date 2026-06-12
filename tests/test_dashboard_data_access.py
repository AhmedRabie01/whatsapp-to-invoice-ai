from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import AutomationLog, Customer, DailyReport, Invoice, Message, Order, OrderItem, Product, Task
from dashboard.data_access import DashboardDataAccess


def build_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_dashboard_data_access_returns_metrics_and_recent_rows() -> None:
    session = build_test_session()

    customer = Customer(full_name="Dashboard Demo", phone="+971500000111", location="Dubai")
    product = Product(
        sku="CLN-APT2",
        name="2 Bedroom Apartment Cleaning",
        category="cleaning",
        unit_price=Decimal("220.00"),
        unit_type="service",
    )
    message = Message(
        customer=customer,
        content="I need cleaning for a 2-bedroom apartment tomorrow in Dubai Marina.",
        intent="service_quote",
        status="processed",
        confidence_score=0.88,
    )
    order = Order(
        customer=customer,
        source_message=message,
        order_type="quotation",
        subtotal=Decimal("220.00"),
        delivery_fee=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("220.00"),
    )
    order_item = OrderItem(
        order=order,
        product=product,
        item_name="2 Bedroom Apartment Cleaning",
        quantity=1,
        unit_price=Decimal("220.00"),
        line_total=Decimal("220.00"),
    )
    invoice = Invoice(
        order=order,
        invoice_number="QUO-20260611-0001",
        document_type="quotation",
        total_amount=Decimal("220.00"),
        subtotal=Decimal("220.00"),
    )
    task = Task(
        customer=customer,
        order=order,
        message=message,
        task_type="quotation_follow_up",
        title="Follow up on quotation approval",
        priority="medium",
    )
    report = DailyReport(
        report_date=date(2026, 6, 11),
        total_messages=1,
        total_orders=1,
        total_invoices=1,
        total_revenue=Decimal("220.00"),
    )
    log = AutomationLog(
        daily_report=report,
        event_type="daily_report_dispatch",
        status="queued",
        target_system="n8n",
    )

    session.add_all([customer, product, message, order_item, invoice, task, report, log])
    session.commit()

    access = DashboardDataAccess(session)
    metrics = access.get_overview_metrics()
    messages = access.get_recent_messages()
    orders = access.get_recent_orders()
    documents = access.get_recent_documents()
    tasks = access.get_recent_tasks()
    products = access.get_products()
    reports = access.get_daily_reports()
    logs = access.get_automation_logs()

    assert metrics["total_messages"] == 1
    assert metrics["total_orders"] == 1
    assert metrics["total_documents"] == 1
    assert metrics["open_tasks"] == 1
    assert metrics["total_revenue"] == "220.00"
    assert messages[0]["intent"] == "service_quote"
    assert orders[0]["document_type"] == "quotation"
    assert documents[0]["invoice_number"] == "QUO-20260611-0001"
    assert tasks[0]["title"] == "Follow up on quotation approval"
    assert products[0]["sku"] == "CLN-APT2"
    assert reports[0]["total_revenue"] == "220.00"
    assert logs[0]["target_system"] == "n8n"
