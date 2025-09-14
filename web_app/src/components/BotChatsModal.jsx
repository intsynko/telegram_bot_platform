import React, { useState, useEffect } from 'react';
import { BASE_URL } from '../config';
import ConversationModal from './ConversationModal';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function BotChatsModal({ bot, onClose }) {
  const [chats, setChats] = useState([]);
  const [formFields, setFormFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize] = useState(10);
  const [selectedChat, setSelectedChat] = useState(null);
  const [showConversationModal, setShowConversationModal] = useState(false);

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
        setFormFields(data.form_fields || []);
        setTotalPages(Math.ceil(data.count / pageSize) || 1);
      } else {
        console.error('Ошибка загрузки чатов');
        setChats([]);
        setFormFields([]);
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

  const handleViewConversation = (chat) => {
    setSelectedChat(chat);
    setShowConversationModal(true);
  };

  const handleCloseConversationModal = () => {
    setShowConversationModal(false);
    setSelectedChat(null);
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

  const getFieldValue = (chat, fieldName) => {
    const value = chat[`field_${fieldName}`];
    return value || '-';
  };

  const truncateText = (text, maxLength = 50) => {
    if (!text || text === '-') return text;
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
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
              ID пользователей и данные форм {formFields.length > 0 && `(${formFields.length} полей)`}
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
                  minWidth: `${400 + (formFields.length * 150)}px`
                }}>
                  <thead>
                    <tr style={{ background: '#f8f9fa' }}>
                      <th style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #e0e0e0', minWidth: '120px' }}>
                        Действия
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0', minWidth: '120px' }}>
                        ID пользователя
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0', minWidth: '120px' }}>
                        Username
                      </th>
                      {formFields.map(fieldName => (
                        <th key={fieldName} style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0', minWidth: '150px' }}>
                          {fieldName}
                        </th>
                      ))}
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #e0e0e0', minWidth: '120px' }}>
                        Создан
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {chats.map(chat => (
                      <tr key={chat.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <button
                            onClick={() => handleViewConversation(chat)}
                            style={{
                              padding: '6px 12px',
                              fontSize: '12px',
                              background: '#1890ff',
                              color: '#fff',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              fontWeight: '500'
                            }}
                            onMouseEnter={(e) => e.target.style.background = '#40a9ff'}
                            onMouseLeave={(e) => e.target.style.background = '#1890ff'}
                          >
                            💬 Переписка
                          </button>
                        </td>
                        <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '14px' }}>
                          {chat.telegram_user_id}
                        </td>
                        <td style={{ padding: '12px' }}>
                          {chat.telegram_username ? (
                            <a 
                              href={`https://t.me/${chat.telegram_username}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                color: '#1890ff',
                                textDecoration: 'none',
                                fontWeight: '500'
                              }}
                              onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
                              onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
                            >
                              @{chat.telegram_username}
                            </a>
                          ) : '-'}
                        </td>
                        {formFields.map(fieldName => (
                          <td key={fieldName} style={{ 
                            padding: '12px', 
                            fontSize: '14px',
                            maxWidth: '200px',
                            wordBreak: 'break-word',
                            color: getFieldValue(chat, fieldName) === '-' ? '#999' : '#333'
                          }}>
                            {truncateText(getFieldValue(chat, fieldName))}
                          </td>
                        ))}
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

      {showConversationModal && selectedChat && (
        <ConversationModal
          chat={selectedChat}
          bot={bot}
          onClose={handleCloseConversationModal}
        />
      )}
    </div>
  );
}
