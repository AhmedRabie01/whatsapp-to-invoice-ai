from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.pricing import MatchedCatalogItem
from app.services.pricing import PricingService


def test_pricing_adds_delivery_fee_for_product_orders() -> None:
    service = PricingService()
    matched_items = [
        MatchedCatalogItem(
            product_id=1,
            sku="MED-PANADOL",
            name="Panadol 500mg",
            requested_name="Panadol 500mg",
            category="pharmacy",
            quantity=2,
            unit_type="box",
            unit_price=Decimal("12.50"),
            line_total=Decimal("25.00"),
            match_score=0.95,
        )
    ]

    pricing = service.calculate(
        matched_items=matched_items,
        intent="product_order",
        location="Al Ain",
    )

    assert pricing.subtotal == Decimal("25.00")
    assert pricing.delivery_fee == Decimal("15.00")
    assert pricing.tax_amount == Decimal("0.00")
    assert pricing.total_amount == Decimal("40.00")
