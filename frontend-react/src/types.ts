// frontend-react/src/types.ts

// Représente un véhicule connu par l’API
export interface Vehicle {
  id: number;
  external_id: string | null;
  vin: string | null;
  nickname: string | null;
  is_active: boolean;
  created_at: string; // ISO datetime (string)
}

// Représente un “snapshot” d’état du véhicule (battery, charge, etc.)
export interface VehicleStatus {
  id: number;
  vehicle_id: number;
  timestamp: string; // ISO datetime

  // Niveau de batterie (en %, généralement)
  battery_level: number | null;

  // Localisation (si disponible)
  latitude?: number | null;
  longitude?: number | null;

  // État de charge
  is_charging?: boolean | null;
  is_plugged?: boolean | null;

  // Autonomie estimée
  total_range_km?: number | null;

  // Temps de charge restant (en minutes)
  remaining_charge_minutes?: number | null;

  // Payload brut renvoyé par MyBlueLink (optionnel)
  raw_payload?: unknown;
}

// Pour typer les erreurs simples côté front
export interface ApiError {
  message: string;
}
