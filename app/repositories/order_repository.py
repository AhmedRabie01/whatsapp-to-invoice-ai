from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Order, OrderItem
from app.schemas.pricing import MatchedCatalogItem


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_order(
        self,
        *,
        customer_id: int,
        source_message_id: int | None,
        order_type: str,
        requested_date: datetime | None,
        subtotal: Decimal,
        delivery_fee: Decimal,
        tax_amount: Decimal,
        total_amount: Decimal,
        notes: str | None,
        matched_items: list[MatchedCatalogItem],
    ) -> Order:
        order = Order(
            customer_id=customer_id,
            source_message_id=source_message_id,
            order_type=order_type,
            requested_date=requested_date,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            total_amount=total_amount,
            notes=notes,
        )
        self.db.add(order)
        self.db.flush()

        for item in matched_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                item_name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
                notes=f"Matched from '{item.requested_name}' with score {item.match_score:.2f}",
            )
            self.db.add(order_item)

        self.db.flush()
        self.db.refresh(order)
        return order
