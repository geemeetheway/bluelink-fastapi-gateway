// frontend-react/src/App.tsx

import { useEffect, useState } from "react";
import {
  listVehicles,
  getLatestVehicleStatus,
  refreshVehicleStatus,
} from "./api/vehicles";
import type { Vehicle, VehicleStatus } from "./types";
import "./App.css"; // facultatif si tu as déjà quelque chose, sinon à ignorer

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    const d = new Date(value);
    return d.toLocaleString();
  } catch {
    return value;
  }
}

function formatBoolean(value: boolean | null | undefined): string {
  if (value === true) return "Oui";
  if (value === false) return "Non";
  return "—";
}

function formatMinutes(value: number | null | undefined): string {
  if (value == null) return "—";
  if (value < 60) return `${value} min`;
  const hours = Math.floor(value / 60);
  const minutes = value % 60;
  if (minutes === 0) return `${hours} h`;
  return `${hours} h ${minutes} min`;
}

function App() {
  const [vehiclesState, setVehiclesState] = useState<
    AsyncState<Vehicle[]>
  >({
    data: null,
    loading: true,
    error: null,
  });

  const [selectedVehicleId, setSelectedVehicleId] = useState<number | null>(
    null,
  );

  const [statusState, setStatusState] = useState<
    AsyncState<VehicleStatus | null>
  >({
    data: null,
    loading: false,
    error: null,
  });

  const [refreshing, setRefreshing] = useState(false);

  // 1) Chargement de la liste des véhicules au montage
  useEffect(() => {
    let cancelled = false;

    async function loadVehicles() {
      setVehiclesState({
        data: null,
        loading: true,
        error: null,
      });

      try {
        const vehicles = await listVehicles();
        if (cancelled) return;

        setVehiclesState({
          data: vehicles,
          loading: false,
          error: null,
        });

        // Si aucun véhicule sélectionné, prendre le premier
        if (vehicles.length > 0 && selectedVehicleId == null) {
          setSelectedVehicleId(vehicles[0].id);
        }
      } catch (error: any) {
        if (cancelled) return;

        setVehiclesState({
          data: null,
          loading: false,
          error:
            error?.message ??
            "Erreur lors du chargement des véhicules.",
        });
      }
    }

    loadVehicles();

    return () => {
      cancelled = true;
    };
  }, [selectedVehicleId]);

  // 2) Chargement du dernier status lorsque le véhicule sélectionné change
  useEffect(() => {
    let cancelled = false;

    async function loadStatus(vehicleId: number) {
      setStatusState({
        data: null,
        loading: true,
        error: null,
      });

      try {
        const status = await getLatestVehicleStatus(vehicleId);
        if (cancelled) return;

        setStatusState({
          data: status,
          loading: false,
          error: null,
        });
      } catch (error: any) {
        if (cancelled) return;

        setStatusState({
          data: null,
          loading: false,
          error:
            error?.message ??
            "Erreur lors du chargement du statut du véhicule.",
        });
      }
    }

    if (selectedVehicleId != null) {
      loadStatus(selectedVehicleId);
    } else {
      setStatusState({
        data: null,
        loading: false,
        error: null,
      });
    }

    return () => {
      cancelled = true;
    };
  }, [selectedVehicleId]);

  async function handleRefreshClick() {
    if (selectedVehicleId == null) return;

    setRefreshing(true);
    setStatusState((prev) => ({
      ...prev,
      error: null,
    }));

    try {
      const status = await refreshVehicleStatus(selectedVehicleId);
      setStatusState({
        data: status,
        loading: false,
        error: null,
      });
    } catch (error: any) {
      setStatusState((prev) => ({
        ...prev,
        error:
          error?.message ??
          "Erreur lors de la demande de rafraîchissement.",
      }));
    } finally {
      setRefreshing(false);
    }
  }

  const vehicles = vehiclesState.data ?? [];
  const selectedVehicle = vehicles.find(
    (v) => v.id === selectedVehicleId,
  );

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#0f172a",
        color: "#e5e7eb",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        padding: "2rem",
      }}
    >
      <div
        style={{
          maxWidth: "960px",
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          gap: "1.5rem",
        }}
      >
        <header>
          <h1 style={{ fontSize: "1.75rem", fontWeight: 700 }}>
            Bluelink FastAPI Gateway – Dashboard
          </h1>
          <p style={{ color: "#9ca3af", marginTop: "0.25rem" }}>
            Visualisation du véhicule et rafraîchissement du statut
            via MyBlueLink.
          </p>
        </header>

        {/* Bloc sélection du véhicule */}
        <section
          style={{
            backgroundColor: "#020617",
            borderRadius: "0.75rem",
            padding: "1rem 1.25rem",
            border: "1px solid #1f2937",
          }}
        >
          <h2
            style={{
              fontSize: "1.1rem",
              fontWeight: 600,
              marginBottom: "0.75rem",
            }}
          >
            Véhicule
          </h2>

          {vehiclesState.loading && <p>Chargement des véhicules…</p>}

          {vehiclesState.error && (
            <p style={{ color: "#fca5a5" }}>{vehiclesState.error}</p>
          )}

          {!vehiclesState.loading && vehicles.length === 0 && (
            <p>Aucun véhicule trouvé.</p>
          )}

          {vehicles.length > 0 && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
              }}
            >
              <label
                htmlFor="vehicle-select"
                style={{
                  fontSize: "0.9rem",
                  color: "#9ca3af",
                }}
              >
                Sélectionner un véhicule :
              </label>
              <select
                id="vehicle-select"
                value={selectedVehicleId ?? ""}
                onChange={(e) =>
                  setSelectedVehicleId(
                    e.target.value
                      ? Number(e.target.value)
                      : null,
                  )
                }
                style={{
                  backgroundColor: "#020617",
                  color: "#e5e7eb",
                  borderRadius: "0.5rem",
                  padding: "0.5rem 0.75rem",
                  border: "1px solid #374151",
                  maxWidth: "320px",
                }}
              >
                {vehicles.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.nickname || v.vin || v.external_id || `#${v.id}`}
                  </option>
                ))}
              </select>

              {selectedVehicle && (
                <div
                  style={{
                    marginTop: "0.75rem",
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: "0.5rem",
                    fontSize: "0.9rem",
                  }}
                >
                  <div>
                    <span style={{ color: "#9ca3af" }}>VIN :</span>{" "}
                    <span>{selectedVehicle.vin ?? "—"}</span>
                  </div>
                  <div>
                    <span style={{ color: "#9ca3af" }}>Nickname :</span>{" "}
                    <span>{selectedVehicle.nickname ?? "—"}</span>
                  </div>
                  <div>
                    <span style={{ color: "#9ca3af" }}>
                      External ID :
                    </span>{" "}
                    <span>{selectedVehicle.external_id ?? "—"}</span>
                  </div>
                  <div>
                    <span style={{ color: "#9ca3af" }}>Actif :</span>{" "}
                    <span>
                      {selectedVehicle.is_active ? "Oui" : "Non"}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: "#9ca3af" }}>
                      Créé le :
                    </span>{" "}
                    <span>
                      {formatDateTime(selectedVehicle.created_at)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Bloc statut du véhicule */}
        <section
          style={{
            backgroundColor: "#020617",
            borderRadius: "0.75rem",
            padding: "1rem 1.25rem",
            border: "1px solid #1f2937",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: "1rem",
              alignItems: "center",
              marginBottom: "0.75rem",
            }}
          >
            <h2
              style={{
                fontSize: "1.1rem",
                fontWeight: 600,
              }}
            >
              Statut du véhicule
            </h2>

            <button
              onClick={handleRefreshClick}
              disabled={
                selectedVehicleId == null || refreshing
              }
              style={{
                backgroundColor: refreshing
                  ? "#4b5563"
                  : "#2563eb",
                border: "none",
                color: "#e5e7eb",
                padding: "0.5rem 0.9rem",
                borderRadius: "9999px",
                fontSize: "0.9rem",
                cursor:
                  selectedVehicleId == null || refreshing
                    ? "not-allowed"
                    : "pointer",
                opacity:
                  selectedVehicleId == null || refreshing
                    ? 0.7
                    : 1,
              }}
            >
              {refreshing
                ? "Rafraîchissement…"
                : "Rafraîchir via MyBlueLink"}
            </button>
          </div>

          {statusState.loading && (
            <p>Chargement du statut…</p>
          )}

          {statusState.error && (
            <p style={{ color: "#fca5a5" }}>{statusState.error}</p>
          )}

          {!statusState.loading &&
            !statusState.error &&
            !statusState.data && (
              <p>
                Aucun statut disponible pour ce véhicule (encore
                jamais rafraîchi ?).
              </p>
            )}

          {statusState.data && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(180px, 1fr))",
                gap: "0.75rem",
                fontSize: "0.9rem",
              }}
            >
              <div>
                <span style={{ color: "#9ca3af" }}>
                  Dernière mise à jour :
                </span>{" "}
                <span>
                  {formatDateTime(statusState.data.timestamp)}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  Batterie :
                </span>{" "}
                <span>
                  {statusState.data.battery_level != null
                    ? `${statusState.data.battery_level}%`
                    : "—"}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  Branché :
                </span>{" "}
                <span>
                  {formatBoolean(statusState.data.is_plugged)}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  En charge :
                </span>{" "}
                <span>
                  {formatBoolean(statusState.data.is_charging)}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  Autonomie totale :
                </span>{" "}
                <span>
                  {statusState.data.total_range_km != null
                    ? `${statusState.data.total_range_km} km`
                    : "—"}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  Temps restant :
                </span>{" "}
                <span>
                  {formatMinutes(
                    statusState.data
                      .remaining_charge_minutes,
                  )}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  Latitude :
                </span>{" "}
                <span>
                  {statusState.data.latitude ?? "—"}
                </span>
              </div>

              <div>
                <span style={{ color: "#9ca3af" }}>
                  Longitude :
                </span>{" "}
                <span>
                  {statusState.data.longitude ?? "—"}
                </span>
              </div>

              {statusState.data.latitude != null &&
                statusState.data.longitude != null && (
                  <div style={{ gridColumn: "1 / -1" }}>
                    <a
                      href={`https://www.google.com/maps?q=${statusState.data.latitude},${statusState.data.longitude}`}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        color: "#60a5fa",
                        textDecoration: "underline",
                      }}
                    >
                      Ouvrir dans Google Maps
                    </a>
                  </div>
                )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;
