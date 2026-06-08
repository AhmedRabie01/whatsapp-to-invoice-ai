from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InvoiceBase(BaseModel):
    order_id: int
    invoice_number: str
    document_type: str = "invoice"
    status: str = "draft"
    subtotal: Decimal = Decimal("0.00")
    delivery_fee: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")
    issue_date: datetime | None = None
    due_date: datetime | None = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
