import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import BotsPage from './pages/BotsPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/bots" element={<BotsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
