import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import ScenariosPage from './pages/ScenariosPage';
import BotsListPage from './pages/BotsListPage';
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/users/auth/user/', {
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
        <Route path="/" element={<LandingPage />} />
        <Route path="/scenarios" element={<ScenariosPage />} />
        <Route path="/bots" element={<BotsListPage user={user} />} />
      </Routes>
    </Router>
  );
}

export default App;
