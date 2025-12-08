# app/db/models/vehicle_status.py
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class VehicleStatus(Base):
    __tablename__ = "vehicle_status"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Timestamp du statut (par défaut maintenant)
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Niveau de batterie en pourcentage (0–100)
    battery_level = Column(Integer, nullable=True)

    # Odomètre en km (si disponible dans BlueLink)
    odometer_km = Column(Float, nullable=True)

    # Champs de localisation BlueLink
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Statut de recharge
    is_charging = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    is_plugged = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Autonomie estimée en km
    total_range_km = Column(Float, nullable=True)

    # Temps restant pour la recharge (minutes)
    remaining_charge_minutes = Column(Integer, nullable=True)

    # Payload brut BlueLink (JSON complet de la réponse)
    raw_payload = Column(JSONB, nullable=True)

    # Relation inverse vers Vehicle
    vehicle = relationship(
        "Vehicle",
        back_populates="statuses",
        lazy="joined",
    )
