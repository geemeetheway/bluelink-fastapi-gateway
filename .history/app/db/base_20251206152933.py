# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base commune pour tous les modèles SQLAlchemy.
    On n'importe PAS les modèles ici pour éviter les imports circulaires.
    """
    pass
