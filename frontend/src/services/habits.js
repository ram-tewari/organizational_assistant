import axios from "axios";

const API_URL = "http://localhost:8000/api/habits-goals/habits"; // Update with your backend_test URL

export const fetchHabits = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const createHabit = async (habit) => {
  const response = await axios.post(API_URL, habit);
  return response.data;
};

export const completeHabit = async (habitId) => {
  const response = await axios.post(`${API_URL}/complete`, { habit_id: habitId });
  return response.data;
};