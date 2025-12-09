# app/core/config.py
import os
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

    # Identifiants de connexion BlueLink
    MYBLUELINK_USERNAME: str = os.getenv("MYBLUELINK_USERNAME")
    MYBLUELINK_PASSWORD: str = os.getenv("MYBLUELINK_PASSWORD")
    MYBLUELINK_PIN: str = os.getenv("MYBLUELINK_PIN")
    MYBLUELINK_VIN: str = os.getenv("MYBLUELINK_VIN")


    #   Utilise la variable d'environnement MYBLUELINK_BASE_URL définie dans ton `.env`.
    #   Valeur par défaut au cas où la variable n'est pas présente.
    mybluelink_base_url: str = os.getenv(
        "MYBLUELINK_BASE_URL",
        "https://mybluelink.ca",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale à importer dans le reste du code
settings = Settings()
