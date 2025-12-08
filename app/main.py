# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


# =====================================================================
# Création de l'application FastAPI
# =====================================================================

app = FastAPI(
    title=getattr(settings, "PROJECT_NAME", "Bluelink FastAPI Gateway"),
    version=getattr(settings, "VERSION", "0.1.0"),
    docs_url="/docs",
    redoc_url="/redoc",
)


# =====================================================================
# Configuration CORS
# =====================================================================

# Origines autorisées en développement.
# A ajuster plus tard / restreindre en prod (par ex. vrai domaine).
origins = [
    "http://localhost:5173",    # React (Vite)
    "http://127.0.0.1:5173",
    "http://localhost:9000",    # Quasar dev
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# Routes de base
# =====================================================================

@app.get("/api/v1/health", tags=["health"])
def health_check():
    """
    Endpoint de santé simple pour vérifier que l'API répond.
    Utilisé aussi bien par Docker que par les frontends.
    """
    return {"status": "ok"}


# =====================================================================
# Inclusion du router principal (versionnée)
# =====================================================================

# Si dans app/core/config.py tu as quelque chose comme :
# API_V1_STR = "/api/v1"
# on l'utilise, sinon on retombe sur "/api/v1" par défaut.
api_prefix = getattr(settings, "API_V1_STR", "/api/v1")

app.include_router(api_router, prefix=api_prefix)
