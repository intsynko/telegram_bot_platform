import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import ScenariosPage from './pages/ScenariosPage';
import BotsListPage from './pages/BotsListPage';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
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
