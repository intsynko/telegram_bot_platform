import React, { useState, useEffect } from 'react';
import { BASE_URL } from "../config";

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function BotModal({ open, onClose, onSave, bot, scenarios, loading, onCreateScenario }) {
  const [name, setName] = useState(bot?.name || '');
  const [token, setToken] = useState(bot?.token || '');
  const [description, setDescription] = useState(bot?.description || '');
  const [scenario, setScenario] = useState(bot?.scenario?.id || '');
  const [showInstructions, setShowInstructions] = useState(false);
  const [nameError, setNameError] = useState('');

  useEffect(() => {
    setName(bot?.name || '');
    setToken(bot?.token || '');
    setDescription(bot?.description || '');
    setScenario(bot?.scenario?.id || '');
    setNameError(''); // Очищаем ошибку при открытии модалки
  }, [bot, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Проверяем, что имя начинается с @
    if (!name.startsWith('@')) {
      setNameError('Имя бота должно начинаться с символа @');
      return;
    }
    
    // Очищаем ошибку если валидация прошла
    setNameError('');
    
    onSave({
      name,
      token,
      description,
      scenario,
    });
  };

  if (!open) return null;
  
  const isEditMode = !!bot;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 400, maxWidth: 500, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
        <button onClick={onClose} type="button" style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} title="Закрыть">×</button>
        <h3>{isEditMode ? 'Редактировать бота' : 'Создать бота'}</h3>
        
        {/* Инструкция для создания бота */}
        {!isEditMode && (
          <div style={{ marginBottom: 16 }}>
            <button
              type="button"
              onClick={() => setShowInstructions(!showInstructions)}
              style={{
                background: 'none',
                border: 'none',
                color: '#1890ff',
                cursor: 'pointer',
                fontSize: 14,
                textDecoration: 'underline',
                padding: 0,
                margin: 0
              }}
            >
              {showInstructions ? 'Скрыть инструкцию' : 'Как создать бота в Telegram?'}
            </button>
            {showInstructions && (
              <div style={{ 
                marginTop: 12, 
                padding: 12, 
                background: '#f8f9fa', 
                borderRadius: 6, 
                fontSize: 13, 
                lineHeight: 1.5,
                border: '1px solid #e9ecef'
              }}>
                <div style={{ fontWeight: 600, marginBottom: 8 }}>Пошаговая инструкция:</div>
                <ol style={{ margin: 0, paddingLeft: 20 }}>
                  <li>Откройте Telegram и найдите <a href="https://t.me/botfather" target="_blank" rel="noopener noreferrer" style={{ color: '#1890ff', textDecoration: 'underline' }}><strong>@BotFather</strong></a></li>
                  <li>Отправьте команду <code>/newbot</code></li>
                  <li>Введите название для вашего бота</li>
                  <li>Введите username для бота (должен заканчиваться на "bot")</li>
                  <li>BotFather выдаст вам токен - скопируйте его</li>
                  <li>Вставьте токен в поле "Токен" ниже</li>
                </ol>
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                  <strong>Важно:</strong> Храните токен в секрете и не делитесь им с другими!
                </div>
              </div>
            )}
          </div>
        )}
        
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
            Имя бота {!isEditMode && <span style={{ color: '#f5222d' }}>*</span>}
          </label>
          <input 
            value={name} 
            onChange={e => {
              setName(e.target.value);
              // Очищаем ошибку при вводе
              if (nameError) setNameError('');
            }} 
            placeholder={!isEditMode ? "@my_bot" : "Имя бота"} 
            required 
            style={{ 
              width: '100%', 
              padding: '8px 12px', 
              borderRadius: 4, 
              border: nameError ? '1px solid #f5222d' : '1px solid #d9d9d9',
              fontSize: 14,
              backgroundColor: nameError ? '#fff2f0' : '#fff'
            }} 
          />
          {nameError ? (
            <div style={{ fontSize: 12, color: '#f5222d', marginTop: 4 }}>
              {nameError}
            </div>
          ) : !isEditMode && (
            <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
              Имя должно начинаться с символа @ (например: @my_bot)
            </div>
          )}
        </div>
        
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
            Токен бота <span style={{ color: '#f5222d' }}>*</span>
          </label>
          <input 
            value={token} 
            onChange={e => setToken(e.target.value)} 
            placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" 
            required 
            style={{ 
              width: '100%', 
              padding: '8px 12px', 
              borderRadius: 4, 
              border: '1px solid #d9d9d9',
              fontSize: 14
            }} 
          />
          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
            Получите токен у <a href="https://t.me/botfather" target="_blank" rel="noopener noreferrer" style={{ color: '#1890ff', textDecoration: 'underline' }}>@BotFather</a> в Telegram
          </div>
        </div>
        
        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
            Описание
          </label>
          <textarea 
            value={description} 
            onChange={e => setDescription(e.target.value)} 
            placeholder="Краткое описание бота" 
            style={{ 
              width: '100%', 
              padding: '8px 12px', 
              borderRadius: 4, 
              border: '1px solid #d9d9d9',
              fontSize: 14,
              minHeight: 60,
              resize: 'vertical'
            }} 
          />
        </div>
        
        <div style={{ marginBottom: 18 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
            Сценарий
          </label>
          <select 
            value={scenario} 
            onChange={e => setScenario(e.target.value)} 
            style={{ 
              width: '100%', 
              padding: '8px 12px', 
              borderRadius: 4, 
              border: '1px solid #d9d9d9',
              fontSize: 14
            }}
          >
            <option value="">Выберите сценарий (необязательно)</option>
            {scenarios.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
            Бот можно создать без сценария и добавить его позже
          </div>
          
          {/* Кнопка создания сценария для ботов без сценария */}
          {isEditMode && !bot.scenario && onCreateScenario && (
            <div style={{ marginTop: 12 }}>
              <button
                type="button"
                onClick={onCreateScenario}
                style={{
                  padding: '8px 16px',
                  borderRadius: 4,
                  border: '1px solid #fa8c16',
                  background: '#fa8c16',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: 14,
                  fontWeight: 500,
                  width: '100%'
                }}
              >
                ➕ Создать новый сценарий
              </button>
              <div style={{ fontSize: 12, color: '#666', marginTop: 4, textAlign: 'center' }}>
                Или выберите существующий сценарий выше
              </div>
            </div>
          )}
        </div>
        
        <button 
          type="submit" 
          disabled={loading} 
          style={{ 
            width: '100%', 
            padding: 12, 
            borderRadius: 6, 
            background: '#1890ff', 
            color: '#fff', 
            border: 'none', 
            fontWeight: 600, 
            fontSize: 16, 
            cursor: loading ? 'not-allowed' : 'pointer', 
            opacity: loading ? 0.7 : 1 
          }}
        >
          {loading ? '...' : (isEditMode ? 'Сохранить' : 'Создать бота')}
        </button>
      </form>
    </div>
  );
}
