# app/api/v1/routes_vehicles.py

from typing import List

import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleRead,
    VehicleStatusRead,
    VehicleStatusCreate,
)
from app.services import vehicles as vehicle_service
from app.integrations.mybluelink.client import MyBlueLinkClient, MyBlueLinkError

router = APIRouter()

# Client MyBlueLink "global" très simple.
# Tu peux remplacer par une dépendance FastAPI si tu préfères.
BLUELINK_client = MyBlueLinkClient(
    base_url=os.getenv("BLUELINK_BASE_URL", "https://mybluelink.ca"),
    username=os.getenv("BLUELINK_USERNAME", ""),
    password=os.getenv("BLUELINK_PASSWORD", ""),
    pin=os.getenv("BLUELINK_PIN", ""),
)


#------------------ ENDPOINTS VEHICLES ET STATUSES ------------------
#------------------------------------------------------------
# /vehicles [post]
@router.post(
    "/vehicles",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau véhicule",
)
def create_vehicle_endpoint(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
):
    """
    Crée un véhicule à partir des données fournies.
    """
    v = vehicle_service.create_vehicle(db, data=payload)
    return v

#------------------------------------------------------------
# /vehicles [get]
@router.get(
    "/vehicles",
    response_model=List[VehicleRead],
    summary="Lister les véhicules",
)
def list_vehicles_endpoint(
    db: Session = Depends(get_db),
):
    """
    Liste tous les véhicules actifs.
    """
    return vehicle_service.list_vehicles(db)

#------------------------------------------------------------
# /vehicles/{vehicle_id} [get]
@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleRead,
    summary="Obtenir un véhicule par son ID",
)
def get_vehicle_endpoint(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    Récupère un véhicule à partir de son identifiant interne.
    """
    v = vehicle_service.get_vehicle(db, vehicle_id=vehicle_id)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    return v

#------------------------------------------------------------
# /vehicles/{vehicle_id}/status [post]
@router.get(
    "/vehicles/{vehicle_id}/status",
    response_model=VehicleStatusRead,
)
def get_vehicle_status(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    Retourne le DERNIER état connu du véhicule depuis la BD.
    Ne déclenche PAS de nouvel appel MyBlueLink.
    """
    vs = vehicle_service.get_latest_status(db, vehicle_id)
    if not vs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No status found for this vehicle",
        )
    return vs

#------------------------------------------------------------
# /vehicles/{vehicle_id}/status/sync [post]
@router.post(
    "/vehicles/{vehicle_id}/status/sync",
    response_model=VehicleStatusRead,
)
async def sync_vehicle_status(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    1. Appelle MyBlueLink pour le VIN correspondant.
    2. Enregistre un nouveau VehicleStatus dans la BD.
    3. Retourne ce nouveau status.
    """
    try:
        vs = await vehicle_service.sync_vehicle_status_from_bluelink(db, vehicle_id)
    except ValueError as e:
        # Vehicle not found ou VIN manquant
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        # Autres erreurs (réseau, parsing, etc.)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error while fetching data from MyBlueLink: {e}",
        ) from e

    return vs

#------------------------------------------------------------
# /vehicles/{vehicle_id}/statuses [get]
@router.get(
    "/vehicles/{vehicle_id}/statuses",
    response_model=List[VehicleStatusRead],
    summary="Lister les statuts d'un véhicule",
)
def list_statuses_endpoint(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    Retourne l'historique des statuts pour un véhicule donné,
    du plus récent au plus ancien.
    """
    v = vehicle_service.get_vehicle(db, vehicle_id=vehicle_id)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    return vehicle_service.list_statuses(db, vehicle_id=vehicle_id)

#------------------------------------------------------------
# /vehicles/{vehicle_id}/status/latest [get]
@router.get(
    "/vehicles/{vehicle_id}/status/latest",
    response_model=VehicleStatusRead,
    summary="Obtenir le dernier statut d'un véhicule",
)
def get_latest_status_endpoint(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    Retourne le dernier statut connu pour un véhicule donné.
    """
    status_obj = vehicle_service.get_latest_status(db, vehicle_id=vehicle_id)
    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No status found for this vehicle",
        )
    return status_obj

#------------------------------------------------------------
# /vehicles/{vehicle_id}/status/refresh [post]
@router.post(
    "/vehicles/{vehicle_id}/status/refresh",
    response_model=VehicleStatusRead,
    summary="Rafraîchir le statut d'un véhicule via MyBlueLink",
)
def refresh_status_from_BLUELINK_endpoint(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    Récupère le statut temps réel du véhicule via l’API MyBlueLink,
    le transforme en VehicleStatus, le sauvegarde dans la base,
    et retourne ce dernier statut.
    """

    vehicle = vehicle_service.get_vehicle(db, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    # On suppose que tu as un champ 'vin' dans ton modèle Vehicle.
    vin = getattr(vehicle, "vin", None)
    if not vin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle does not have a VIN configured for MyBlueLink.",
        )

    try:
        bluelink_json = BLUELINK_client.get_realtime_status(vin=vin)
    except MyBlueLinkError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"MyBlueLink error: {exc}",
        )

    status_obj = vehicle_service.refresh_status_from_mybluelink(
        db=db,
        vehicle=vehicle,
        bluelink_payload=bluelink_json,
    )

    return status_obj
