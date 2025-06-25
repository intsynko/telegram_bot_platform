import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import BotsPage from './pages/BotsPage';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  return (
    <Router>
      <Header user={user} setUser={setUser} />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/bots" element={<BotsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
