// src/pages/Dashboard.js
import React from "react";
import { Link } from "react-router-dom";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Dashboard</h1>
          <nav>
            <Link to="/tasks" className="mr-4">
              Tasks
            </Link>
            <Link to="/calendar" className="mr-4">
              Calendar
            </Link>
            <Link to="/notes">Notes</Link>
          </nav>
        </div>
      </header>
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-bold mb-4">Upcoming Tasks</h2>
            <ul>
              <li className="mb-2">Task 1</li>
              <li className="mb-2">Task 2</li>
            </ul>
            <button className="mt-4 bg-blue-500 text-white p-2 rounded">
              Add Task
            </button>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-bold mb-4">Habit Tracker</h2>
            <ul>
              <li className="mb-2">Habit 1</li>
              <li className="mb-2">Habit 2</li>
            </ul>
            <button className="mt-4 bg-blue-500 text-white p-2 rounded">
              Add Habit
            </button>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-bold mb-4">Goals Overview</h2>
            <ul>
              <li className="mb-2">Goal 1</li>
              <li className="mb-2">Goal 2</li>
            </ul>
            <button className="mt-4 bg-blue-500 text-white p-2 rounded">
              Add Goal
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;