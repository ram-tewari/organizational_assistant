import React from "react";
import { Link } from "react-router-dom";

const Notes = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Notes</h1>
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
          <h2 className="text-lg font-bold mb-4">Note List</h2>
          <ul>
            <li className="mb-2">Note 1</li>
            <li className="mb-2">Note 2</li>
          </ul>
          <button className="mt-4 bg-blue-500 text-white p-2 rounded">
            Add Note
          </button>
        </div>
      </main>
    </div>
  );
};

export default Notes;