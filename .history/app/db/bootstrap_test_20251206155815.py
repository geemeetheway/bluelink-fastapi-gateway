# app/db/bootstrap_test.py
from app.db.session import SessionLocal
from app.db.models.vehicle import Vehicle
from app.db.models.vehicle_status import VehicleStatus  # même si pas encore utilisé


def main():
    db = SessionLocal()
    try:
        existing = (
            db.query(Vehicle)
            .filter(Vehicle.external_id == "demo-vehicle-1")
            .first()
        )

        if existing:
            print(f"Vehicle already exists with id={existing.id}")
            return

        v = Vehicle(
            external_id="demo-vehicle-1",
            name="Demo Vehicle",
            vin="VIN-123456-DEMO",
        )
        db.add(v)
        db.commit()
        db.refresh(v)
        print(f"Vehicle created with id={v.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
