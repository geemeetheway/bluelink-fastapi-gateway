# app/schemas/vehicle.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# -----------------
# Schémas Véhicule
# -----------------

class VehicleBase(BaseModel):
    external_id: str = Field(
        ...,
        description="Identifiant externe du véhicule (ex: ID Bluelink).",
    )
    name: str = Field(
        ...,
        description="Nom lisible du véhicule (ex: 'Ioniq 5 Blanche').",
    )
    vin: str = Field(
        ...,
        description="Numéro VIN du véhicule.",
    )


class VehicleCreate(VehicleBase):
    """
    Schéma utilisé à la création d'un véhicule.
    Pour l'instant identique à VehicleBase, mais prêt pour évoluer.
    """
    pass


class VehicleRead(VehicleBase):
    """
    Schéma renvoyé lorsqu'on lit un véhicule.
    """
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# -------------------------
# Schémas Statut Véhicule
# -------------------------

class VehicleStatusRead(BaseModel):
    id: int
    vehicle_id: int
    timestamp: datetime
    battery_level: Optional[float] = None
    doors_locked: bool
    odometer_km: Optional[float] = None

    class Config:
        orm_mode = True
