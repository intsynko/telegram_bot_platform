import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AuthModal from './AuthModal';
import { BASE_URL } from "../config";

export default function Header({ user, setUser }) {
  const [showAuth, setShowAuth] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef();

  // Закрытие меню по клику вне
  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [menuOpen]);

  // Логаут
  const handleLogout = async () => {
    const csrfToken = getCookie('csrftoken');
    await fetch(`${BASE_URL}/api/users/auth/logout/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRFToken': csrfToken,
      },
    });
    // Проверяем, реально ли разлогинились
    const res = await fetch(`${BASE_URL}/api/users/auth/user/`, {
      credentials: 'include',
    });
    if (!res.ok) {
      setUser(null);
    } else {
      // Если вдруг user всё ещё есть — обновить user
      const data = await res.json();
      setUser(data);
    }
    setMenuOpen(false);
  };

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

  return (
    <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 32px', background: '#f7f7f7', borderBottom: '1px solid #eee', position: 'sticky', top: 0, zIndex: 10 }}>
      <div style={{ fontWeight: 'bold', fontSize: 20 }}>
        <Link to="/" style={{ textDecoration: 'none', color: '#222' }}>TG Bot Master</Link>
      </div>
      <nav style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {user ? (
          <>
            {/* <Link to="/scenarios" style={{ textDecoration: 'none', color: '#1890ff', fontWeight: 500 }}>Сценарии</Link> */}
            <Link to="/scenarios/templates" style={{ textDecoration: 'none', color: '#1890ff', fontWeight: 500 }}>Сценарии</Link>
            <Link to="/bots" style={{ textDecoration: 'none', color: '#1890ff', fontWeight: 500 }}>Боты</Link>
            <div style={{ position: 'relative', marginLeft: 16 }}>
              <button
                onClick={() => setMenuOpen(v => !v)}
                style={{
                  background: 'none', border: 'none', color: '#222', fontWeight: 500, cursor: 'pointer', fontSize: 16, padding: 0
                }}
              >
                {user.email} ▼
              </button>
              {menuOpen && (
                <div ref={menuRef} style={{
                  position: 'absolute', right: 0, top: '120%', background: '#fff', border: '1px solid #eee', borderRadius: 8, boxShadow: '0 4px 16px rgba(0,0,0,0.08)', minWidth: 180, zIndex: 100
                }}>
                  <button
                    style={{ width: '100%', padding: '10px 16px', border: 'none', background: 'none', textAlign: 'left', cursor: 'pointer', fontSize: 15 }}
                    onClick={() => { setMenuOpen(false); alert('Настройки аккаунта (заглушка)'); }}
                  >
                    ⚙ Настройки аккаунта
                  </button>
                  <button
                    style={{ width: '100%', padding: '10px 16px', border: 'none', background: 'none', textAlign: 'left', color: '#f5222d', cursor: 'pointer', fontSize: 15 }}
                    onClick={handleLogout}
                  >
                    Выйти
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <button onClick={() => setShowAuth(true)} style={{ marginLeft: 16, padding: '6px 18px', borderRadius: 6, border: '1px solid #1890ff', background: '#fff', color: '#1890ff', cursor: 'pointer' }}>Войти</button>
        )}
      </nav>
      <AuthModal open={showAuth} onClose={() => setShowAuth(false)} setUser={setUser} />
    </header>
  );
}
