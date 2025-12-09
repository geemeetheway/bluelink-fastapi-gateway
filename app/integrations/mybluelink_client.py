# app/integrations/mybluelink_client.py

from __future__ import annotations

from typing import Any, Dict, List
from app.core.config import settings
import httpx


class MyBlueLinkClient:
    """
    Client très simple pour parler à MyBlueLink.

    Toute la configuration provient de `app.core.config.settings`,
    elle-même alimentée par le fichier .env.
    """

    def __init__(self) -> None:
        # Base URL provenant exclusivement de settings
        self.base_url = (settings.BLUELINK_BASE_URL or "").rstrip("/")
        self.api_key = settings.BLUELINK_API_KEY or ""

        if not self.base_url:
            raise RuntimeError(
                "BLUELINK_BASE_URL (MYBLUELINK_BASE_URL dans .env) n’est pas configurée."
            )

    def _headers(self) -> Dict[str, str]:
        """
        Headers communs pour appeler l'API MyBlueLink.
        """
        headers = {
            "Accept": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def list_vehicles(self) -> List[Dict[str, Any]]:
        """
        Appelle l'endpoint équivalent à exampleData/listVehicles.json.
        """
        url = f"{self.base_url}/vehicles"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()

            try:
                data = resp.json()
            except ValueError:
                raise RuntimeError(
                    f"Réponse non-JSON reçue depuis MyBlueLink: {resp.text[:200]}"
                )

        # Les véhicules sont dans data.result.vehicles selon tes exemples
        return data.get("result", {}).get("vehicles", [])

    async def get_vehicle_status_by_vin(self, vin: str) -> Dict[str, Any]:
        """
        Appelle l'endpoint équivalent à exampleData/vehicleStatus.json.
        """
        url = f"{self.base_url}/vehicles/{vin}/status"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()

            try:
                data = resp.json()
            except ValueError:
                raise RuntimeError(
                    f"Réponse non-JSON reçue depuis MyBlueLink: {resp.text[:200]}"
                )

        return data  # Le mapping sera fait ailleurs
