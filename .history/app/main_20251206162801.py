# app/main.py
from fastapi import FastAPI

from app.api.v1 import routes_health
from app.api.v1 import routes_vehicles
from app.core.config import settings

app = FastAPI(
    title="Bluelink Gateway API",
    description="API démonstrateur Python/FastAPI pour télémétrie véhicule.",
    version="0.1.0",
)

# Routers
app.include_router(routes_health.router, prefix=settings.API_V1_STR)
app.include_router(routes_vehicles.router, prefix=settings.API_V1_STR)
