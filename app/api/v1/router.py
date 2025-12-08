from fastapi import APIRouter

from app.api.v1 import routes_vehicles
from app.api.v1.routes_health import router as health_router
from app.api.v1.routes_vehicles import router as vehicles_router

# Routeur global pour /api/v1
api_router = APIRouter()

# On monte les sous-routeurs.
# ATTENTION :
# - Ici on suppose que routes_health.py et routes_vehicles.py
#   définissent chacun `router = APIRouter()` *sans* prefix.
# - Les préfixes sont donc centralisés ici.
api_router.include_router(health_router,            tags=["health"],    prefix="/health")
api_router.include_router(routes_vehicles.router,   tags=["vehicles"],  prefix="")
