# app/services/vehicles.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models.vehicle import Vehicle
from app.db.models.vehicle_status import VehicleStatus
from app.schemas.vehicle import VehicleCreate


def create_vehicle(db: Session, data: VehicleCreate) -> Vehicle:
    """
    Crée un nouveau véhicule à partir des données fournies.
    """
    v = Vehicle(
        external_id=data.external_id,
        name=data.name,
        vin=data.vin,
        is_active=True,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def list_vehicles(db: Session) -> List[Vehicle]:
    """
    Retourne la liste de tous les véhicules actifs.
    """
    return db.query(Vehicle).filter(Vehicle.is_active == True).all()  # noqa: E712


def get_vehicle(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    """
    Retourne un véhicule par son identifiant interne.
    """
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def get_latest_status(db: Session, vehicle_id: int) -> Optional[VehicleStatus]:
    """
    Retourne le dernier statut connu pour un véhicule donné.
    """
    return (
        db.query(VehicleStatus)
        .filter(VehicleStatus.vehicle_id == vehicle_id)
        .order_by(VehicleStatus.timestamp.desc())
        .first()
    )
