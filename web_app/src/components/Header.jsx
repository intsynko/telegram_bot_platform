import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import AuthModal from './AuthModal';

export default function Header({ user, setUser }) {
  const [showAuth, setShowAuth] = useState(false);

  return (
    <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 32px', background: '#f7f7f7', borderBottom: '1px solid #eee', position: 'sticky', top: 0, zIndex: 10 }}>
      <div style={{ fontWeight: 'bold', fontSize: 20 }}>
        <Link to="/" style={{ textDecoration: 'none', color: '#222' }}>TG Bot Master</Link>
      </div>
      <nav style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {user ? (
          <>
            <Link to="/scenarios" style={{ textDecoration: 'none', color: '#1890ff', fontWeight: 500 }}>Сценарии</Link>
            <Link to="/bots" style={{ textDecoration: 'none', color: '#1890ff', fontWeight: 500 }}>Боты</Link>
            <span style={{ marginLeft: 16 }}>{user.email}</span>
          </>
        ) : (
          <button onClick={() => setShowAuth(true)} style={{ marginLeft: 16, padding: '6px 18px', borderRadius: 6, border: '1px solid #1890ff', background: '#fff', color: '#1890ff', cursor: 'pointer' }}>Войти</button>
        )}
      </nav>
      <AuthModal open={showAuth} onClose={() => setShowAuth(false)} setUser={setUser} />
    </header>
  );
}
