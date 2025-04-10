import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // Replace with your backend_test URL
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;