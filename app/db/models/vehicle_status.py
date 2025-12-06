# app/db/models/vehicle_status.py
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class VehicleStatus(Base):
    __tablename__ = "vehicle_status"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    battery_level = Column(Float, nullable=True)
    doors_locked = Column(Boolean, default=True)
    odometer_km = Column(Float, nullable=True)

    vehicle = relationship("Vehicle", back_populates="statuses")
