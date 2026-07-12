"""Database setup with SQLAlchemy + SQLite."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import DB_PATH

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    """Create all tables."""
    import backend.models  # noqa: F401 — register models
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a DB session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
