import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHabits, createHabit, completeHabit } from "../services/habits";

const HabitsGoals = () => {
  const [habits, setHabits] = useState([]);
  const [newHabit, setNewHabit] = useState({ title: "", description: "" });

  useEffect(() => {
    loadHabits();
  }, []);

  const loadHabits = async () => {
    try {
      const data = await fetchHabits();
      setHabits(data);
    } catch (error) {
      console.error("Failed to load habits:", error);
    }
  };

  const handleCreateHabit = async () => {
    try {
      const habit = await createHabit(newHabit);
      setHabits([...habits, habit]);
      setNewHabit({ title: "", description: "" });
    } catch (error) {
      console.error("Failed to create habit:", error);
    }
  };

  const handleCompleteHabit = async (habitId) => {
    try {
      const updatedHabit = await completeHabit(habitId);
      setHabits(habits.map((habit) => (habit.id === habitId ? updatedHabit : habit)));
    } catch (error) {
      console.error("Failed to complete habit:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Habits & Goals</h1>
          <nav>
            <Link to="/dashboard" className="mr-4">
              Dashboard
            </Link>
            <Link to="/tasks">Tasks</Link>
          </nav>
        </div>
      </header>
      <main className="container mx-auto px-6 py-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold mb-4">Habits</h2>
          <ul>
            {habits.map((habit) => (
              <li key={habit.id} className="mb-2 flex justify-between items-center">
                <div>
                  <h3 className="font-bold">{habit.title}</h3>
                  <p>{habit.description}</p>
                  <p>Streak: {habit.streak}</p>
                </div>
                <button
                  onClick={() => handleCompleteHabit(habit.id)}
                  className="bg-green-500 text-white p-2 rounded"
                >
                  Complete
                </button>
              </li>
            ))}
          </ul>
          <div className="mt-4">
            <h3 className="text-lg font-bold mb-2">Add New Habit</h3>
            <input
              type="text"
              placeholder="Title"
              value={newHabit.title}
              onChange={(e) => setNewHabit({ ...newHabit, title: e.target.value })}
              className="w-full p-2 mb-2 border rounded"
            />
            <input
              type="text"
              placeholder="Description"
              value={newHabit.description}
              onChange={(e) => setNewHabit({ ...newHabit, description: e.target.value })}
              className="w-full p-2 mb-2 border rounded"
            />
            <button
              onClick={handleCreateHabit}
              className="bg-blue-500 text-white p-2 rounded"
            >
              Add Habit
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HabitsGoals;