# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base commune pour tous les modèles SQLAlchemy.
    Alembic s'en servira pour générer automatiquement les migrations.
    """
    pass
