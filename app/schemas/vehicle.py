# app/schemas/vehicle.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# -----------------
# Schémas Véhicule
# -----------------

class VehicleBase(BaseModel):
    """
    Base commune pour les véhicules (création / lecture).

    On garde `name` mais on le rend optionnel pour rester compatible avec
    les anciens enregistrements / anciens modèles, même si la colonne
    SQLAlchemy a changé ou si la valeur est NULL.
    """
    external_id: Optional[str] = Field(
        None,
        description="Identifiant externe (MyBlueLink, etc.).",
    )
    name: Optional[str] = Field(
        None,
        description="Nom convivial du véhicule (optionnel).",
    )
    vin: Optional[str] = Field(
        None,
        description="Numéro de série du véhicule (VIN).",
        min_length=1,
        max_length=64,
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

    # Pydantic v2 : remplace l'ancien `class Config: orm_mode = True`
    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Schémas Statut Véhicule
# -------------------------

class VehicleStatusRead(BaseModel):
    id: int
    vehicle_id: int
    timestamp: datetime
    battery_level: Optional[float] = None
    doors_locked: bool | None = None
    odometer_km: Optional[float] = None

    # Pydantic v2 : idem, permet la conversion depuis un objet SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class VehicleStatusCreate(BaseModel):
    battery_level: Optional[float] = Field(
        None,
        description="Niveau de batterie en pourcentage.",
    )
    doors_locked: bool = Field(
        True,
        description="True si les portes sont verrouillées.",
    )
    odometer_km: Optional[float] = Field(
        None,
        description="Odomètre en kilomètres.",
    )
