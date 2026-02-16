# app/db/models/vehicle.py
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    # Identifiant externe (par ex. id BlueLink, ou id télémétrie)
    external_id = Column(String, index=True, nullable=True, unique=True)

    # VIN du véhicule (facultatif, mais généralement unique)
    vin = Column(String(32), nullable=True, unique=True, index=True)

    # Nom ou surnom donné au véhicule (ex.: "Ioniq 5 familiale")
    nickname = Column(String, nullable=True)

    # Indique si le véhicule est actif dans le système
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Date de création de l’enregistrement
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Relation avec les statuts télémétriques
    # back_populates doit correspondre au "vehicle" défini dans VehicleStatus
    statuses = relationship(
        "VehicleStatus",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
