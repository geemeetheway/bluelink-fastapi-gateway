# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    """
    Paramètres principaux de l'application.
    Basés sur les variables d'environnement, avec des valeurs par défaut
    raisonnables pour le développement local.
    """

    # Préfixe d'API
    API_V1_STR: str = "/api/v1"

    # URL de la base de données (sqlite par défaut pour le dev local)
    DATABASE_URL: str = "sqlite:///./bluelink.db"

    # On gardera ces champs pour plus tard (API externe, secrets, etc.)
    # BLUELINK_BASE_URL: AnyUrl | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale à importer dans le reste du code
settings = Settings()
