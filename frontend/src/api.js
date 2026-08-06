import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE });

export const getTopics = () => api.get("/topics").then((r) => r.data);

export const startSession = (payload) =>
  api.post("/session/start", payload).then((r) => r.data);

export const submitResponse = (sessionId, payload) =>
  api.post(`/session/${sessionId}/submit`, payload).then((r) => r.data);
