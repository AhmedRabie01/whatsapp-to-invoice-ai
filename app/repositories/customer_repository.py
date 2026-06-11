from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_by_phone(self, phone: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.phone == phone).first()

    def create(
        self,
        *,
        full_name: str,
        phone: str | None = None,
        email: str | None = None,
        location: str | None = None,
    ) -> Customer:
        customer = Customer(
            full_name=full_name,
            phone=phone,
            email=email,
            location=location,
        )
        self.db.add(customer)
        self.db.flush()
        return customer
