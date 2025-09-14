import React, { useState, useEffect } from 'react';
import { BASE_URL } from '../config';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function BotChatsModal({ bot, onClose }) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize] = useState(10);

  useEffect(() => {
    if (bot) {
      fetchChats();
    }
  }, [bot, currentPage]);

  const fetchChats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BASE_URL}/api/chats/by_bot/${bot.id}/?page=${currentPage}&page_size=${pageSize}`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setChats(data.results || []);
        setTotalPages(Math.ceil(data.count / pageSize) || 1);
      } else {
        console.error('Ошибка загрузки чатов');
        setChats([]);
      }
    } catch (error) {
      console.error('Ошибка сети при загрузке чатов:', error);
      setChats([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFormFieldsTable = (formFields) => {
    if (!formFields || formFields.length === 0) {
      return <span style={{ color: '#999', fontStyle: 'italic' }}>Нет данных</span>;
    }

    return (
      <table style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: '12px',
        marginTop: '5px'
      }}>
        <thead>
          <tr style={{ background: '#f5f5f5' }}>
            <th style={{ padding: '4px 8px', textAlign: 'left', border: '1px solid #ddd' }}>Поле</th>
            <th style={{ padding: '4px 8px', textAlign: 'left', border: '1px solid #ddd' }}>Значение</th>
          </tr>
        </thead>
        <tbody>
          {formFields.map((field, index) => (
            <tr key={index}>
              <td style={{ padding: '4px 8px', border: '1px solid #ddd', maxWidth: '150px', wordBreak: 'break-word' }}>
                {field.name}
              </td>
              <td style={{ padding: '4px 8px', border: '1px solid #ddd', maxWidth: '200px', wordBreak: 'break-word' }}>
                {field.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  if (!bot) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0,0,0,0.5)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: '#fff',
        borderRadius: '12px',
        width: '90%',
        maxWidth: '1200px',
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
            <h2 style={{ margin: '0 0 5px 0', fontSize: '24px', color: '#333' }}>
              Чаты бота: {bot.name}
            </h2>
            <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
              ID пользователей и данные форм
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

        {/* Content */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: '20px'
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
              Загрузка чатов...
            </div>
          ) : chats.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '60px 20px',
              color: '#666'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '20px' }}>💬</div>
              <h3 style={{ margin: '0 0 10px 0' }}>Нет чатов</h3>
              <p style={{ margin: '0' }}>Пользователи еще не начали диалог с этим ботом</p>
            </div>
          ) : (
            <div>
              {/* Table */}
              <div style={{
                overflow: 'auto',
                border: '1px solid #e0e0e0',
                borderRadius: '8px'
              }}>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  minWidth: '800px'
                }}>
                  <thead>
                    <tr style={{ background: '#f8f9fa' }}>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0' }}>
                        ID пользователя
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0' }}>
                        Username
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0' }}>
                        ID чата
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0' }}>
                        Поля формы
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0' }}>
                        Создан
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {chats.map(chat => (
                      <tr key={chat.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '14px' }}>
                          {chat.telegram_user_id}
                        </td>
                        <td style={{ padding: '12px' }}>
                          {chat.telegram_username ? `@${chat.telegram_username}` : '-'}
                        </td>
                        <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '14px' }}>
                          {chat.telegram_chat_id}
                        </td>
                        <td style={{ padding: '12px', maxWidth: '300px' }}>
                          {getFormFieldsTable(chat.form_fields)}
                        </td>
                        <td style={{ padding: '12px', fontSize: '14px', color: '#666' }}>
                          {formatDate(chat.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  marginTop: '20px',
                  gap: '10px'
                }}>
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    style={{
                      padding: '8px 16px',
                      border: '1px solid #d9d9d9',
                      background: currentPage === 1 ? '#f5f5f5' : '#fff',
                      borderRadius: '6px',
                      cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                      color: currentPage === 1 ? '#999' : '#333'
                    }}
                  >
                    Назад
                  </button>
                  
                  <span style={{ fontSize: '14px', color: '#666' }}>
                    Страница {currentPage} из {totalPages}
                  </span>
                  
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    style={{
                      padding: '8px 16px',
                      border: '1px solid #d9d9d9',
                      background: currentPage === totalPages ? '#f5f5f5' : '#fff',
                      borderRadius: '6px',
                      cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                      color: currentPage === totalPages ? '#999' : '#333'
                    }}
                  >
                    Вперед
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
