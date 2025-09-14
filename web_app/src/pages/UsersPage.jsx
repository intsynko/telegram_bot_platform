import React, { useState, useEffect } from 'react';
import { BASE_URL } from '../config';
import BotChatsModal from '../components/BotChatsModal';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function UsersPage() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBot, setSelectedBot] = useState(null);
  const [showChatsModal, setShowChatsModal] = useState(false);

  useEffect(() => {
    fetchBots();
  }, []);

  const fetchBots = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/bots/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setBots(data);
      } else {
        console.error('Ошибка загрузки ботов');
      }
    } catch (error) {
      console.error('Ошибка сети при загрузке ботов:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBotClick = (bot) => {
    setSelectedBot(bot);
    setShowChatsModal(true);
  };

  const handleCloseChatsModal = () => {
    setShowChatsModal(false);
    setSelectedBot(null);
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Загрузка ботов...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ 
        marginBottom: '30px', 
        color: '#333',
        fontSize: '28px',
        fontWeight: '600'
      }}>
        Управление пользователями
      </h1>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
        gap: '20px' 
      }}>
        {bots.map(bot => (
          <div
            key={bot.id}
            onClick={() => handleBotClick(bot)}
            style={{
              background: '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '12px',
              padding: '20px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              ':hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 16px rgba(0,0,0,0.15)'
              }
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            }}
          >
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              marginBottom: '15px' 
            }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                background: bot.is_running ? '#52c41a' : '#f5222d',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '15px',
                fontSize: '20px'
              }}>
                {bot.is_running ? '🟢' : '🔴'}
              </div>
              <div>
                <h3 style={{ 
                  margin: '0 0 5px 0', 
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#333'
                }}>
                  {bot.name}
                </h3>
                <p style={{ 
                  margin: '0', 
                  color: '#666',
                  fontSize: '14px'
                }}>
                  {bot.is_running ? 'Активен' : 'Остановлен'}
                </p>
              </div>
            </div>

            <div style={{ 
              marginBottom: '15px',
              padding: '10px',
              background: '#f8f9fa',
              borderRadius: '6px'
            }}>
              <p style={{ 
                margin: '0 0 5px 0', 
                fontSize: '14px',
                color: '#666'
              }}>
                <strong>Токен:</strong> {bot.token ? `${bot.token.substring(0, 20)}...` : 'Не указан'}
              </p>
              {bot.scenario && (
                <p style={{ 
                  margin: '0', 
                  fontSize: '14px',
                  color: '#666'
                }}>
                  <strong>Сценарий:</strong> {bot.scenario.name}
                </p>
              )}
            </div>

            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '10px 0',
              borderTop: '1px solid #e0e0e0'
            }}>
              <span style={{
                fontSize: '14px',
                color: '#1890ff',
                fontWeight: '500'
              }}>
                Просмотреть чаты →
              </span>
            </div>
          </div>
        ))}
      </div>

      {bots.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#666'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>🤖</div>
          <h3 style={{ margin: '0 0 10px 0' }}>Нет ботов</h3>
          <p style={{ margin: '0' }}>Создайте бота, чтобы начать работу с пользователями</p>
        </div>
      )}

      {showChatsModal && selectedBot && (
        <BotChatsModal
          bot={selectedBot}
          onClose={handleCloseChatsModal}
        />
      )}
    </div>
  );
}
