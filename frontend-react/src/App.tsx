import { useEffect, useState } from "react";
import api from "./api/client";
import type {
  Vehicle,
  VehicleStatus,
  CreateVehicleDto,
  CreateStatusDto,
} from "./types";

function App() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [latestStatus, setLatestStatus] = useState<VehicleStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [newVehicle, setNewVehicle] = useState<CreateVehicleDto>({
    external_id: "",
    name: "",
    vin: "",
  });

  const [newStatus, setNewStatus] = useState<CreateStatusDto>({
    battery_level: undefined,
    doors_locked: true,
    odometer_km: undefined,
  });

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get<Vehicle[]>("/vehicles");
      setVehicles(res.data);
    } catch (e: any) {
      console.error(e);
      setError("Impossible de charger les véhicules.");
    } finally {
      setLoading(false);
    }
  };

  const fetchLatestStatus = async (vehicle: Vehicle) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get<VehicleStatus>(
        `/vehicles/${vehicle.id}/status/latest`
      );
      setLatestStatus(res.data);
    } catch (e: any) {
      console.error(e);
      setLatestStatus(null);
      setError(
        "Aucun statut trouvé pour ce véhicule ou erreur lors du chargement."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSelectVehicle = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle);
    fetchLatestStatus(vehicle);
  };

  const handleCreateVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const res = await api.post<Vehicle>("/vehicles", newVehicle);
      setVehicles((prev) => [...prev, res.data]);
      setNewVehicle({ external_id: "", name: "", vin: "" });
    } catch (e: any) {
      console.error(e);
      setError("Erreur lors de la création du véhicule.");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedVehicle) return;

    try {
      setLoading(true);
      setError(null);
      const payload: CreateStatusDto = {
        doors_locked: newStatus.doors_locked,
        battery_level:
          newStatus.battery_level === undefined
            ? undefined
            : Number(newStatus.battery_level),
        odometer_km:
          newStatus.odometer_km === undefined
            ? undefined
            : Number(newStatus.odometer_km),
      };

      const res = await api.post<VehicleStatus>(
        `/vehicles/${selectedVehicle.id}/status`,
        payload
      );
      setLatestStatus(res.data);
      setNewStatus({
        battery_level: undefined,
        doors_locked: true,
        odometer_km: undefined,
      });
    } catch (e: any) {
      console.error(e);
      setError("Erreur lors de la création du statut.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 900, margin: "0 auto", padding: 16 }}>
      <h1>Bluelink Gateway – Tableau de bord</h1>
      <p>
        Démonstration React/TypeScript consommant l&apos;API FastAPI (véhicules
        & statuts).
      </p>

      {loading && <p>⏳ Chargement…</p>}
      {error && <p style={{ color: "red" }}>⚠ {error}</p>}

      <hr />

      <section>
        <h2>Créer un véhicule</h2>
        <form onSubmit={handleCreateVehicle}>
          <div>
            <label>
              External ID&nbsp;
              <input
                type="text"
                value={newVehicle.external_id}
                onChange={(e) =>
                  setNewVehicle({ ...newVehicle, external_id: e.target.value })
                }
                required
              />
            </label>
          </div>
          <div>
            <label>
              Nom&nbsp;
              <input
                type="text"
                value={newVehicle.name}
                onChange={(e) =>
                  setNewVehicle({ ...newVehicle, name: e.target.value })
                }
                required
              />
            </label>
          </div>
          <div>
            <label>
              VIN&nbsp;
              <input
                type="text"
                value={newVehicle.vin}
                onChange={(e) =>
                  setNewVehicle({ ...newVehicle, vin: e.target.value })
                }
                required
              />
            </label>
          </div>
          <button type="submit" disabled={loading}>
            Ajouter le véhicule
          </button>
        </form>
      </section>

      <hr />

      <section>
        <h2>Liste des véhicules</h2>
        <button onClick={fetchVehicles} disabled={loading}>
          Rafraîchir
        </button>
        {vehicles.length === 0 ? (
          <p>Aucun véhicule pour le moment.</p>
        ) : (
          <ul>
            {vehicles.map((v) => (
              <li key={v.id}>
                <button type="button" onClick={() => handleSelectVehicle(v)}>
                  {v.name} ({v.vin})
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <hr />

      {selectedVehicle && (
        <section>
          <h2>Véhicule sélectionné</h2>
          <p>
            <strong>{selectedVehicle.name}</strong> — VIN :{" "}
            {selectedVehicle.vin}
          </p>

          <h3>Dernier statut connu</h3>
          {latestStatus ? (
            <ul>
              <li>
                Horodatage : {new Date(latestStatus.timestamp).toLocaleString()}
              </li>
              <li>
                Batterie :{" "}
                {latestStatus.battery_level != null
                  ? `${latestStatus.battery_level}%`
                  : "N/D"}
              </li>
              <li>
                Portes verrouillées :{" "}
                {latestStatus.doors_locked ? "Oui" : "Non"}
              </li>
              <li>
                Odomètre :{" "}
                {latestStatus.odometer_km != null
                  ? `${latestStatus.odometer_km} km`
                  : "N/D"}
              </li>
            </ul>
          ) : (
            <p>Aucun statut disponible.</p>
          )}

          <h3>Ajouter un statut</h3>
          <form onSubmit={handleCreateStatus}>
            <div>
              <label>
                Batterie (%)&nbsp;
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={
                    newStatus.battery_level !== undefined
                      ? newStatus.battery_level
                      : ""
                  }
                  onChange={(e) =>
                    setNewStatus({
                      ...newStatus,
                      battery_level:
                        e.target.value === "" ? undefined : Number(e.target.value),
                    })
                  }
                />
              </label>
            </div>
            <div>
              <label>
                Odomètre (km)&nbsp;
                <input
                  type="number"
                  min={0}
                  value={
                    newStatus.odometer_km !== undefined
                      ? newStatus.odometer_km
                      : ""
                  }
                  onChange={(e) =>
                    setNewStatus({
                      ...newStatus,
                      odometer_km:
                        e.target.value === "" ? undefined : Number(e.target.value),
                    })
                  }
                />
              </label>
            </div>
            <div>
              <label>
                Portes verrouillées&nbsp;
                <input
                  type="checkbox"
                  checked={newStatus.doors_locked}
                  onChange={(e) =>
                    setNewStatus({
                      ...newStatus,
                      doors_locked: e.target.checked,
                    })
                  }
                />
              </label>
            </div>
            <button type="submit" disabled={loading}>
              Enregistrer le statut
            </button>
          </form>
        </section>
      )}
    </div>
  );
}

export default App;
