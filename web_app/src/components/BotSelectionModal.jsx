import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { BASE_URL } from "../config";

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function BotSelectionModal({ open, onClose, onBotSelected, scenarioId }) {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBot, setSelectedBot] = useState(null);

  useEffect(() => {
    if (open) {
      fetchBots();
    }
  }, [open]);

  const fetchBots = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/api/bots/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setBots(data);
      } else {
        toast.error('Ошибка загрузки ботов');
      }
    } catch (error) {
      toast.error('Ошибка сети при загрузке ботов');
    } finally {
      setLoading(false);
    }
  };

  const handleBotSelect = async (bot) => {
    if (!bot || !scenarioId) return;
    
    setLoading(true);
    try {
      // Сначала назначаем сценарий боту
      const csrfToken = getCookie('csrftoken');
      const assignResponse = await fetch(`${BASE_URL}/api/bots/${bot.id}/set_scenario/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          scenario: scenarioId,
        }),
      });

      if (!assignResponse.ok) {
        toast.error('Ошибка назначения сценария боту');
        setLoading(false);
        return;
      }

      // Затем запускаем бота
      const runResponse = await fetch(`${BASE_URL}/api/bots/${bot.id}/run/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRFToken': csrfToken,
        },
      });

      if (runResponse.ok) {
        toast.success(`Бот ${bot.name} успешно запущен со сценарием!`);
        onBotSelected(bot);
        onClose();
      } else {
        toast.error('Ошибка запуска бота');
      }
    } catch (error) {
      toast.error('Ошибка сети при запуске бота');
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{ 
        background: '#fff', 
        borderRadius: 10, 
        padding: 32, 
        minWidth: 500, 
        maxWidth: '80vw',
        maxHeight: '80vh',
        boxShadow: '0 4px 24px rgba(0,0,0,0.10)', 
        position: 'relative',
        overflow: 'auto'
      }}>
        <button 
          onClick={onClose} 
          type="button" 
          style={{ 
            position: 'absolute', 
            top: 12, 
            right: 18, 
            background: 'none', 
            border: 'none', 
            fontSize: 22, 
            color: '#888', 
            cursor: 'pointer', 
            zIndex: 2 
          }} 
          title="Закрыть"
        >
          ×
        </button>
        
        <h3 style={{ marginBottom: 24, textAlign: 'center' }}>
          Выберите бота для запуска сценария
        </h3>
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <div>Загрузка...</div>
          </div>
        ) : bots.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#666' }}>
            У вас пока нет ботов. Сначала создайте бота в разделе{' '}
            <Link 
              to="/bots" 
              style={{ 
                color: '#1890ff', 
                textDecoration: 'underline',
                cursor: 'pointer',
                fontWeight: '500'
              }}
              onClick={onClose} // Закрываем модалку при переходе
            >
              "Боты"
            </Link>
            .
          </div>
        ) : (
          <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
            {bots.map(bot => (
              <div
                key={bot.id}
                onClick={() => handleBotSelect(bot)}
                style={{
                  padding: 16,
                  border: '1px solid #d9d9d9',
                  borderRadius: 8,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  background: selectedBot?.id === bot.id ? '#f0f8ff' : '#fff',
                  borderColor: selectedBot?.id === bot.id ? '#1890ff' : '#d9d9d9',
                }}
                onMouseEnter={e => {
                  e.target.style.borderColor = '#1890ff';
                  e.target.style.boxShadow = '0 2px 8px rgba(24, 144, 255, 0.15)';
                }}
                onMouseLeave={e => {
                  e.target.style.borderColor = selectedBot?.id === bot.id ? '#1890ff' : '#d9d9d9';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: 8, color: '#1890ff' }}>
                  {bot.name}
                </div>
                <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>
                  {bot.description || 'Без описания'}
                </div>
                <div style={{ fontSize: 12, color: bot.scenario ? '#52c41a' : '#faad14' }}>
                  {bot.scenario ? `Сценарий: ${bot.scenario.name}` : 'Без сценария'}
                </div>
                {bot.is_running && (
                  <div style={{ 
                    fontSize: 11, 
                    color: '#52c41a', 
                    marginTop: 8,
                    padding: '2px 8px',
                    background: '#f6ffed',
                    borderRadius: 4,
                    display: 'inline-block'
                  }}>
                    🟢 Запущен
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        <div style={{ marginTop: 24, textAlign: 'center', fontSize: 12, color: '#666' }}>
          Выбранному боту будет назначен текущий сценарий и он будет автоматически запущен
        </div>
      </div>
    </div>
  );
}
