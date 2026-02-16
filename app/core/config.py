# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Paramètres principaux de l'application.
    Chargés depuis le fichier .env ou les variables d'environnement.
    """

    # =====================================================
    # API
    # =====================================================
    API_V1_STR: str = "/api/v1"

    # =====================================================
    # Base de données
    # =====================================================
    # La valeur par défaut est sqlite pour du dev local,
    # mais en pratique, on la surchargera via la variable d'env DATABASE_URL.
    DATABASE_URL: str = Field(
        default="sqlite:///./bluelink.db",
        env="DATABASE_URL",
    )

    # =====================================================
    # BlueLink - Activation et implémentation
    # =====================================================
    # Permettra plus tard de choisir entre "mock", "python", "node", etc.
    BLUELINK_ENABLED: bool = Field(
        default=True,
        env="BLUELINK_ENABLED",
    )
    BLUELINK_IMPL: str = Field(
        default="mock",  # valeurs possibles : "mock", "python", "node"
        env="BLUELINK_IMPL",
    )

    # =====================================================
    # BlueLink - Identifiants utilisateur
    # =====================================================
    # On lit les variables déjà présentes dans ton .env :
    #   MYBLUELINK_USERNAME, MYBLUELINK_PASSWORD, MYBLUELINK_PIN
    BLUELINK_USERNAME: str | None = Field(
        default=None,
        env="MYBLUELINK_USERNAME",
    )
    BLUELINK_PASSWORD: str | None = Field(
        default=None,
        env="MYBLUELINK_PASSWORD",
    )
    BLUELINK_PIN: str | None = Field(
        default=None,
        env="MYBLUELINK_PIN",
    )

    # =====================================================
    # BlueLink - Paramètres véhicule
    # =====================================================
    # VIN de la voiture (issu de MYBLUELINK_VIN dans ton .env)
    BLUELINK_VIN: str | None = Field(
        default=None,
        env="MYBLUELINK_VIN",
    )

    # Marque & région (au besoin plus tard)
    BLUELINK_BRAND: str = Field(
        default="hyundai",
        env="BLUELINK_BRAND",
    )
    BLUELINK_REGION: str = Field(
        default="CA",
        env="BLUELINK_REGION",
    )

    # =====================================================
    # BlueLink - API HTTP
    # =====================================================
    # Client HTTP principal : on mappe BLUELINK_BASE_URL sur
    # ta variable existante MYBLUELINK_BASE_URL dans .env
    #   MYBLUELINK_BASE_URL="https://mybluelink.ca"
    BLUELINK_BASE_URL: str = Field(
        default="https://mybluelink.ca",
        env="MYBLUELINK_BASE_URL",
    )

    # Clé API (si nécessaire)
    BLUELINK_API_KEY: str | None = Field(
        default=None,
        env="MYBLUELINK_API_KEY",
    )

    class Config:
        # Pydantic Settings lira automatiquement ce fichier .env
        env_file = ".env"
        env_file_encoding = "utf-8"

        # IMPORTANT :
        # On demande à Pydantic d'IGNORER les variables d'env qui ne
        # correspondent pas à un champ du modèle (par ex. BLUELINK_API_BASE_URL).
        extra = "ignore"


# Instance globale utilisée dans le reste du code
settings = Settings()
