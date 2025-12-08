# app/services/telematics/hyundai_kia.py
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.services.telematics.base import TelematicsProvider
from app.schemas.vehicle import VehicleStatusCreate
from app.core.config import settings


class MyBlueLinkProvider(TelematicsProvider):
    """
    Implémentation d'un fournisseur télématique basé sur la documentation MyBlueLink
    que tu as fournie (https://mybluelink.ca, endpoints /tods/api/...).

    On se concentre ici sur :
    - l'authentification
    - la récupération du statut temps réel du véhicule
    - la conversion en VehicleStatusCreate
    """

    BASE_URL = "https://mybluelink.ca/tods/api"

    def __init__(self, settings=settings) -> None:
        self.username = settings.MYBLUELINK_USERNAME
        self.password = settings.MYBLUELINK_PASSWORD
        self.pin = settings.MYBLUELINK_PIN
        self.session_token: Optional[str] = None
        self.client = httpx.Client(timeout=20.0)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def _auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.session_token}"} if self.session_token else {}

    def login(self) -> str:
        """
        POST /lgn
        Authentifie l'utilisateur et récupère un token.
        """
        url = f"{self.BASE_URL}/lgn"
        payload = {
            "username": self.username,
            "password": self.password,
        }

        r = self.client.post(url, json=payload)
        r.raise_for_status()

        data = r.json()
        self.session_token = data.get("token")
        return self.session_token

    def verify_token(self) -> bool:
        """
        POST /vrfyacctkn
        Valide un token de compte existant.
        """
        if not self.session_token:
            return False

        url = f"{self.BASE_URL}/vrfyacctkn"
        r = self.client.post(url, headers=self._auth_header())
        return r.status_code == 200

    def _ensure_session(self) -> None:
        """
        Garantit qu'on dispose d'un token valide.
        """
        if not self.session_token:
            self.login()
        elif not self.verify_token():
            self.login()

    # ------------------------------------------------------------------
    # Statut temps réel
    # ------------------------------------------------------------------
    def _realtime_status_raw(self, external_id: str) -> Dict[str, Any]:
        """
        GET /rltmvhclsts
        Statut temps réel du véhicule.
        """
        self._ensure_session()

        url = f"{self.BASE_URL}/rltmvhclsts"
        params = {"vehicle_id": external_id}

        r = self.client.get(url, headers=self._auth_header(), params=params)
        r.raise_for_status()
        return r.json()

    def _map_status_to_vehicle_status_create(self, data: Dict[str, Any]) -> VehicleStatusCreate:
        """
        Adapte ici la structure MyBlueLink -> VehicleStatusCreate.

        Exemple minimaliste :
        - on stocke tout le payload dans raw_payload
        - les champs spécifiques (battery_level, is_charging, etc.)
          sont à mapper selon TON schéma exact.
        """
        # TODO : adapte ces champs selon ton schéma réel.
        return VehicleStatusCreate(
            raw_payload=data  # Assure-toi que ce champ existe dans ton schema Pydantic
        )

    # ------------------------------------------------------------------
    # Implémentation de l'interface
    # ------------------------------------------------------------------
    def fetch_latest_status(self, vehicle_external_id: str) -> VehicleStatusCreate:
        """
        Implémentation de l'interface TelematicsProvider :
        récupère le statut temps réel et le convertit en VehicleStatusCreate.
        """
        raw = self._realtime_status_raw(vehicle_external_id)
        return self._map_status_to_vehicle_status_create(raw)
