import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchTasks, createTask, deleteTask } from "../services/tasks";

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    dueDate: "",
    priority: "medium",
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await fetchTasks();
      setTasks(data);
    } catch (error) {
      console.error("Failed to load tasks:", error);
    }
  };

  const handleCreateTask = async () => {
    try {
      const task = await createTask(newTask);
      setTasks([...tasks, task]);
      setNewTask({ title: "", description: "", dueDate: "", priority: "medium" });
    } catch (error) {
      console.error("Failed to create task:", error);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await deleteTask(taskId);
      setTasks(tasks.filter((task) => task.id !== taskId));
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Tasks</h1>
          <nav>
            <Link to="/dashboard" className="mr-4">
              Dashboard
            </Link>
            <Link to="/calendar">Calendar</Link>
          </nav>
        </div>
      </header>
      <main className="container mx-auto px-6 py-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold mb-4">Task List</h2>
          <ul>
            {tasks.map((task) => (
              <li key={task.id} className="mb-2 flex justify-between items-center">
                <div>
                  <h3 className="font-bold">{task.title}</h3>
                  <p>{task.description}</p>
                  <p>Due: {new Date(task.dueDate).toLocaleDateString()}</p>
                  <p>Priority: {task.priority}</p>
                </div>
                <button
                  onClick={() => handleDeleteTask(task.id)}
                  className="bg-red-500 text-white p-2 rounded"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
          <div className="mt-4">
            <h3 className="text-lg font-bold mb-2">Add New Task</h3>
            <input
              type="text"
              placeholder="Title"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              className="w-full p-2 mb-2 border rounded"
            />
            <input
              type="text"
              placeholder="Description"
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              className="w-full p-2 mb-2 border rounded"
            />
            <input
              type="date"
              value={newTask.dueDate}
              onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })}
              className="w-full p-2 mb-2 border rounded"
            />
            <select
              value={newTask.priority}
              onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
              className="w-full p-2 mb-2 border rounded"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <button
              onClick={handleCreateTask}
              className="bg-blue-500 text-white p-2 rounded"
            >
              Add Task
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Tasks;