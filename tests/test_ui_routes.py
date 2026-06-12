from decimal import Decimal
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, get_db
from app.main import app
from app.models import Customer, Product


def build_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def seed_ui_data(session) -> None:
    customer = Customer(full_name="UI Demo", phone="+971500000555", location="Dubai")
    product = Product(
        sku="MED-PANADOL",
        name="Panadol 500mg",
        category="pharmacy",
        unit_price=Decimal("12.50"),
        unit_type="box",
    )
    session.add_all([customer, product])
    session.commit()


def test_ui_routes_serve_html_and_data() -> None:
    TestingSessionLocal = build_test_db()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    seed_session = TestingSessionLocal()
    seed_ui_data(seed_session)
    seed_session.close()

    client = TestClient(app)

    html_response = client.get("/ui")
    data_response = client.get("/ui/data")

    app.dependency_overrides.clear()

    assert html_response.status_code == 200
    assert "SME Workflow Console" in html_response.text
    assert data_response.status_code == 200
    payload = data_response.json()
    assert "metrics" in payload
    assert "products" in payload
    assert payload["products"][0]["sku"] == "MED-PANADOL"
