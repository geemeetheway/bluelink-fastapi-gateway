// frontend-react/src/types.ts

// Véhicule tel que renvoyé par l'API
export interface Vehicle {
  id: number;
  external_id: string;
  name: string;
  vin: string;
  is_active: boolean;
}

// DTO pour créer un véhicule (correspond au body POST /vehicles)
export interface CreateVehicleDto {
  external_id: string;
  name: string;
  vin: string;
}

// Statut de véhicule tel que renvoyé par l'API
export interface VehicleStatus {
  id: number;
  vehicle_id: number;
  timestamp: string; // ISO 8601
  battery_level?: number | null;
  doors_locked: boolean;
  odometer_km?: number | null;
}

// DTO pour créer un statut (body POST /vehicles/{id}/status)
export interface CreateStatusDto {
  battery_level?: number | null;
  doors_locked: boolean;
  odometer_km?: number | null;
}
