from sqlalchemy.orm import Session

from app.models import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self) -> list[Product]:
        return (
            self.db.query(Product)
            .filter(Product.is_active.is_(True))
            .order_by(Product.name.asc())
            .all()
        )

    def count(self) -> int:
        return self.db.query(Product).count()

    def add(self, product: Product) -> Product:
        self.db.add(product)
        return product
