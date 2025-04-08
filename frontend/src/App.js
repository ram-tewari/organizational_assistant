import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LoginSignup from "./pages/LoginSignup";
import Dashboard from "./pages/Dashboard";
import Tasks from "./pages/Tasks";
import Calendar from "./pages/Calendar";
import Notes from "./pages/Notes";
import HabitsGoals from "./pages/HabitsGoals";
import Pomodoro from "./pages/Pomodoro";
import StudyRecommendations from "./pages/StudyRecommendations";
import Files from "./pages/Files";
import Settings from "./pages/Settings";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginSignup />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/notes" element={<Notes />} />
        <Route path="/habits-goals" element={<HabitsGoals />} />
        <Route path="/pomodoro" element={<Pomodoro />} />
        <Route path="/study-recommendations" element={<StudyRecommendations />} />
        <Route path="/files" element={<Files />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<h1>404 - Page Not Found</h1>} />
      </Routes>
    </Router>
  );
};

export default App;