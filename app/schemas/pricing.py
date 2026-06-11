from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ai import MessageExtractionResponse
from app.schemas.task import TaskRead


class CommercialWorkflowRequest(BaseModel):
    message_text: str = Field(min_length=1)
    channel: str = "whatsapp"
    customer_id: int | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    document_type: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class MatchedCatalogItem(BaseModel):
    product_id: int
    sku: str
    name: str
    requested_name: str
    category: str | None = None
    quantity: int
    unit_type: str
    unit_price: Decimal
    line_total: Decimal
    match_score: float


class PricingBreakdown(BaseModel):
    currency: str = "AED"
    subtotal: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    total_amount: Decimal


class DraftOrderSummary(BaseModel):
    id: int
    customer_id: int
    status: str
    order_type: str
    subtotal: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime


class DraftDocumentSummary(BaseModel):
    id: int
    invoice_number: str
    document_type: str
    status: str
    total_amount: Decimal
    issue_date: datetime


class CommercialWorkflowResponse(BaseModel):
    extraction: MessageExtractionResponse
    matched_items: list[MatchedCatalogItem] = Field(default_factory=list)
    unmatched_items: list[str] = Field(default_factory=list)
    pricing: PricingBreakdown
    order: DraftOrderSummary
    document: DraftDocumentSummary
    generated_tasks: list[TaskRead] = Field(default_factory=list)
    invoice_html: str
    suggested_customer_reply: str
