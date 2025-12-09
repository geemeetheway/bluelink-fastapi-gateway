# app/schemas/vehicle_status.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VehicleStatusBase(BaseModel):
    """
    Modèle de base pour l'état d'un véhicule.

    Tous les champs "temps réel" (portes verrouillées, clim, etc.)
    sont optionnels pour éviter les erreurs de validation tant que
    la base de données ou l'intégration MyBlueLink ne fournit pas
    encore toutes les valeurs.
    """

    # Champ temporel principal : doit exister dans la DB
    timestamp_utc: datetime

    # Champs optionnels : s'ils n'existent pas ou sont NULL en DB,
    # la réponse API restera valide (ils seront simplement à null).
    odometer_km: Optional[float] = None
    battery_level_percent: Optional[float] = None
    battery_range_km: Optional[float] = None

    is_charging: Optional[bool] = None
    climate_on: Optional[bool] = None

    # 🔹 Champ qui causait l'erreur : rendu optionnel
    doors_locked: bool | None = None

    # Tu pourras ajouter d'autres champs ici plus tard au besoin,
    # toujours en les mettant optionnels tant que tout n'est pas câblé.


class VehicleStatusCreate(VehicleStatusBase):
    """
    Modèle utilisé lors de la création d'un nouvel état de véhicule.
    """

    vehicle_id: int


class VehicleStatusRead(VehicleStatusBase):
    """
    Modèle utilisé comme response_model dans les endpoints FastAPI.

    - `id` et `vehicle_id` sont requis car ils doivent exister en DB.
    - `from_attributes=True` permet de construire ce modèle directement
      à partir d'un objet SQLAlchemy (VehicleStatus) sans dict intermédiaire.
    """

    id: int
    vehicle_id: int

    model_config = ConfigDict(from_attributes=True)
