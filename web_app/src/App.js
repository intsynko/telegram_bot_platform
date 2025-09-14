import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import ScenarioEditPage from './pages/ScenarioEdit';
import ScenariosPage from './pages/ScenariosPage';
import BotsListPage from './pages/BotsListPage';
import UsersPage from './pages/UsersPage';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';
import { BASE_URL } from "./config";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`${BASE_URL}/api/users/auth/user/`, {
      credentials: 'include',
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && data.email) setUser(data);
      });
  }, []);

  return (
    <Router>
      <Header user={user} setUser={setUser} />
      <Routes>
        <Route path="/" element={<LandingPage setUser={setUser} />} />
        <Route path="/scenarios" element={<ScenarioEditPage />} />
        <Route path="/scenarios/templates" element={<ScenariosPage user={user} />} />
        <Route path="/bots" element={<BotsListPage user={user} />} />
        <Route path="/users" element={<UsersPage />} />
      </Routes>
      <ToastContainer position="top-right" autoClose={2500} />
    </Router>
  );
}

export default App;
