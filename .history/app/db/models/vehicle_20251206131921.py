# app/db/models/vehicle.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    vin = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    statuses = relationship(
        "VehicleStatus",
        back_populates="vehicle",
        cascade="all, delete-orphan",
    )
