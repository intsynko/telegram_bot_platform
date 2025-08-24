import React, { useState, useEffect } from 'react';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function AuthModal({ open, onClose, setUser }) {
  const [tab, setTab] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [csrfToken, setCsrfToken] = useState('');

  useEffect(() => {
    if (open) {
      fetch('http://79.174.93.201:8000/api/csrf/', {
        credentials: 'include',
      }).then(() => {
        const token = getCookie('csrftoken');
        setCsrfToken(token || '');
      });
    }
  }, [open]);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const url = tab === 'login'
        ? 'http://79.174.93.201:8000/api/users/auth/login/'
        : 'http://79.174.93.201:8000/api/users/auth/register/';
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });
      const data = await resp.json();
      if (!resp.ok) {
        setError(data.error || 'Ошибка авторизации/регистрации');
        setLoading(false);
        return;
      }
      setUser(data); // data должен содержать email
      setLoading(false);
      onClose();
    } catch (err) {
      setError('Ошибка сети');
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 340, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
        <button onClick={onClose} style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} title="Закрыть">×</button>
        <div style={{ display: 'flex', marginBottom: 24 }}>
          <button onClick={() => { setTab('login'); setError(''); }} style={{ flex: 1, padding: 8, borderBottom: tab === 'login' ? '2px solid #1890ff' : '2px solid #eee', background: 'none', borderTop: 'none', borderLeft: 'none', borderRight: 'none', fontWeight: tab === 'login' ? 600 : 400, color: tab === 'login' ? '#1890ff' : '#888', cursor: 'pointer' }}>Вход</button>
          <button onClick={() => { setTab('register'); setError(''); }} style={{ flex: 1, padding: 8, borderBottom: tab === 'register' ? '2px solid #1890ff' : '2px solid #eee', background: 'none', borderTop: 'none', borderLeft: 'none', borderRight: 'none', fontWeight: tab === 'register' ? 600 : 400, color: tab === 'register' ? '#1890ff' : '#888', cursor: 'pointer' }}>Регистрация</button>
        </div>
        <form onSubmit={handleSubmit}>
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            style={{ width: '100%', marginBottom: 12, padding: 8, borderRadius: 6, border: '1px solid #ccc' }}
            required
            autoComplete="username"
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={{ width: '100%', marginBottom: 18, padding: 8, borderRadius: 6, border: '1px solid #ccc' }}
            required
            autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
          />
          {error && <div style={{ color: '#f5222d', marginBottom: 10 }}>{error}</div>}
          <button type="submit" disabled={loading} style={{ width: '100%', padding: 10, borderRadius: 6, background: '#1890ff', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
            {loading ? '...' : (tab === 'login' ? 'Войти' : 'Зарегистрироваться')}
          </button>
        </form>
      </div>
    </div>
  );
}
