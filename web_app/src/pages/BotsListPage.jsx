import React, { useEffect, useState } from 'react';
import { BASE_URL } from "../config";
import BotModal from '../components/BotModal';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
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
    fetch(`${BASE_URL}/api/bots/`, {
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
    const resp = await fetch(`${BASE_URL}/api/scenarios/`, { credentials: 'include' });
    const data = await resp.json();
    setScenarios(data);
    setModalBot(bot);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить бота?')) return;
    const csrfToken = getCookie('csrftoken');
    await fetch(`${BASE_URL}/api/bots/${id}/`, {
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
      const resp = await fetch(`${BASE_URL}/api/bots/${botId}/run/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': csrfToken },
      });
      if (resp.ok) {
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
      const resp = await fetch(`${BASE_URL}/api/bots/${botId}/stop/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': csrfToken },
      });
      if (resp.ok) {
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
      ? `${BASE_URL}/api/bots/${modalBot.id}/`
      : `${BASE_URL}/api/bots/`;
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

  const handleCreateScenario = () => {
    // Закрываем модалку бота и переходим к созданию сценария
    setModalOpen(false);
    // Здесь можно добавить навигацию к созданию сценария
    // Например, открыть модалку создания сценария или перейти на страницу сценариев
    window.open('/scenarios/templates', '_blank');
  };

  if (!user) return <div style={{ margin: 40, textAlign: 'center' }}>Войдите, чтобы просматривать ботов.</div>;
  if (loading) return <div style={{ margin: 40, textAlign: 'center' }}>Загрузка...</div>;
  if (error) return <div style={{ margin: 40, color: 'red', textAlign: 'center' }}>{error}</div>;

  return (
    <div style={{ maxWidth: 900, margin: '40px auto' }}>
      <h2 style={{ marginBottom: 24 }}>Мои боты</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        {/* Карточка для создания нового бота */}
        <div 
          onClick={() => openModal(null)}
          style={{ 
            background: '#f0f8ff', 
            border: '2px dashed #1890ff', 
            borderRadius: 10, 
            padding: 40, 
            textAlign: 'center', 
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 200
          }}
          onMouseEnter={(e) => e.target.style.background = '#e6f7ff'}
          onMouseLeave={(e) => e.target.style.background = '#f0f8ff'}
        >
          <div style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }}>+</div>
          <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8, color: '#1890ff' }}>Создать нового бота</div>
          <div style={{ color: '#666', fontSize: 14 }}>Добавить нового Telegram бота</div>
        </div>
        
        {bots.map(bot => (
          <div key={bot.id} style={{ background: '#f7f7f7', borderRadius: 10, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8 }}>
              <a 
                href={`https://t.me/${bot.name.replace('@', '')}`} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ 
                  color: '#1890ff', 
                  textDecoration: 'none',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
                onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
              >
                {bot.name}
              </a>
            </div>
            <div style={{ color: '#888', marginBottom: 8 }}>{bot.description || 'Без описания'}</div>
            <div style={{ fontSize: 14, marginBottom: 4 }}><b>Токен:</b> {bot.token}</div>
            <div style={{ fontSize: 14, marginBottom: 12 }}>
              <b>Сценарий:</b> 
              <span style={{ color: bot.scenario ? '#333' : '#f5222d', fontWeight: bot.scenario ? 'normal' : '500' }}>
                {bot.scenario?.name || 'Не выбран'}
              </span>
            </div>
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
                  disabled={runningBots.has(bot.id) || !bot.scenario}
                  style={{ 
                    padding: '4px 12px', 
                    borderRadius: 4, 
                    border: '1px solid #52c41a', 
                    background: '#52c41a', 
                    color: '#fff', 
                    cursor: (runningBots.has(bot.id) || !bot.scenario) ? 'not-allowed' : 'pointer',
                    opacity: (runningBots.has(bot.id) || !bot.scenario) ? 0.7 : 1
                  }}
                  title={!bot.scenario ? 'Для запуска бота необходимо выбрать сценарий' : ''}
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
      <BotModal 
        open={modalOpen} 
        onClose={() => setModalOpen(false)} 
        onSave={handleSave} 
        bot={modalBot} 
        scenarios={scenarios} 
        loading={modalLoading} 
        onCreateScenario={handleCreateScenario} 
      />
    </div>
  );
} 