# app/api/v1/routes_health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"])
def health_check():
    """
    Endpoint de vérification de l'état de l'API.
    Séparé dans un router dédié pour illustrer l'architecture modulaire.
    """
    return {"status": "ok"}
