// frontend-react/src/api/vehicles.ts

import client from "./client";  
import type { Vehicle, VehicleStatus } from "../types";

/**
 * Récupère la liste des véhicules.
 * GET /vehicles
 */
export async function listVehicles(): Promise<Vehicle[]> {
  const res = await client.get<Vehicle[]>("/vehicles");
  return res.data;
}

/**
 * Récupère le dernier status connu d’un véhicule.
 * GET /vehicles/{vehicleId}/status/latest
 *
 * Si ton backend expose un autre chemin, adapte simplement l’URL.
 */
export async function getLatestVehicleStatus(
  vehicleId: number,
): Promise<VehicleStatus | null> {
  const res = await client.get<VehicleStatus | null>(
    `/vehicles/${vehicleId}/status/latest`,
  );
  return res.data;
}

/**
 * Demande au backend de rafraîchir le statut auprès de MyBlueLink
 * puis retourne le nouveau status.
 *
 * POST /vehicles/{vehicleId}/status/refresh
 */
export async function refreshVehicleStatus(
  vehicleId: number,
): Promise<VehicleStatus> {
  const res = await client.post<VehicleStatus>(
    `/vehicles/${vehicleId}/status/refresh`,
  );
  return res.data;
}
