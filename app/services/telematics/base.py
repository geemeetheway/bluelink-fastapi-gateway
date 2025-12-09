# app/services/telematics/base.py
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.vehicle import VehicleStatusCreate


class TelematicsProvider(ABC):
    """
    Interface générique pour un fournisseur télématique (MyBlueLink, etc.).
    """

    @abstractmethod
    def fetch_latest_status(self, vehicle_external_id: str) -> VehicleStatusCreate:
        """
        Récupère le dernier statut connu d'un véhicule identifié par son external_id.
        Le résultat est normalisé dans un VehicleStatusCreate.
        """
        raise NotImplementedError
