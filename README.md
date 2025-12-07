# Bluelink FastAPI Gateway

Backend demonstration project built with **Python**, **FastAPI**, **SQLAlchemy**, **Alembic** and **PostgreSQL**.

The goal of this project is to model a simple **vehicle telemetry gateway** inspired by Hyundai / Kia Bluelink (E-GMP platform).  
It exposes a REST API to manage vehicles and their status over time (battery level, doors lock state, odometer, etc.).

This project is also used as a **portfolio piece** to showcase backend skills aligned with stacks similar to:

- Python / FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Docker / Docker Compose
- Clean service / router / schema separation

---

## Features

- FastAPI application with a clear modular structure:
  - `app/core` → configuration
  - `app/db` → SQLAlchemy models, session management, Alembic integration
  - `app/schemas` → Pydantic v2 schemas (from_attributes)
  - `app/services` → business logic / service layer
  - `app/api/v1` → API routers and endpoints
- SQLAlchemy ORM models:
  - `Vehicle`
  - `VehicleStatus`
- Alembic migrations:
  - Initial schema migration applied automatically on startup
- PostgreSQL database running in Docker
- REST API endpoints:
  - Health check
  - CRUD-like operations for vehicles
  - Creation and history of vehicle status (telemetry)
- Ready for extension:
  - Integration with real external Bluelink-like APIs
  - Authentication (JWT)
  - Background tasks and data pipelines

---

## Tech Stack

- **Language**: Python 3.12
- **Web framework**: FastAPI
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Database**: PostgreSQL 16
- **Containerization**: Docker & Docker Compose
- **Configuration**: `.env` + Pydantic Settings
- **Schemas**: Pydantic v2 (`ConfigDict(from_attributes=True)`)

---

## Architecture Overview

```
app/
├─ api/
│  └─ v1/
│     ├─ routes_health.py      # Health check endpoint
│     └─ routes_vehicles.py    # Vehicle + status endpoints
├─ core/
│  └─ config.py                # Settings, DATABASE_URL, API prefix, etc.
├─ db/
│  ├─ base.py                  # Base model
│  ├─ models/
│  │  ├─ vehicle.py            # Vehicle model
│  │  └─ vehicle_status.py     # VehicleStatus model
│  └─ session.py               # SessionLocal, get_db dependency
├─ schemas/
│  └─ vehicle.py               # Pydantic v2 schemas (Vehicle, VehicleStatus)
├─ services/
│  └─ vehicles.py              # Business logic for vehicles and statuses
└─ main.py                     # FastAPI application, routers wiring

alembic/
├─ env.py                      # Alembic configuration
└─ versions/
   └─ c9a8516ab1ca_init_schema.py  # Initial schema migration
```

---

## Getting Started (Docker)

### Prerequisites

- Docker
- Docker Compose

### 1. Environment variables

Create a `.env` file at the project root:

```env
API_V1_STR=/api/v1
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/bluelink
```

> Note: in a real deployment, credentials would be stored in a secure secrets manager or environment variables, not committed.

### 2. Build and run with Docker Compose

From the project root:

```bash
docker compose up --build
```

This will:

- start a PostgreSQL 16 instance (`db` service)
- build and start the FastAPI app (`api` service)
- apply Alembic migrations on startup
- expose the API on port `8000`

### 3. Open API docs

Once running, open your browser at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### Health Check
**GET** `/api/v1/health`

---

### Vehicles

**POST** `/api/v1/vehicles`  
Create a vehicle.

**GET** `/api/v1/vehicles`  
List vehicles.

**GET** `/api/v1/vehicles/{vehicle_id}`  
Get a vehicle by ID.

---

### Vehicle Status (Telemetry)

**POST** `/api/v1/vehicles/{vehicle_id}/status`  
Create a new status entry.

**GET** `/api/v1/vehicles/{vehicle_id}/statuses`  
List all statuses.

**GET** `/api/v1/vehicles/{vehicle_id}/status/latest`  
Get the latest known status.

---

## Possible Next Steps

- External Bluelink API integration  
- Background polling tasks  
- JWT authentication  
- GitHub Actions CI/CD  
- PostGIS for geolocation  

---

## Author

**Jimmy Lavoie**  
Backend / Full-stack Developer  
GitHub: https://github.com/geemeetheway  
Website: https://jimmylavoie.com
