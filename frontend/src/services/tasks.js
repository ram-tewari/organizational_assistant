import axios from "axios";

const API_URL = "http://localhost:8000/api/tasks"; // Update with your backend_test URL

export const fetchTasks = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const createTask = async (task) => {
  const response = await axios.post(API_URL, task);
  return response.data;
};

export const updateTask = async (taskId, task) => {
  const response = await axios.put(`${API_URL}/${taskId}`, task);
  return response.data;
};

export const deleteTask = async (taskId) => {
  const response = await axios.delete(`${API_URL}/${taskId}`);
  return response.data;
};