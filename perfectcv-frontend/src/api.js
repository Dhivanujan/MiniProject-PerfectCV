// src/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000", // Flask backend URL (updated to port 8000)
  withCredentials: true,             // ✅ Important for session
});

export default api;
