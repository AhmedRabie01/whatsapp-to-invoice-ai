from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import Product
from app.schemas.ai import ExtractedItem
from app.services.catalog_matching import CatalogMatchingService


def build_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def seed_products(session) -> None:
    session.add_all(
        [
            Product(
                sku="MED-PANADOL",
                name="Panadol 500mg",
                category="pharmacy",
                unit_price=Decimal("12.50"),
                unit_type="box",
            ),
            Product(
                sku="CLN-APT2",
                name="2 Bedroom Apartment Cleaning",
                category="cleaning",
                unit_price=Decimal("220.00"),
                unit_type="service",
            ),
        ]
    )
    session.commit()


def test_catalog_matching_matches_extracted_items_to_products() -> None:
    session = build_test_session()
    seed_products(session)
    service = CatalogMatchingService(session)

    matched_items, unmatched_items = service.match_items(
        [
            ExtractedItem(name="Panadol 500mg", quantity=2, item_type="product"),
            ExtractedItem(name="2-bedroom apartment cleaning", quantity=1, item_type="service"),
        ]
    )

    assert len(matched_items) == 2
    assert matched_items[0].sku == "MED-PANADOL"
    assert matched_items[1].sku == "CLN-APT2"
    assert unmatched_items == []
