import csv
from decimal import Decimal
from pathlib import Path

from app.core.database import SessionLocal
from app.models import Product
from app.repositories.product_repository import ProductRepository


def seed_sample_products() -> None:
    db = SessionLocal()
    try:
        repository = ProductRepository(db)
        if repository.count() > 0:
            return

        sample_file = Path(__file__).resolve().parents[2] / "data" / "sample_products.csv"
        with sample_file.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                repository.add(
                    Product(
                        sku=row["sku"],
                        name=row["name"],
                        description=row["description"],
                        category=row["category"],
                        unit_price=Decimal(row["unit_price"]),
                        unit_type=row["unit_type"],
                        is_active=row["is_active"].lower() == "true",
                    )
                )

        db.commit()
    finally:
        db.close()
