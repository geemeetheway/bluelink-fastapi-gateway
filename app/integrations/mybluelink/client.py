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
# Configuration du client (pilotée par .env)
# ---------------------------------------------------------------------------


@dataclass
class MyBlueLinkConfig:
    """
    Configuration du client MyBlueLink.

    Les valeurs proviennent des variables d’environnement, typiquement définies
    dans le `.env` utilisé par Docker Compose.

    Variables supportées actuellement :

    - BLUELINK_ENABLED        : "true"/"false" (ou 1/0, yes/no…)
    - BLUELINK_IMPL           : "mock" | "python" | "node"
    - BLUELINK_USERNAME       : identifiant Bluelink (optionnel en mock)
    - BLUELINK_PASSWORD       : mot de passe Bluelink (optionnel en mock)
    - BLUELINK_PIN            : PIN Bluelink (optionnel)
    - BLUELINK_API_BASE_URL   : URL de base de l’API Bluelink à joindre
                                (utile quand BLUELINK_IMPL="python")

    Notes de design :
    - En mode "mock", on active systématiquement demo_mode=True
      (aucun appel HTTP externe).
    - En mode "python", demo_mode=False et on utilise BLUELINK_API_BASE_URL
      comme endpoint HTTP réel (quand vous l’aurez).
    - En mode "node", l’idée sera plus tard de joindre un microservice Node,
      mais pour l’instant on peut décider de rester en demo_mode=True.
    """

    username: str
    password: str
    pin: Optional[str] = None
    base_url: Optional[str] = None
    demo_mode: bool = True  # En mode DEMO, on ne fait pas d'appel HTTP réel.
    impl: str = "mock"
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "MyBlueLinkConfig":
        """
        Construit la configuration à partir des variables d'environnement.
        """

        # --------------------------------------------------------------
        # 1) Lecture des flags de haut niveau
        # --------------------------------------------------------------
        enabled_raw = os.getenv("BLUELINK_ENABLED", "true").strip().lower()
        enabled = enabled_raw not in ("0", "false", "no", "off", "")

        impl = os.getenv("BLUELINK_IMPL", "mock").strip().lower()
        # impl ∈ {"mock", "python", "node", ...}

        # --------------------------------------------------------------
        # 2) Identifiants utilisateur
        # --------------------------------------------------------------
        username = os.getenv("BLUELINK_USERNAME", "").strip()
        password = os.getenv("BLUELINK_PASSWORD", "").strip()
        pin = os.getenv("BLUELINK_PIN", "").strip() or None

        # --------------------------------------------------------------
        # 3) URL API
        # --------------------------------------------------------------
        # Dans votre .env actuel, c’est BLUELINK_API_BASE_URL
        api_base_url = os.getenv("BLUELINK_API_BASE_URL", "").strip() or None

        # --------------------------------------------------------------
        # 4) Détermination du demo_mode
        # --------------------------------------------------------------
        # Règle proposée :
        # - Si non activé => demo_mode = True (pas d’appels réels)
        # - Si impl == "mock" => demo_mode = True
        # - Si impl == "python" => demo_mode = False (intégration HTTP Python directe)
        # - Si impl == "node"   => pour l’instant on laisse demo_mode=True,
        #                          le temps d’implémenter un appel vers le service Node.
        if not enabled:
            demo_mode = True
        elif impl == "mock":
            demo_mode = True
        elif impl == "python":
            demo_mode = False
        elif impl == "node":
            # TODO plus tard : appeler un microservice Node.
            demo_mode = True
        else:
            # Valeur inconnue -> par prudence, on reste en démo.
            demo_mode = True

        # En mode réel (demo_mode=False), il faut un minimum de config.
        if not demo_mode:
            if not username or not password:
                raise MyBlueLinkError(
                    "BLUELINK_USERNAME et BLUELINK_PASSWORD doivent être définis "
                    "dans l'environnement quand BLUELINK_IMPL='python'."
                )
            if not api_base_url:
                raise MyBlueLinkError(
                    "BLUELINK_API_BASE_URL doit être défini pour le mode réel "
                    "(BLUELINK_IMPL='python')."
                )

        return cls(
            username=username,
            password=password,
            pin=pin,
            base_url=api_base_url,
            demo_mode=demo_mode,
            impl=impl,
            enabled=enabled,
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
        - MyBlueLinkClient(base_url="...", username="...", password="...", pin="1234",
                           demo_mode=False)
        - MyBlueLinkClient()  -> configuration lue depuis l'environnement.
        """

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
                impl=env_cfg.impl,
                enabled=env_cfg.enabled,
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
                "BLUELINK_API_BASE_URL doit être défini pour le mode réel."
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
        self._ensure_logged_in()

        # --------------------------------------------------------------
        # Mode DEMO : on renvoie un payload figé, cohérent avec votre
        #             schéma VehicleStatus (odometer, battery, doors, etc.).
        # --------------------------------------------------------------
        if self._config.demo_mode:
            return {
                "vin": vin,
                "timestamp_utc": "2025-01-01T12:00:00Z",
                "odometer_km": 12345.6,
                "battery_level_percent": 82.0,
                "battery_range_km": 310.0,
                "is_charging": False,
                "doors_locked": True,
                "climate_on": False,
                "raw_payload": {
                    "source": "demo",
                    "note": "Statut simulé par MyBlueLinkClient en mode DEMO.",
                },
            }

        # --------------------------------------------------------------
        # Mode réel : à brancher sur l’API MyBlueLink/Hyundai/Kia.
        # --------------------------------------------------------------
        if not self._config.base_url:
            raise MyBlueLinkError(
                "BLUELINK_API_BASE_URL doit être défini pour récupérer le statut réel."
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

        data = self._safe_json(resp)

        # À adapter si besoin pour remapper les clés de la réponse réelle vers
        # celles utilisées dans votre couche de service (vehicles_service).
        return data


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
