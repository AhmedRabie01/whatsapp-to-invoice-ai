from decimal import Decimal

from app.schemas.pricing import MatchedCatalogItem, PricingBreakdown


class PricingService:
    def calculate(
        self,
        *,
        matched_items: list[MatchedCatalogItem],
        intent: str,
        location: str | None,
    ) -> PricingBreakdown:
        subtotal = sum((item.line_total for item in matched_items), Decimal("0.00"))
        delivery_fee = self._delivery_fee(intent=intent, location=location, subtotal=subtotal)
        tax_amount = Decimal("0.00")
        total_amount = subtotal + delivery_fee + tax_amount

        return PricingBreakdown(
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            total_amount=total_amount,
        )

    def _delivery_fee(
        self,
        *,
        intent: str,
        location: str | None,
        subtotal: Decimal,
    ) -> Decimal:
        if intent == "product_order" and subtotal > Decimal("0.00"):
            return Decimal("15.00") if location else Decimal("10.00")
        return Decimal("0.00")
