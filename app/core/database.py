from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    import app.models  # noqa: F401
    from app.services.catalog_seed import seed_sample_products

    Base.metadata.create_all(bind=engine)
    seed_sample_products()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
