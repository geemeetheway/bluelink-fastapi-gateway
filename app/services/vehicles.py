# app/services/vehicles.py
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.db.models.vehicle import Vehicle
from app.db.models.vehicle_status import VehicleStatus
from app.schemas.vehicle import VehicleCreate, VehicleStatusCreate


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

def create_status(
    db: Session,
    vehicle_id: int,
    data: VehicleStatusCreate,
) -> VehicleStatus:
    """
    Crée un nouveau statut pour un véhicule donné.
    """
    status_obj = VehicleStatus(
        vehicle_id=vehicle_id,
        battery_level=data.battery_level,
        doors_locked=data.doors_locked,
        odometer_km=data.odometer_km,
    )
    db.add(status_obj)
    db.commit()
    db.refresh(status_obj)
    return status_obj

def list_statuses(
    db: Session,
    vehicle_id: int,
) -> List[VehicleStatus]:
    """
    Retourne l'historique des statuts pour un véhicule donné,
    du plus récent au plus ancien.
    """
    return (
        db.query(VehicleStatus)
        .filter(VehicleStatus.vehicle_id == vehicle_id)
        .order_by(VehicleStatus.timestamp.desc())
        .all()
    )

def _get_nested(d: Dict[str, Any], path: list[str], default: Any = None) -> Any:
    """
    Helper pour naviguer dans un dict JSON de manière défensive.

    Exemple :
        _get_nested(data, ["result", "status", "evStatus", "batteryStatus"], 0)
    """
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur

def refresh_status_from_mybluelink(
    db: Session,
    vehicle: Vehicle,
    bluelink_payload: Dict[str, Any],
) -> VehicleStatus:
    """
    Crée un VehicleStatus à partir du JSON retourné par MyBlueLink.

    Le JSON est supposé ressembler à ton fichier exampleData/vehicleStatus.json.
    """

    status_root = _get_nested(bluelink_payload, ["result", "status"], default={})
    ev_status = status_root.get("evStatus", {}) if isinstance(status_root, dict) else {}

    # Batterie : dans ton exemple, "batteryStatus" est directement un entier.
    battery_level = _get_nested(ev_status, ["batteryStatus"], default=0)
    if isinstance(battery_level, dict):
        # fallback défensif si un jour c'est un objet
        battery_level = battery_level.get("value", 0)
    try:
        battery_level_int = int(battery_level)
    except (TypeError, ValueError):
        battery_level_int = 0

    # Statut de charge (bool)
    is_charging = bool(_get_nested(ev_status, ["batteryCharge"], default=False))

    # Branché / plug-in (0/1) dans l’exemple
    plugin_raw = _get_nested(ev_status, ["batteryPlugin"], default=0)
    try:
        plugin_int = int(plugin_raw)
    except (TypeError, ValueError):
        plugin_int = 0
    is_plugged = plugin_int == 1

    # Temps restant de charge (remainTime2.etc1.value en minutes)
    remain_time2 = _get_nested(ev_status, ["remainTime2"], default={})
    remaining_charge_minutes = 0
    if isinstance(remain_time2, dict):
        etc1 = remain_time2.get("etc1", {})
        if isinstance(etc1, dict):
            val = etc1.get("value")
            try:
                remaining_charge_minutes = int(val)
            except (TypeError, ValueError):
                remaining_charge_minutes = 0

    # Range total (si tu as ce champ dans ton JSON, adapte ici).
    # Exemple défensif : on cherche un champ "dte" (distance to empty) si présent.
    total_range_km = 0
    dte = status_root.get("dte") if isinstance(status_root, dict) else None
    if isinstance(dte, dict):
        # à adapter selon l’exemple concret
        val = dte.get("rangeByFuel", 0)
        try:
            total_range_km = int(val)
        except (TypeError, ValueError):
            total_range_km = 0

    # Coordonnées GPS : souvent un endpoint séparé, mais si ton payload les contient,
    # adapte ici (ex : status_root["lastLocation"]["coord"]["lat"] / "lon"]).
    latitude = None
    longitude = None
    last_location = status_root.get("lastLocation") if isinstance(status_root, dict) else None
    if isinstance(last_location, dict):
        coord = last_location.get("coord", {})
        if isinstance(coord, dict):
            latitude = coord.get("lat")
            longitude = coord.get("lon")

    # On garde le payload brut dans la colonne raw_payload (JSON ou TEXT)
    import json

    raw_payload_str = json.dumps(bluelink_payload, ensure_ascii=False)

    status_obj = VehicleStatus(
        vehicle_id=vehicle.id,
        battery_level=battery_level_int,
        is_charging=is_charging,
        is_plugged=is_plugged,
        total_range_km=total_range_km,
        remaining_charge_minutes=remaining_charge_minutes,
        latitude=latitude,
        longitude=longitude,
        raw_payload=raw_payload_str,
    )

    db.add(status_obj)
    db.commit()
    db.refresh(status_obj)

    return status_obj