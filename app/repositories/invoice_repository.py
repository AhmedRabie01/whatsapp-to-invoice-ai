from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Invoice


class InvoiceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_document_number(self, document_type: str) -> str:
        prefix = "QUO" if document_type == "quotation" else "INV"
        today = datetime.utcnow().strftime("%Y%m%d")
        existing_count = (
            self.db.query(Invoice)
            .filter(Invoice.invoice_number.like(f"{prefix}-{today}-%"))
            .count()
        )
        return f"{prefix}-{today}-{existing_count + 1:04d}"

    def create_invoice(
        self,
        *,
        order_id: int,
        document_type: str,
        subtotal: Decimal,
        delivery_fee: Decimal,
        tax_amount: Decimal,
        total_amount: Decimal,
    ) -> Invoice:
        invoice = Invoice(
            order_id=order_id,
            invoice_number=self.generate_document_number(document_type),
            document_type=document_type,
            status="draft",
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            total_amount=total_amount,
        )
        self.db.add(invoice)
        self.db.flush()
        self.db.refresh(invoice)
        return invoice
