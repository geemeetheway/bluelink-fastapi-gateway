# app/main.py
from fastapi import FastAPI

from app.api.v1 import routes_health

app = FastAPI(
    title="Bluelink Gateway API",
    description="API démonstrateur Python/FastAPI pour télémétrie véhicule.",
    version="0.1.0",
)

# On "branche" le router health sur le chemin /api/v1
app.include_router(routes_health.router, prefix="/api/v1")
