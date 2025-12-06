# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import des modèles pour qu'Alembic les voie
# (même si on ne les utilise pas directement ici)
from app.db.models.vehicle import Vehicle  # noqa: F401
from app.db.models.vehicle_status import VehicleStatus  # noqa: F401
