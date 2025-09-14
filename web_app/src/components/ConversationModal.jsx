import React, { useState, useEffect } from 'react';
import { BASE_URL } from '../config';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function ConversationModal({ chat, bot, onClose }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (chat) {
      fetchMessages();
    }
  }, [chat]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BASE_URL}/api/chats/${chat.id}/messages/`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      } else {
        console.error('Ошибка загрузки сообщений');
        setMessages([]);
      }
    } catch (error) {
      console.error('Ошибка сети при загрузке сообщений:', error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const formatMessageTime = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (!chat) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0,0,0,0.5)',
      zIndex: 1001,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: '#fff',
        borderRadius: '12px',
        width: '90%',
        maxWidth: '800px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 10px 40px rgba(0,0,0,0.2)'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h2 style={{ margin: '0 0 5px 0', fontSize: '20px', color: '#333' }}>
              Переписка с {chat.telegram_username ? `@${chat.telegram_username}` : `ID ${chat.telegram_user_id}`}
            </h2>
            <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
              Бот: {bot.name} • {messages.length} сообщений
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              color: '#999',
              cursor: 'pointer',
              padding: '5px',
              borderRadius: '4px'
            }}
            onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
            onMouseLeave={(e) => e.target.style.background = 'none'}
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: '20px',
          background: '#f8f9fa'
        }}>
          {loading ? (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '200px',
              fontSize: '16px',
              color: '#666'
            }}>
              Загрузка сообщений...
            </div>
          ) : messages.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '60px 20px',
              color: '#666'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '20px' }}>💬</div>
              <h3 style={{ margin: '0 0 10px 0' }}>Нет сообщений</h3>
              <p style={{ margin: '0' }}>Переписка с этим пользователем пуста</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {messages.map((message, index) => (
                  <div
                    key={message.id}
                    style={{
                      display: 'flex',
                      justifyContent: message.is_user_message ? 'flex-start' : 'flex-end',
                      marginBottom: '8px'
                    }}
                  >
                  <div style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    background: message.is_user_message ? '#fff' : '#1890ff',
                    color: message.is_user_message ? '#333' : '#fff',
                    border: message.is_user_message ? '1px solid #e0e0e0' : 'none',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    position: 'relative'
                  }}>
                    <div style={{
                      fontSize: '14px',
                      lineHeight: '1.4',
                      wordBreak: 'break-word',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {message.text}
                    </div>
                    <div style={{
                      fontSize: '11px',
                      opacity: 0.7,
                      marginTop: '4px',
                      textAlign: 'right'
                    }}>
                      {formatMessageTime(message.created_at)}
                    </div>
                    <div style={{
                      position: 'absolute',
                      top: '8px',
                      right: message.is_user_message ? 'auto' : '-8px',
                      left: message.is_user_message ? '-8px' : 'auto',
                      width: '0',
                      height: '0',
                      borderLeft: message.is_user_message ? '8px solid #fff' : '8px solid transparent',
                      borderRight: message.is_user_message ? '8px solid transparent' : '8px solid #1890ff',
                      borderTop: '8px solid transparent',
                      borderBottom: '8px solid transparent'
                    }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
