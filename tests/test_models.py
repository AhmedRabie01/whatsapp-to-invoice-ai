from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import AutomationLog, Customer, DailyReport, Invoice, Message, Order, OrderItem, Product, Task


def build_test_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_core_models_can_store_business_workflow_data() -> None:
    session = build_test_session()

    customer = Customer(
        full_name="Fatima Noor",
        phone="+971500000001",
        location="Al Ain",
    )
    message = Message(
        customer=customer,
        content="Need 2 Panadol boxes tomorrow in Al Ain.",
        raw_language="en",
        intent="product_order",
        confidence_score=0.92,
    )
    product = Product(
        sku="MED-PANADOL",
        name="Panadol 500mg",
        category="pharmacy",
        unit_price=Decimal("12.50"),
        unit_type="box",
    )
    order = Order(
        customer=customer,
        source_message=message,
        order_type="order",
        subtotal=Decimal("25.00"),
        delivery_fee=Decimal("10.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("35.00"),
    )
    order_item = OrderItem(
        order=order,
        product=product,
        item_name="Panadol 500mg",
        quantity=2,
        unit_price=Decimal("12.50"),
        line_total=Decimal("25.00"),
    )
    invoice = Invoice(
        order=order,
        invoice_number="INV-0001",
        document_type="invoice",
        subtotal=Decimal("25.00"),
        delivery_fee=Decimal("10.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("35.00"),
    )
    task = Task(
        customer=customer,
        order=order,
        message=message,
        task_type="follow_up",
        title="Confirm delivery time",
        priority="high",
    )
    report = DailyReport(
        report_date=date(2026, 6, 7),
        total_messages=1,
        total_orders=1,
        total_invoices=1,
        total_revenue=Decimal("35.00"),
        summary="One pharmacy order processed.",
        sent_via="email",
    )
    automation_log = AutomationLog(
        daily_report=report,
        event_type="daily_report_dispatch",
        status="queued",
        target_system="n8n",
    )

    session.add_all([customer, product, order_item, invoice, task, report, automation_log])
    session.commit()
    session.refresh(order)
    session.refresh(report)

    saved_order = session.query(Order).filter_by(id=order.id).one()
    saved_report = session.query(DailyReport).filter_by(id=report.id).one()

    assert saved_order.customer.full_name == "Fatima Noor"
    assert saved_order.source_message.content.startswith("Need 2 Panadol")
    assert saved_order.items[0].product.sku == "MED-PANADOL"
    assert saved_order.items[0].quantity == 2
    assert saved_order.invoice.invoice_number == "INV-0001"
    assert saved_order.tasks[0].title == "Confirm delivery time"
    assert saved_report.automation_logs[0].target_system == "n8n"
    assert saved_report.total_revenue == Decimal("35.00")
