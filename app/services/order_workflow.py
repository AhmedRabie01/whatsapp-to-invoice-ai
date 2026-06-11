from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.ai import MessageExtractionRequest
from app.schemas.pricing import (
    CommercialWorkflowRequest,
    CommercialWorkflowResponse,
    DraftDocumentSummary,
    DraftOrderSummary,
)
from app.services.catalog_matching import CatalogMatchingService
from app.services.invoice_rendering import InvoiceRenderingService
from app.services.message_processing import MessageProcessingService
from app.services.pricing import PricingService


class OrderWorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.customer_repository = CustomerRepository(db)
        self.message_repository = MessageRepository(db)
        self.order_repository = OrderRepository(db)
        self.invoice_repository = InvoiceRepository(db)
        self.catalog_matching_service = CatalogMatchingService(db)
        self.pricing_service = PricingService()
        self.message_processing_service = MessageProcessingService()
        self.invoice_rendering_service = InvoiceRenderingService()

    def process_message_to_document(
        self,
        request: CommercialWorkflowRequest,
    ) -> CommercialWorkflowResponse:
        extraction = self.message_processing_service.process_message(
            MessageExtractionRequest(
                message_text=request.message_text,
                channel=request.channel,
                customer_id=request.customer_id,
            )
        )

        customer = self._resolve_customer(request, extraction.location)
        message = self.message_repository.create_processed_message(
            customer_id=customer.id,
            channel=request.channel,
            content=request.message_text,
            extraction=extraction,
        )

        matched_items, unmatched_items = self.catalog_matching_service.match_items(
            extraction.items_or_services
        )

        pricing = self.pricing_service.calculate(
            matched_items=matched_items,
            intent=extraction.intent,
            location=extraction.location,
        )

        order_type = "quotation" if self._resolve_document_type(request, extraction.intent) == "quotation" else "order"
        requested_date = self._resolve_requested_date(extraction.requested_date_text)

        order = self.order_repository.create_order(
            customer_id=customer.id,
            source_message_id=message.id,
            order_type=order_type,
            requested_date=requested_date,
            subtotal=pricing.subtotal,
            delivery_fee=pricing.delivery_fee,
            tax_amount=pricing.tax_amount,
            total_amount=pricing.total_amount,
            notes=extraction.customer_need,
            matched_items=matched_items,
        )

        document_type = self._resolve_document_type(request, extraction.intent)
        document = self.invoice_repository.create_invoice(
            order_id=order.id,
            document_type=document_type,
            subtotal=pricing.subtotal,
            delivery_fee=pricing.delivery_fee,
            tax_amount=pricing.tax_amount,
            total_amount=pricing.total_amount,
        )

        self.db.commit()
        self.db.refresh(order)
        self.db.refresh(document)

        invoice_html = self.invoice_rendering_service.render(
            customer=customer,
            order=order,
            invoice=document,
        )

        return CommercialWorkflowResponse(
            extraction=extraction,
            matched_items=matched_items,
            unmatched_items=unmatched_items,
            pricing=pricing,
            order=DraftOrderSummary(
                id=order.id,
                customer_id=order.customer_id,
                status=order.status,
                order_type=order.order_type,
                subtotal=order.subtotal,
                delivery_fee=order.delivery_fee,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                created_at=order.created_at,
            ),
            document=DraftDocumentSummary(
                id=document.id,
                invoice_number=document.invoice_number,
                document_type=document.document_type,
                status=document.status,
                total_amount=document.total_amount,
                issue_date=document.issue_date,
            ),
            invoice_html=invoice_html,
            suggested_customer_reply=self._build_customer_reply(
                customer_name=customer.full_name,
                document_type=document.document_type,
                total_amount=pricing.total_amount,
                unmatched_items=unmatched_items,
            ),
        )

    def _resolve_customer(self, request: CommercialWorkflowRequest, location: str | None):
        if request.customer_id is not None:
            customer = self.customer_repository.get_by_id(request.customer_id)
            if customer is None:
                raise ValueError(f"Customer with id {request.customer_id} was not found.")
            return customer

        if request.customer_phone:
            existing_customer = self.customer_repository.get_by_phone(request.customer_phone)
            if existing_customer is not None:
                return existing_customer

        return self.customer_repository.create(
            full_name=request.customer_name or "Walk-in Customer",
            phone=request.customer_phone,
            email=request.customer_email,
            location=location,
        )

    def _resolve_document_type(self, request: CommercialWorkflowRequest, intent: str) -> str:
        if request.document_type:
            if request.document_type not in {"invoice", "quotation"}:
                raise ValueError("document_type must be either 'invoice' or 'quotation'.")
            return request.document_type
        if intent == "service_quote":
            return "quotation"
        return "invoice"

    def _resolve_requested_date(self, requested_date_text: str | None) -> datetime | None:
        if requested_date_text == "today":
            return datetime.utcnow()
        if requested_date_text == "tomorrow":
            return (datetime.utcnow() + timedelta(days=1)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        return None

    def _build_customer_reply(
        self,
        *,
        customer_name: str,
        document_type: str,
        total_amount: Decimal,
        unmatched_items: list[str],
    ) -> str:
        document_label = "quotation" if document_type == "quotation" else "invoice"
        reply = (
            f"Hello {customer_name}, we prepared a draft {document_label} for AED {total_amount:.2f}. "
            "Please review and confirm if you would like us to proceed."
        )
        if unmatched_items:
            reply += f" We still need manual review for: {', '.join(unmatched_items)}."
        return reply
