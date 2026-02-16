// frontend-react/src/api/client.ts
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Export nommé pour pouvoir faire `import { client } from "./client"`
export const client = api;

// Optionnel mais pratique : on garde aussi un export par défaut
export default api;
