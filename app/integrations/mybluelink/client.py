# app/integrations/mybluelink/client.py

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx


class MyBlueLinkError(Exception):
    """Erreur générique pour le client MyBlueLink."""


class MyBlueLinkClient:
    """
    Client très simplifié pour l’API MyBlueLink.

    Il illustre le flux suivant :
    - login (POST /tods/api/lgn)
    - appel d’un endpoint de statut en temps réel (GET /tods/api/rltmvhclsts)
    """

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        pin: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url or os.getenv("MYBLUELINK_BASE_URL", "https://mybluelink.ca")
        self.username = username or os.getenv("MYBLUELINK_USERNAME", "")
        self.password = password or os.getenv("MYBLUELINK_PASSWORD", "")
        self.pin = pin or os.getenv("MYBLUELINK_PIN", "")
        self.timeout = timeout

        self._access_token: Optional[str] = None
        self._account_token: Optional[str] = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def login(self) -> None:
        """
        Appelle POST /tods/api/lgn pour obtenir un token de session.

        À adapter en fonction du format réel renvoyé par MyBlueLink.
        """
        payload = {
            "username": self.username,
            "password": self.password,
        }

        url = f"{self.base_url}/tods/api/lgn"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers=self._get_headers())
            if resp.status_code != 200:
                raise MyBlueLinkError(
                    f"Login failed ({resp.status_code}): {resp.text}"
                )

            data: Dict[str, Any] = resp.json()
            # Exemple : adapter à la structure réelle.
            # Imaginons que data["accessToken"] contienne le token :
            self._access_token = data.get("accessToken")
            self._account_token = data.get("accountToken")

            if not self._access_token:
                raise MyBlueLinkError("No access token found in login response.")

    def ensure_logged_in(self) -> None:
        """
        Login paresseux : ne fait un login que si pas déjà connecté.
        """
        if not self._access_token:
            self.login()

    def get_realtime_status(self, vin: str) -> Dict[str, Any]:
        """
        Appelle GET /tods/api/rltmvhclsts pour obtenir le statut temps réel du véhicule.

        À adapter à la réalité :
        - parfois, l’API BlueLink attend un body JSON même pour des "GET"
          ou utilise "POST" pour ce type d’opérations.
        - Le nom du paramètre (VIN, vehicleId, etc.) doit être aligné
          sur le comportement réel de l’API.
        """
        self.ensure_logged_in()

        url = f"{self.base_url}/tods/api/rltmvhclsts"

        # Exemple générique. À ajuster selon ce que l’API attend exactement.
        params_or_body = {
            "vin": vin,
        }

        with httpx.Client(timeout=self.timeout) as client:
            # Si en réalité c’est un POST, remplace par client.post(...)
            resp = client.get(url, params=params_or_body, headers=self._get_headers())
            if resp.status_code != 200:
                raise MyBlueLinkError(
                    f"get_realtime_status failed ({resp.status_code}): {resp.text}"
                )

            return resp.json()
