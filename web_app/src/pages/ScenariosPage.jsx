import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BASE_URL } from "../config";

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export default function ScenariosPage({ user }) {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [userScenarios, setUserScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCopyModal, setShowCopyModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [copyLoading, setCopyLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    
    // Загружаем шаблоны и пользовательские сценарии параллельно
    Promise.all([
      fetch(`${BASE_URL}/api/scenarios/template/`, { credentials: 'include' }),
      fetch(`${BASE_URL}/api/scenarios/`, { credentials: 'include' })
    ])
      .then(responses => Promise.all(responses.map(res => res.json())))
      .then(([templatesData, userScenariosData]) => {
        setTemplates(templatesData);
        setUserScenarios(userScenariosData);
        setLoading(false);
      })
      .catch(() => {
        setError('Ошибка загрузки сценариев');
        setLoading(false);
      });
  }, [user]);

  const handleCreateEmpty = () => {
    navigate('/scenarios?create=true');
  };

  const handleUseTemplate = (template) => {
    setSelectedTemplate(template);
    setShowCopyModal(true);
  };

  const handleConfirmCopy = async () => {
    if (!selectedTemplate) return;
    
    setCopyLoading(true);
    try {
      const resp = await fetch(`${BASE_URL}/api/scenarios/${selectedTemplate.id}/copy/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });
      
      if (resp.ok) {
        const newScenario = await resp.json();
        setUserScenarios(prev => [...prev, newScenario]);
        setShowCopyModal(false);
        setSelectedTemplate(null);
        navigate(`/scenarios?id=${newScenario.id}`);
      } else {
        alert('Ошибка создания сценария');
      }
    } catch (error) {
      alert('Ошибка создания сценария');
    } finally {
      setCopyLoading(false);
    }
  };

  const handleOpenScenario = (scenarioId) => {
    navigate(`/scenarios?id=${scenarioId}`);
  };

  const handleDeleteScenario = async (scenarioId) => {
    if (!window.confirm('Удалить сценарий?')) return;
    
    try {
      const csrfToken = getCookie('csrftoken');
      await fetch(`${BASE_URL}/api/scenarios/${scenarioId}/`, {
        method: 'DELETE',
        credentials: 'include',
        headers: { 'X-CSRFToken': csrfToken },
      });
      setUserScenarios(prev => prev.filter(s => s.id !== scenarioId));
    } catch (error) {
      alert('Ошибка удаления сценария');
    }
  };

  if (!user) return <div style={{ margin: 40, textAlign: 'center' }}>Войдите, чтобы просматривать сценарии.</div>;
  if (loading) return <div style={{ margin: 40, textAlign: 'center' }}>Загрузка...</div>;
  if (error) return <div style={{ margin: 40, color: 'red', textAlign: 'center' }}>{error}</div>;

  return (
    <div style={{ maxWidth: 1200, margin: '40px auto' }}>
      <h2 style={{ marginBottom: 24 }}>Мои сценарии</h2>
      
      {/* Шаблоны */}
      <div style={{ marginBottom: 40 }}>
        <h3 style={{ marginBottom: 16, color: '#333' }}>Шаблоны для быстрого старта</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 24 }}>
          {/* Пустая карточка для создания с нуля */}
          <div 
            onClick={handleCreateEmpty}
            style={{ 
              background: '#f0f8ff', 
              border: '2px dashed #1890ff', 
              borderRadius: 10, 
              padding: 40, 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.background = '#e6f7ff'}
            onMouseLeave={(e) => e.target.style.background = '#f0f8ff'}
          >
            <div style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }}>+</div>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8, color: '#1890ff' }}>Начать с пустого листа</div>
            <div style={{ color: '#666', fontSize: 14 }}>Создать новый сценарий с нуля</div>
          </div>
          
                     {templates.map(template => (
             <div key={template.id} style={{ background: '#f7f7f7', borderRadius: 10, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', position: 'relative' }}>
               <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8 }}>{template.name}</div>
               <div style={{ color: '#888', marginBottom: 12, lineHeight: 1.4 }}>{template.description || 'Без описания'}</div>
               <div style={{ marginTop: 'auto', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                 <button 
                   onClick={() => handleUseTemplate(template)} 
                   style={{ 
                     padding: '6px 14px', 
                     borderRadius: 4, 
                     border: '1px solid #52c41a', 
                     background: '#52c41a', 
                     color: '#fff', 
                     cursor: 'pointer',
                     fontWeight: 500
                   }}
                 >
                   Использовать шаблон
                 </button>
               </div>
             </div>
           ))}
         </div>
       </div>

      {/* Пользовательские сценарии */}
      {userScenarios.length > 0 && (
        <div>
          <h3 style={{ marginBottom: 16, color: '#333' }}>Мои сценарии</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 24 }}>
            {userScenarios.map(scenario => (
              <div 
                key={scenario.id} 
                onClick={() => handleOpenScenario(scenario.id)}
                style={{ 
                  background: '#f7f7f7', 
                  borderRadius: 10, 
                  padding: 24, 
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'flex-start', 
                  position: 'relative',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = '#f0f0f0'}
                onMouseLeave={(e) => e.target.style.background = '#f7f7f7'}
              >
                <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8 }}>{scenario.name}</div>
                <div style={{ color: '#888', marginBottom: 12, lineHeight: 1.4 }}>{scenario.description || 'Без описания'}</div>
                <div style={{ fontSize: 14, marginBottom: 8 }}>
                  <b>Создан:</b> {new Date(scenario.created_at).toLocaleDateString()}
                </div>
                {scenario.updated_at && (
                  <div style={{ fontSize: 14, marginBottom: 12 }}>
                    <b>Обновлен:</b> {new Date(scenario.updated_at).toLocaleDateString()}
                  </div>
                )}
                <div style={{ marginTop: 'auto', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenScenario(scenario.id);
                    }}
                    style={{ 
                      padding: '6px 14px', 
                      borderRadius: 4, 
                      border: '1px solid #1890ff', 
                      background: '#1890ff', 
                      color: '#fff', 
                      cursor: 'pointer',
                      fontWeight: 500
                    }}
                  >
                    Открыть
                  </button>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteScenario(scenario.id);
                    }}
                    style={{ 
                      padding: '6px 14px', 
                      borderRadius: 4, 
                      border: '1px solid #f5222d', 
                      background: '#fff', 
                      color: '#f5222d', 
                      cursor: 'pointer' 
                    }}
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

             {/* Сообщение если нет сценариев */}
       {userScenarios.length === 0 && templates.length === 0 && (
         <div style={{ textAlign: 'center', color: '#666', marginTop: 40 }}>
           <div style={{ fontSize: 18, marginBottom: 8 }}>У вас пока нет сценариев</div>
           <div style={{ fontSize: 14 }}>Создайте первый сценарий, используя шаблон или начните с пустого листа</div>
         </div>
       )}

       {/* Модальное окно подтверждения копирования */}
       {showCopyModal && selectedTemplate && (
         <div style={{
           position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
           background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
         }}>
           <div style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 400, maxWidth: 500, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
             <button 
               onClick={() => { setShowCopyModal(false); setSelectedTemplate(null); }} 
               style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} 
               title="Закрыть"
             >
               ×
             </button>
             <h3 style={{ marginBottom: 16 }}>Использовать шаблон</h3>
             <div style={{ marginBottom: 20 }}>
               <div style={{ fontWeight: 600, marginBottom: 8 }}>{selectedTemplate.name}</div>
               <div style={{ color: '#666', fontSize: 14 }}>{selectedTemplate.description || 'Без описания'}</div>
             </div>
             <div style={{ color: '#666', fontSize: 14, marginBottom: 24 }}>
               Этот шаблон будет скопирован и создан как новый сценарий. Вы сможете сразу приступить к его редактированию.
             </div>
             <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
               <button 
                 onClick={() => { setShowCopyModal(false); setSelectedTemplate(null); }}
                 disabled={copyLoading}
                 style={{ 
                   padding: '8px 16px', 
                   borderRadius: 6, 
                   border: '1px solid #ddd', 
                   background: '#fff', 
                   color: '#666', 
                   cursor: copyLoading ? 'not-allowed' : 'pointer',
                   opacity: copyLoading ? 0.7 : 1
                 }}
               >
                 Отмена
               </button>
               <button 
                 onClick={handleConfirmCopy}
                 disabled={copyLoading}
                 style={{ 
                   padding: '8px 16px', 
                   borderRadius: 6, 
                   background: '#52c41a', 
                   color: '#fff', 
                   border: 'none', 
                   cursor: copyLoading ? 'not-allowed' : 'pointer',
                   opacity: copyLoading ? 0.7 : 1,
                   fontWeight: 500
                 }}
               >
                 {copyLoading ? 'Создание...' : 'Создать сценарий'}
               </button>
             </div>
           </div>
         </div>
       )}
     </div>
   );
 }
