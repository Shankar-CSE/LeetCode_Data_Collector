import axios from "axios";

const API = axios.create({ baseURL: "/api" });

export function fetchAnalytics(groupBy, metric) {
  return API.get("/analytics", { params: { group_by: groupBy, metric } }).then(
    (r) => r.data
  );
}

export function fetchSummary() {
  return API.get("/summary").then((r) => r.data);
}

export function fetchLeaderboard() {
  return API.get("/leaderboard").then((r) => r.data);
}

export function fetchScatter() {
  return API.get("/scatter").then((r) => r.data);
}
