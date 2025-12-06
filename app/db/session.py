# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Pour SQLite, on a besoin de ce paramètre pour le multithreading de SQLAlchemy
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,  # tu peux passer à True pour voir les requêtes SQL en dev
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def get_db():
    """
    Dépendance FastAPI qui fournit une session DB
    et s'assure qu'elle est fermée après usage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
