# app/db/base.py
"""
Centralisation des modèles SQLAlchemy pour qu'Alembic puisse les détecter.
"""

from app.db.base_class import Base

# Imports "pour effets de bord" : ils enregistrent les modèles auprès de Base
from app.db.models.vehicle import Vehicle  # noqa: F401
from app.db.models.vehicle_status import VehicleStatus  # noqa: F401
