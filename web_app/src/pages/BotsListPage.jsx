import React, { useEffect, useState } from 'react';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Модалка для создания/редактирования бота
function BotModal({ open, onClose, onSave, bot, scenarios, loading }) {
  const [name, setName] = useState(bot?.name || '');
  const [token, setToken] = useState(bot?.token || '');
  const [description, setDescription] = useState(bot?.description || '');
  const [scenario, setScenario] = useState(bot?.scenario?.id || '');

  useEffect(() => {
    setName(bot?.name || '');
    setToken(bot?.token || '');
    setDescription(bot?.description || '');
    setScenario(bot?.scenario?.id || '');
  }, [bot, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      name,
      token,
      description,
      scenario,
    });
  };

  if (!open) return null;
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 340, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
        <button onClick={onClose} type="button" style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} title="Закрыть">×</button>
        <h3>{bot ? 'Редактировать бота' : 'Создать бота'}</h3>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Имя" required style={{ width: '100%', marginBottom: 12, padding: 8 }} />
        <input value={token} onChange={e => setToken(e.target.value)} placeholder="Токен" required style={{ width: '100%', marginBottom: 12, padding: 8 }} />
        <textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Описание" style={{ width: '100%', marginBottom: 12, padding: 8 }} />
        <select value={scenario} onChange={e => setScenario(e.target.value)} required style={{ width: '100%', marginBottom: 18, padding: 8 }}>
          <option value="">Выберите сценарий</option>
          {scenarios.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <button type="submit" disabled={loading} style={{ width: '100%', padding: 10, borderRadius: 6, background: '#1890ff', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
          {loading ? '...' : (bot ? 'Сохранить' : 'Создать')}
        </button>
      </form>
    </div>
  );
}

export default function BotsListPage({ user }) {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalBot, setModalBot] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [scenarios, setScenarios] = useState([]);
  const [runningBots, setRunningBots] = useState(new Set());

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    fetch('http://localhost:8000/api/bots/', {
      credentials: 'include',
    })
      .then(res => res.json())
      .then(data => {
        setBots(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Ошибка загрузки ботов');
        setLoading(false);
      });
  }, [user]);

  const openModal = async (bot = null) => {
    // Получить сценарии
    const resp = await fetch('http://localhost:8000/api/scenarios/', { credentials: 'include' });
    const data = await resp.json();
    setScenarios(data);
    setModalBot(bot);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить бота?')) return;
    const csrfToken = getCookie('csrftoken');
    await fetch(`http://localhost:8000/api/bots/${id}/`, {
      method: 'DELETE',
      credentials: 'include',
      headers: { 'X-CSRFToken': csrfToken },
    });
    setBots(bots => bots.filter(b => b.id !== id));
  };

  const handleRunBot = async (botId) => {
    const csrfToken = getCookie('csrftoken');
    setRunningBots(prev => new Set([...prev, botId]));
    
    try {
      const response = await fetch(`http://localhost:8000/api/bots/${botId}/run/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': csrfToken },
      });
      
      if (response.ok) {
        // Обновляем состояние бота в списке
        setBots(prevBots => 
          prevBots.map(bot => 
            bot.id === botId ? { ...bot, is_running: true } : bot
          )
        );
      } else {
        alert('Ошибка запуска бота');
      }
    } catch (error) {
      alert('Ошибка запуска бота');
    } finally {
      setRunningBots(prev => {
        const newSet = new Set(prev);
        newSet.delete(botId);
        return newSet;
      });
    }
  };

  const handleStopBot = async (botId) => {
    const csrfToken = getCookie('csrftoken');
    setRunningBots(prev => new Set([...prev, botId]));
    
    try {
      const response = await fetch(`http://localhost:8000/api/bots/${botId}/stop/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': csrfToken },
      });
      
      if (response.ok) {
        // Обновляем состояние бота в списке
        setBots(prevBots => 
          prevBots.map(bot => 
            bot.id === botId ? { ...bot, is_running: false } : bot
          )
        );
      } else {
        alert('Ошибка остановки бота');
      }
    } catch (error) {
      alert('Ошибка остановки бота');
    } finally {
      setRunningBots(prev => {
        const newSet = new Set(prev);
        newSet.delete(botId);
        return newSet;
      });
    }
  };

  const handleSave = async (botData) => {
    setModalLoading(true);
    const csrfToken = getCookie('csrftoken');
    const isEdit = !!modalBot;
    const url = isEdit
      ? `http://localhost:8000/api/bots/${modalBot.id}/`
      : 'http://localhost:8000/api/bots/';
    const method = isEdit ? 'PATCH' : 'POST';
    const resp = await fetch(url, {
      method,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(botData),
    });
    const data = await resp.json();
    if (resp.ok) {
      setModalOpen(false);
      setModalBot(null);
      setBots(bots => {
        if (isEdit) {
          return bots.map(b => b.id === data.id ? data : b);
        } else {
          return [...bots, data];
        }
      });
    }
    setModalLoading(false);
  };

  if (!user) return <div style={{ margin: 40, textAlign: 'center' }}>Войдите, чтобы просматривать ботов.</div>;
  if (loading) return <div style={{ margin: 40, textAlign: 'center' }}>Загрузка...</div>;
  if (error) return <div style={{ margin: 40, color: 'red', textAlign: 'center' }}>{error}</div>;

  return (
    <div style={{ maxWidth: 900, margin: '40px auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>Мои боты</h2>
        <button onClick={() => openModal(null)} style={{ padding: '8px 18px', borderRadius: 6, background: '#1890ff', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}>
          + Новый бот
        </button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        {bots.map(bot => (
          <div key={bot.id} style={{ background: '#f7f7f7', borderRadius: 10, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8 }}>{bot.name}</div>
            <div style={{ color: '#888', marginBottom: 8 }}>{bot.description || 'Без описания'}</div>
            <div style={{ fontSize: 14, marginBottom: 4 }}><b>Токен:</b> {bot.token}</div>
            <div style={{ fontSize: 14, marginBottom: 12 }}><b>Сценарий:</b> {bot.scenario?.name || 'Не выбран'}</div>
            <div style={{ marginTop: 'auto', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {bot.is_running ? (
                <button 
                  onClick={() => handleStopBot(bot.id)} 
                  disabled={runningBots.has(bot.id)}
                  style={{ 
                    padding: '4px 12px', 
                    borderRadius: 4, 
                    border: '1px solid #f5222d', 
                    background: '#f5222d', 
                    color: '#fff', 
                    cursor: runningBots.has(bot.id) ? 'not-allowed' : 'pointer',
                    opacity: runningBots.has(bot.id) ? 0.7 : 1
                  }}
                >
                  {runningBots.has(bot.id) ? '...' : 'Stop'}
                </button>
              ) : (
                <button 
                  onClick={() => handleRunBot(bot.id)} 
                  disabled={runningBots.has(bot.id)}
                  style={{ 
                    padding: '4px 12px', 
                    borderRadius: 4, 
                    border: '1px solid #52c41a', 
                    background: '#52c41a', 
                    color: '#fff', 
                    cursor: runningBots.has(bot.id) ? 'not-allowed' : 'pointer',
                    opacity: runningBots.has(bot.id) ? 0.7 : 1
                  }}
                >
                  {runningBots.has(bot.id) ? '...' : 'Play'}
                </button>
              )}
              <button onClick={() => openModal(bot)} style={{ padding: '4px 12px', borderRadius: 4, border: '1px solid #1890ff', background: '#fff', color: '#1890ff', cursor: 'pointer' }}>Редактировать</button>
              <button onClick={() => handleDelete(bot.id)} style={{ padding: '4px 12px', borderRadius: 4, border: '1px solid #f5222d', background: '#fff', color: '#f5222d', cursor: 'pointer' }}>Удалить</button>
            </div>
          </div>
        ))}
      </div>
      <BotModal open={modalOpen} onClose={() => setModalOpen(false)} onSave={handleSave} bot={modalBot} scenarios={scenarios} loading={modalLoading} />
    </div>
  );
} 