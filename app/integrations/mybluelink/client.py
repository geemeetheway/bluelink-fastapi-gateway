# app/integrations/mybluelink/client.py

from __future__ import annotations

import os
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any, Dict, Optional

import requests


# ---------------------------------------------------------------------------
# Exceptions spécifiques à l'intégration MyBlueLink
# ---------------------------------------------------------------------------


class MyBlueLinkError(Exception):
    """
    Erreur fonctionnelle liée à MyBlueLink (auth, JSON invalide, etc.).
    Cette exception peut être interceptée dans les routes pour retourner
    une réponse HTTP 4xx / 5xx propre au frontend.
    """


# ---------------------------------------------------------------------------
# Configuration simplifiée du client
# ---------------------------------------------------------------------------


@dataclass
class MyBlueLinkConfig:
    """
    Configuration du client MyBlueLink.
    Les valeurs réelles peuvent être injectées via les variables
    d'environnement dans le docker-compose (.env).
    """

    username: str
    password: str
    pin: Optional[str] = None
    base_url: Optional[str] = None
    demo_mode: bool = True  # En mode DEMO, on ne fait pas d'appel HTTP réel.

    @classmethod
    def from_env(cls) -> "MyBlueLinkConfig":
        """
        Construit la configuration à partir des variables d'environnement.

        Variables possibles :
        - BLUELINK_USERNAME
        - BLUELINK_PASSWORD
        - BLUELINK_PIN
        - BLUELINK_BASE_URL
        - BLUELINK_DEMO_MODE (true/false)
        """
        username = os.getenv("BLUELINK_USERNAME", "").strip()
        password = os.getenv("BLUELINK_PASSWORD", "").strip()
        pin = os.getenv("BLUELINK_PIN", "").strip() or None
        base_url = os.getenv("BLUELINK_BASE_URL", "").strip() or None
        demo_raw = os.getenv("BLUELINK_DEMO_MODE", "true").strip().lower()

        demo_mode = demo_raw in ("1", "true", "yes", "y", "on")

        if not username or not password:
            # En mode DEMO, on autorise l’absence de credentials.
            # En mode réel, on lève une erreur explicite.
            if not demo_mode:
                raise MyBlueLinkError(
                    "BLUELINK_USERNAME et BLUELINK_PASSWORD doivent être "
                    "définis dans l'environnement pour utiliser MyBlueLink en mode réel."
                )

        return cls(
            username=username,
            password=password,
            pin=pin,
            base_url=base_url,
            demo_mode=demo_mode,
        )


# ---------------------------------------------------------------------------
# Client MyBlueLink
# ---------------------------------------------------------------------------


