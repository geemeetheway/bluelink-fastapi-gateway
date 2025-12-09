# app/integrations/mybluelink_client.py

from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx
import os


class MyBlueLinkClient:
    """
    Client très simple pour parler à MyBlueLink.

    On suppose que tu as ces variables dans ton .env :
    - MYBLUELINK_BASE_URL
    - MYBLUELINK_API_KEY ou token d'accès
    """

    def __init__(self) -> None:
        self.base_url = os.getenv("MYBLUELINK_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("MYBLUELINK_API_KEY", "")
        if not self.base_url:
            raise RuntimeError("MYBLUELINK_BASE_URL is not configured")

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def list_vehicles(self) -> List[Dict[str, Any]]:
        """
        Appelle l'endpoint équivalent à ton exampleData/listVehicles.json.
        """
        url = f"{self.base_url}/vehicles"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()

        # D’après ton JSON, les véhicules sont dans result.vehicles
        vehicles = data.get("result", {}).get("vehicles", [])
        return vehicles

    async def get_vehicle_status_by_vin(self, vin: str) -> Dict[str, Any]:
        """
        Appelle l'endpoint équivalent à ton exampleData/vehicleStatus.json
        pour un VIN donné.
        """
        url = f"{self.base_url}/vehicles/{vin}/status"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()

        # On renvoie tel quel, on fera le mapping ailleurs.
        return data
