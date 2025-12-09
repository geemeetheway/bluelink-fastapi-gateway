# app/services/vehicles.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.vehicle import Vehicle
from app.db.models.vehicle_status import VehicleStatus
from app.integrations.mybluelink_client import MyBlueLinkClient

from app.schemas.vehicle import VehicleCreate, VehicleStatusCreate, VehicleStatusRead

# Service de gestion des véhicules et de leurs statuts.
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

# Liste tous les véhicules actifs
def list_vehicles(db: Session) -> List[Vehicle]:
    """
    Retourne la liste de tous les véhicules actifs.
    """
    return db.query(Vehicle).filter(Vehicle.is_active == True).all()  # noqa: E712

# Retourne un véhicule par son identifiant interne
def get_vehicle(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    """
    Retourne un véhicule par son identifiant interne.
    """
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

# Retourne le dernier statut connu pour un véhicule donné
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

# Crée un nouveau statut pour un véhicule donné
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

# Liste l'historique des statuts pour un véhicule donné
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

# Helper pour naviguer dans un dict JSON de manière défensive.
def _get_nested(d: Dict[str, Any], path: list[str], default: Any = None) -> Any:
    """
    Helper pour naviguer dans un dict JSON de manière défensive.

    Exemple :
        _get_nested(data, ["result", "status", "evStatus", "batteryStatus"], 0)
    """
    current: Any = d
    for part in path:
        if current is None:
            return default
        # support index de liste en string "0"
        if isinstance(current, list):
            try:
                idx = int(part)
            except ValueError:
                return default
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return default
        elif isinstance(current, dict):
            if part not in current:
                return default
            current = current[part]
        else:
            return default
    return current

# Crée un VehicleStatus à partir du JSON retourné par MyBlueLink.
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

# Mapping détaillé du payload MyBlueLink vers VehicleStatus
def _map_bluelink_payload_to_vehicle_status(
    vehicle: Vehicle,
    payload: Dict[str, Any],
) -> VehicleStatus:
    """
    Crée un VehicleStatus à partir du payload MyBlueLink.
    Ne commit PAS ici, on laisse le service appelant gérer la transaction.
    """
    status_root = payload.get("result", {}).get("status", {})
    ev = status_root.get("evStatus", {}) or {}
    battery = status_root.get("battery", {}) or {}

    # Batterie (en %)
    battery_level = _get_nested(battery, ["batSoc"], default=None)
    if battery_level is None:
        battery_level = _get_nested(ev, ["batteryStatus"], default=None)

    if battery_level is not None:
        try:
            battery_level = int(battery_level)
        except (TypeError, ValueError):
            battery_level = None

    # Charge en cours ?
    is_charging_raw = ev.get("batteryCharge")
    is_charging = bool(is_charging_raw) if is_charging_raw is not None else False

    # Véhicule branché ?
    battery_plugin_raw = ev.get("batteryPlugin")
    if battery_plugin_raw is None:
        is_plugged = False
    else:
        # Certains payloads mettent 0/1, d'autres True/False
        is_plugged = bool(battery_plugin_raw)

    # Autonomie totale (km)
    total_range_km = _get_nested(
        ev,
        ["drvDistance", "0", "rangeByFuel", "evModeRange", "value"],
        default=None,
    )
    if total_range_km is not None:
        try:
            total_range_km = int(total_range_km)
        except (TypeError, ValueError):
            total_range_km = None

    # Temps restant de charge (minutes)
    # D’après ton JSON : remainTime2.etc1.value
    remaining_charge_minutes = _get_nested(
        ev,
        ["remainTime2", "etc1", "value"],
        default=None,
    )
    if remaining_charge_minutes is not None:
        try:
            remaining_charge_minutes = int(remaining_charge_minutes)
        except (TypeError, ValueError):
            remaining_charge_minutes = None

    # Latitude / longitude : si tu as un autre endpoint, tu les rempliras ici plus tard.
    latitude = None
    longitude = None

    vs = VehicleStatus(
        vehicle_id=vehicle.id,
        battery_level=battery_level,
        is_charging=is_charging,
        is_plugged=is_plugged,
        total_range_km=total_range_km,
        remaining_charge_minutes=remaining_charge_minutes,
        latitude=latitude,
        longitude=longitude,
        raw_payload=payload,
    )

    return vs

# Service de synchronisation MyBlueLink
_bluelink_client = MyBlueLinkClient()

# Synchronise le statut d’un véhicule depuis MyBlueLink
async def sync_vehicle_status_from_bluelink(
    db: Session,
    vehicle_id: int,
) -> VehicleStatus:
    """
    1. Récupère le véhicule (pour son VIN).
    2. Appelle MyBlueLink.
    3. Mappe la réponse vers VehicleStatus.
    4. Enregistre un NOUVEAU VehicleStatus (historique).
    5. Retourne le VehicleStatus créé.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None:
        raise ValueError(f"Vehicle {vehicle_id} not found")

    if not vehicle.vin:
        raise ValueError(f"Vehicle {vehicle_id} has no VIN configured")

    payload = await _bluelink_client.get_vehicle_status_by_vin(vehicle.vin)

    vs = _map_bluelink_payload_to_vehicle_status(vehicle, payload)

    db.add(vs)
    db.commit()
    db.refresh(vs)

    return vs

# Retourne le dernier VehicleStatus pour un véhicule donné
def get_latest_status(db: Session, vehicle_id: int) -> Optional[VehicleStatus]:
    """
    Retourne le dernier VehicleStatus pour un véhicule donné.
    Utile si tu veux afficher l’historique sans recontacter MyBlueLink.
    """
    return (
        db.query(VehicleStatus)
        .filter(VehicleStatus.vehicle_id == vehicle_id)
        .order_by(desc(VehicleStatus.timestamp))
        .first()
    )