class MyBlueLinkClient:
    """
    Client minimaliste pour l'API (officieuse) MyBlueLink.

    Compatibilité :
    - Ancien usage : MyBlueLinkClient(base_url=..., username=..., password=..., pin=...)
    - Nouvel usage : MyBlueLinkClient(config=MyBlueLinkConfig(...))
      ou MyBlueLinkClient(MyBlueLinkConfig(...))

    Pour l'instant :
    - Supporte un mode DEMO (aucun appel HTTP sortant, réponses simulées).
    - Initialise bien l’attribut _logged_in pour éviter l'AttributeError.
    - Encapsule les appels JSON afin d’éviter les JSONDecodeError brutes.
    """

    def __init__(
        self,
        config: Optional[MyBlueLinkConfig] = None,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        pin: Optional[str] = None,
        base_url: Optional[str] = None,
        demo_mode: Optional[bool] = None,
    ) -> None:
        """
        Constructeur rétrocompatible.

        Cas possibles :
        - MyBlueLinkClient(config=MyBlueLinkConfig(...))
        - MyBlueLinkClient(MyBlueLinkConfig(...))  [via param positionnel]
        - MyBlueLinkClient(base_url="...", username="...", password="...", pin="1234", demo_mode=False)
        - MyBlueLinkClient()  -> configuration lue depuis l'environnement.
        """

        # Si le premier paramètre a été passé de façon positionnelle,
        # il sera dans "config" (signature standard Python).
        if config is not None:
            self._config = config
        else:
            # On part de la config provenant de l'environnement
            env_cfg = MyBlueLinkConfig.from_env()

            # On permet d'écraser certains champs via les arguments nommés,
            # pour rester compatible avec l'ancien usage.
            self._config = MyBlueLinkConfig(
                username=username or env_cfg.username,
                password=password or env_cfg.password,
                pin=pin if pin is not None else env_cfg.pin,
                base_url=base_url if base_url is not None else env_cfg.base_url,
                demo_mode=demo_mode if demo_mode is not None else env_cfg.demo_mode,
            )

        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "BluelinkJimMobile/0.1",
                "Accept": "application/json, text/plain, */*",
            }
        )

        # 🔹 ÉTAT DE CONNEXION INITIAL : évite l'AttributeError
        self._logged_in: bool = False

        # Eventuel token, cookies, etc. (pour usage réel ultérieur)
        self._access_token: Optional[str] = None

    # ------------------------------------------------------------------
    # Utilitaires internes
    # ------------------------------------------------------------------

    @property
    def logged_in(self) -> bool:
        """
        Indique si le client considère être authentifié auprès de MyBlueLink.
        """
        return self._logged_in

    def _safe_json(self, resp: requests.Response) -> Dict[str, Any]:
        """
        Tente de décoder la réponse HTTP en JSON.
        En cas d’échec, lève une MyBlueLinkError lisible.
        """
        try:
            return resp.json()
        except JSONDecodeError as exc:
            # Pour debug, on pourrait logguer resp.text ici.
            raise MyBlueLinkError(
                "Réponse MyBlueLink non valide : le contenu n'est pas du JSON."
            ) from exc

    def _ensure_logged_in(self) -> None:
        """
        S'assure que le client est connecté avant d’appeler des endpoints.
        En mode DEMO, on se contente de considérer que la connexion est OK.
        """
        if self._logged_in:
            return

        # En mode DEMO, on ne fait pas de véritable login.
        if self._config.demo_mode:
            self._logged_in = True
            return

        # En mode réel, on appelle la méthode login() qui effectuera
        # l'authentification auprès de MyBlueLink.
        self.login()

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def login(self) -> None:
        """
        Authentifie l'utilisateur auprès de MyBlueLink.

        Implémentation actuelle :
        - En mode DEMO : on marque simplement le client comme connecté.
        - En mode réel : à implémenter avec les endpoints officiels/privés.
        """
        if self._config.demo_mode:
            # Pas d'appel HTTP, on simule un succès.
            self._logged_in = True
            return

        if not self._config.base_url:
            raise MyBlueLinkError(
                "BLUELINK_BASE_URL doit être défini pour le mode réel."
            )

        login_url = f"{self._config.base_url.rstrip('/')}/login"

        payload: Dict[str, Any] = {
            "username": self._config.username,
            "password": self._config.password,
        }

        # Si l'API MyBlueLink a besoin du PIN au login, on pourrait l'inclure ici.
        if self._config.pin:
            payload["pin"] = self._config.pin

        resp = self._session.post(login_url, json=payload, timeout=15)
        # Si la réponse est une erreur HTTP, on lève une exception requests.HTTPError.
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise MyBlueLinkError(
                f"Erreur HTTP lors de la connexion MyBlueLink : {exc}"
            ) from exc

        data = self._safe_json(resp)

        # Ici, adapter en fonction du format réel de l’API MyBlueLink
        token = data.get("access_token")
        if not token:
            raise MyBlueLinkError(
                "Connexion MyBlueLink réussie mais aucun token d'accès n'a été trouvé."
            )

        self._access_token = token
        self._session.headers["Authorization"] = f"Bearer {token}"
        self._logged_in = True

    def get_realtime_status(self, vin: str) -> Dict[str, Any]:
        """
        Récupère le statut temps réel du véhicule pour un VIN donné.

        En mode DEMO :
        - Retourne un JSON statique simulant une réponse MyBlueLink.

        En mode réel :
        - Nécessitera l'implémentation de l'endpoint exact MyBlueLink.
        """
        # 🔹 S'assure que _logged_in existe et est correctement initialisé.
        self._ensure_logged_in()

        if self._config.demo_mode:
            # Réponse de démonstration (à adapter selon ton UI).
            return {
                "vin": vin,
                "timestamp_utc": "2025-01-01T12:00:00Z",
                "odometer_km": 12345.6,
                "battery_level_percent": 82.0,
                "battery_range_km": 310.0,
                "is_charging": False,
                "doors_locked": True,
                "climate_on": False,
            }

        if not self._config.base_url:
            raise MyBlueLinkError(
                "BLUELINK_BASE_URL doit être défini pour récupérer le statut réel."
            )

        # Exemple d'URL, à remplacer par celle de l'API MyBlueLink réelle.
        status_url = f"{self._config.base_url.rstrip('/')}/vehicles/{vin}/status"

        try:
            resp = self._session.get(status_url, timeout=15)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise MyBlueLinkError(
                f"Erreur HTTP lors de la récupération du statut MyBlueLink : {exc}"
            ) from exc
        except requests.RequestException as exc:
            raise MyBlueLinkError(
                f"Erreur réseau lors de l'appel MyBlueLink : {exc}"
            ) from exc

        return self._safe_json(resp)


# ---------------------------------------------------------------------------
# Fabrique de client utilisée par le reste de l'application
# ---------------------------------------------------------------------------


def get_mybluelink_client() -> MyBlueLinkClient:
    """
    Fonction utilitaire appelée par les routes/services pour obtenir
    une instance de MyBlueLinkClient prête à l'emploi.

    Exemple typique d'utilisation dans une route :

        from app.integrations.mybluelink.client import get_mybluelink_client

        @router.post("/vehicles/{vehicle_id}/status/refresh")
        def refresh_status(...):
            client = get_mybluelink_client()
            data = client.get_realtime_status(vin=vin)
            ...

    """
    config = MyBlueLinkConfig.from_env()
    return MyBlueLinkClient(config=config)
