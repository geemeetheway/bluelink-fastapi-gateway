# API Reference — Bluelink FastAPI Gateway

This document describes the public HTTP API exposed by the **Bluelink FastAPI Gateway**.

Base URL (local development, Docker):

- `http://localhost:8000`

All JSON responses follow standard HTTP status codes and use Pydantic v2 schemas.

---

## Versioning & Prefix

All endpoints are currently under:

- `/api/v1`

The main prefix is configured via the `API_V1_STR` environment variable (default: `/api/v1`).

---

## Health

### `GET /api/v1/health`

Simple health check endpoint to verify that the API is running.

**Response 200**

```json
{
  "status": "ok",
  "service": "bluelink-gateway"
}
```

---

## Vehicles

Vehicles represent registered cars in the system linked to external Bluelink IDs and VINs.

### Vehicle Schema

**VehicleCreate** (request)

```json
{
  "external_id": "string",
  "name": "string",
  "vin": "string"
}
```

**VehicleRead** (response)

```json
{
  "id": 1,
  "external_id": "string",
  "name": "string",
  "vin": "string",
  "is_active": true
}
```

### `POST /api/v1/vehicles` — Create a vehicle

Registers a new vehicle in the system.

**Request Body**

- `external_id` — string, required (external system ID, e.g. Bluelink)
- `name` — string, required (human readable name)
- `vin` — string, required (unique VIN)

**Responses**

- `201 Created` — returns `VehicleRead`
- `400 Bad Request` — invalid payload or VIN already exists

---

### `GET /api/v1/vehicles` — List vehicles

Returns all active vehicles.

**Responses**

- `200 OK` — array of `VehicleRead`

Example:

```json
[
  {
    "id": 1,
    "external_id": "demo-vehicle-1",
    "name": "Ioniq 5 Blanche",
    "vin": "VIN-123456-DEMO",
    "is_active": true
  }
]
```

---

### `GET /api/v1/vehicles/{vehicle_id}` — Get vehicle by ID

Returns a single vehicle by its internal ID.

**Path Parameters**

- `vehicle_id` — integer, required

**Responses**

- `200 OK` — `VehicleRead`
- `404 Not Found` — vehicle does not exist or is inactive

---

## Vehicle Status (Telemetry)

Vehicle status represents a point-in-time snapshot of telemetry data (battery, doors, odometer, etc.).

### Status Schemas

**VehicleStatusCreate** (request)

```json
{
  "battery_level": 85.5,
  "doors_locked": true,
  "odometer_km": 12345.6
}
```

- `battery_level` — number (0–100), optional
- `doors_locked` — boolean, required
- `odometer_km` — number, optional

**VehicleStatusRead** (response)

```json
{
  "id": 1,
  "vehicle_id": 1,
  "timestamp": "2025-01-01T12:00:00Z",
  "battery_level": 85.5,
  "doors_locked": true,
  "odometer_km": 12345.6
}
```

---

### `POST /api/v1/vehicles/{vehicle_id}/status` — Create a new status

Creates a new status entry for the given vehicle.

**Path Parameters**

- `vehicle_id` — integer, required

**Request Body**

`VehicleStatusCreate`

**Responses**

- `201 Created` — `VehicleStatusRead`
- `404 Not Found` — vehicle does not exist
- `400 Bad Request` — invalid body

---

### `GET /api/v1/vehicles/{vehicle_id}/statuses` — List all statuses

Returns all status entries for the given vehicle, typically sorted from newest to oldest.

**Path Parameters**

- `vehicle_id` — integer, required

**Responses**

- `200 OK` — array of `VehicleStatusRead`
- `404 Not Found` — vehicle does not exist

---

### `GET /api/v1/vehicles/{vehicle_id}/status/latest` — Get latest status

Returns the latest status entry for the given vehicle.

**Path Parameters**

- `vehicle_id` — integer, required

**Responses**

- `200 OK` — `VehicleStatusRead`
- `404 Not Found` — vehicle has no status or does not exist

---

## Error Handling

Common error responses:

- `400 Bad Request`
  - Invalid JSON
  - Missing or invalid fields
- `404 Not Found`
  - Vehicle or status not found
- `500 Internal Server Error`
  - Unexpected server-side error

Error payload shape may follow FastAPI’s default error format, e.g.:

```json
{
  "detail": "Vehicle not found"
}
```

As the project evolves, a standardized error response format can be introduced.
