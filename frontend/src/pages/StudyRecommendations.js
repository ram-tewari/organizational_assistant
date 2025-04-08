import React from "react";
import { Link } from "react-router-dom";

const StudyRecommendations = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Study Recommendations</h1>
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
          <h2 className="text-lg font-bold mb-4">Productivity Analysis</h2>
          <p>Productivity chart will go here.</p>
        </div>
      </main>
    </div>
  );
};

export default StudyRecommendations;