# Bluelink FastAPI Gateway — Architecture Documentation

This document describes the internal architecture of the **Bluelink FastAPI Gateway**, the roles of each component, and how new features should integrate with the system.

---

# 🏛 High-Level Architecture

```
            ┌──────────────────────────────────────────┐
            │     Quasar Mobile App (Future Client)     │
            │               or external apps            │
            └──────────────────────────────────────────┘
                             │ REST API
                             ▼
                ┌──────────────────────────────┐
                │         FastAPI API          │
                │  (app/api/routers/*.py)      │
                └──────────────────────────────┘
                             │ Calls services
                             ▼
           ┌────────────────────────────────────────┐
           │               Services Layer            │
           │   (business logic + Bluelink wrapper)  │
           └────────────────────────────────────────┘
                             │ Uses ORM models
                             ▼
           ┌────────────────────────────────────────┐
           │       SQLAlchemy ORM Models            │
           │             (app/db/models)            │
           └────────────────────────────────────────┘
                             │ Via SessionLocal
                             ▼
           ┌────────────────────────────────────────┐
           │              PostgreSQL DB              │
           └────────────────────────────────────────┘

             Alembic handles database migrations.
```

---

# 📦 Directory Responsibilities

## `app/main.py`
- Creates FastAPI application  
- Registers routers  
- Registers startup/shutdown events  

---

## `app/api/routers/*`
Contains the public HTTP endpoints.  
Each router handles:

- Request validation (via Pydantic schemas)
- Calling the services layer
- Returning clean API responses

Routers *must never* contain business logic directly.

---

## `app/services/*`
Contains reusable business logic and external integrations, for example:

- Vehicle CRUD logic  
- Vehicle status processing  
- Bluelink API communication (future)

This layer isolates the domain logic from HTTP concerns.

---

## `app/schemas/*`
Pydantic v2 schemas used for:

- Validating incoming data  
- Serializing outgoing responses  
- Ensuring strong typing  

---

## `app/db/models/*`
SQLAlchemy declarative models that represent database tables.

Example:

```python
class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    vin = Column(String, unique=True, index=True)
```

---

## `app/db/session.py`
Provides the database session factory:

```python
SessionLocal = sessionmaker(...)
```

The API layer injects a session via FastAPI dependencies.

---

## `app/db/migrations` (Alembic)
Includes:

- `env.py` (migration runtime configuration)
- `versions/*.py` (generated migration scripts)

Developers should follow this workflow:

```bash
alembic revision --autogenerate -m "your message"
alembic upgrade head
```

---

# 🧠 Domain Entities

### Vehicle
Represents a car associated with a user or account.

Fields include:

- `external_id`
- `vin`
- `name`
- `is_active`

### VehicleStatus
Stores time‑series status snapshots:

- battery level  
- last update timestamp  
- any decoded diagnostic info  

---

# 🔌 External Services (Future)

The project is structured to add a **Bluelink API wrapper** inside:

```
app/services/bluelink_service.py
```

Expected responsibilities:

- Manage authentication tokens  
- Call Hyundai/Kia endpoints  
- Normalize remote data to local schemas  
- Detect and report changes  

---

# 📐 Architectural Principles

1. **Single Responsibility Principle**  
2. **Separation of Concerns**  
3. **Dependency Injection** via FastAPI  
4. **Stateless API** (future session caching in Redis optional)  
5. **Migrations-driven DB evolution** using Alembic  
6. **Docker-first deployment**  

---

# 🚀 Deployment Overview

You run the full stack using:

```bash
docker compose up --build
```

Services included:

- `bluelink-api` (FastAPI app)
- `bluelink-db` (PostgreSQL 16)

Environment variables come from `.env`.

---

# 📅 Future Roadmap

- OAuth2/JWT authentication  
- Redis caching  
- WebSocket real-time events  
- Bluelink telematics polling engine  
- Notifications on status change  
- Multi-user support  
- Vehicle commands (lock/unlock, climate, charging)  

---

If you'd like, I can also generate:

- `docs/sequence_diagrams.md`  
- UML diagrams  
- Architecture PNG images  
- A Mermaid diagram for GitHub rendering  
