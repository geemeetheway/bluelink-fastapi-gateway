from fastapi import FastAPI

app = FastAPI(
    title="Bluelink Gateway API",
    description="API démonstrateur Python/FastAPI pour télémétrie véhicule.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Endpoint très simple pour vérifier que l'API répond.
    Utile pour les tests, le monitoring, et comme point de départ.
    """
    return {"status": "ok"}
