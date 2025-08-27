import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import { BASE_URL } from "../config";
import BotSelectionModal from './BotSelectionModal';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function CreateScenarioModal({ open, onClose, onCreate, loading }) {
  const [name, setName] = useState('');
  const csrfToken = getCookie('csrftoken') || '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (name.trim()) {
      await onCreate(name);
      setName('');
    }
  };

  if (!open) return null;
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 320, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
        <button onClick={onClose} type="button" style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} title="Закрыть">×</button>
        <h3>Создать сценарий</h3>
        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Название сценария"
          required
          style={{ width: '100%', marginBottom: 18, padding: 8 }}
        />
        <button type="submit" disabled={loading} style={{ width: '100%', padding: 10, borderRadius: 6, background: '#1890ff', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
          {loading ? '...' : 'Создать'}
        </button>
      </form>
    </div>
  );
}

export default function ScenarioSelector({ nodes = [], edges = [], setNodes, setEdges, scenarioId, shouldCreate }) {
  const [scenarios, setScenarios] = useState([]);
  const [currentScenario, setCurrentScenario] = useState('');
  const [scenarioName, setScenarioName] = useState('');
  const [showCreateScenarioModal, setShowCreateScenarioModal] = useState(false);
  const [createScenarioLoading, setCreateScenarioLoading] = useState(false);
  const [showBotSelectionModal, setShowBotSelectionModal] = useState(false);
  const [currentBot, setCurrentBot] = useState(null);
  const [botRunning, setBotRunning] = useState(false);
  const csrfToken = getCookie('csrfToken') || '';

  // Загрузка сценариев
  const fetchScenarios = useCallback(() => {
    fetch(`${BASE_URL}/api/scenarios/`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setScenarios(data);
        if (data.length && !currentScenario) setCurrentScenario(data[0].id);
      })
      .catch(() => {
        // Обработка ошибки загрузки
      });
  }, [currentScenario]);

  // Поиск бота с текущим сценарием
  const findBotWithScenario = useCallback(async () => {
    if (!currentScenario) return;
    
    try {
      const response = await fetch(`${BASE_URL}/api/bots/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const bots = await response.json();
        const botWithScenario = bots.find(bot => bot.scenario?.id == currentScenario);
        if (botWithScenario) {
          setCurrentBot(botWithScenario);
          setBotRunning(botWithScenario.is_running || false);
        } else {
          setCurrentBot(null);
          setBotRunning(false);
        }
      }
    } catch (error) {
      // Игнорируем ошибки при поиске бота
    }
  }, [currentScenario]);

  useEffect(() => {
    fetchScenarios();
  }, [fetchScenarios]);

  // Устанавливаем scenarioId как текущий сценарий, если он передан
  useEffect(() => {
    if (scenarioId && scenarios.length > 0) {
      setCurrentScenario(scenarioId);
    }
  }, [scenarioId, scenarios]);

  // Автоматически открываем модалку создания сценария, если передан параметр shouldCreate
  useEffect(() => {
    if (shouldCreate) {
      setShowCreateScenarioModal(true);
    }
  }, [shouldCreate]);

    // Подгрузка graph при смене сценария
  useEffect(() => {
    if (!currentScenario) return;
    fetch(`${BASE_URL}/api/scenarios/${currentScenario}/`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setScenarioName(data.name || '');
        if (data.graph) {
          try {
            const graph = typeof data.graph === 'string' ? JSON.parse(data.graph) : data.graph;
            setNodes(Array.isArray(graph.nodes) ? graph.nodes : []);
            setEdges(Array.isArray(graph.edges) ? graph.edges : []);
          } catch (e) {
            setNodes([]);
            setEdges([]);
          }
        } else {
          setNodes([]);
          setEdges([]);
        }
      });
      
    // Ищем бота с текущим сценарием
    findBotWithScenario();
  }, [currentScenario, setNodes, setEdges, findBotWithScenario]);

  // Создание сценария
  const handleCreateScenario = async (name) => {
    const csrfToken = getCookie('csrftoken');
    setCreateScenarioLoading(true);
    try {
      const resp = await fetch(`${BASE_URL}/api/scenarios/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ name }),
      });
      
      if (resp.ok) {
        const newScenario = await resp.json();
        setCurrentScenario(newScenario.id);
        setScenarioName(newScenario.name);
        setShowCreateScenarioModal(false);
        setCreateScenarioLoading(false);
        fetchScenarios();
      } else {
        alert('Ошибка создания сценария');
        setCreateScenarioLoading(false);
      }
    } catch (error) {
      alert('Ошибка создания сценария');
      setCreateScenarioLoading(false);
    }
  };

  // Запуск бота
  const handleRunBot = async () => {
    if (!currentBot) {
      setShowBotSelectionModal(true);
      return;
    }

    const csrfToken = getCookie('csrftoken');
    try {
      const response = await fetch(`${BASE_URL}/api/bots/${currentBot.id}/run/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRFToken': csrfToken,
        },
      });
      
      if (response.ok) {
        setBotRunning(true);
        toast.success(`Бот ${currentBot.name} успешно запущен!`);
      } else {
        toast.error('Ошибка запуска бота');
      }
    } catch (error) {
      toast.error('Ошибка сети при запуске бота');
    }
  };

  // Остановка бота
  const handleStopBot = async () => {
    if (!currentBot) return;

    const csrfToken = getCookie('csrftoken');
    try {
      const response = await fetch(`${BASE_URL}/api/bots/${currentBot.id}/stop/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRFToken': csrfToken,
        },
      });
      
      if (response.ok) {
        setBotRunning(false);
        toast.success(`Бот ${currentBot.name} остановлен!`);
      } else {
        toast.error('Ошибка остановки бота');
      }
    } catch (error) {
      toast.error('Ошибка сети при остановке бота');
    }
  };

  // Обработка выбора бота из модалки
  const handleBotSelected = (bot) => {
    setCurrentBot(bot);
    setBotRunning(true);
    findBotWithScenario(); // Обновляем состояние
  };

  // Сохранение сценария
  const handleSaveScenario = async () => {
    if (!currentScenario) return;
    const csrfToken = getCookie('csrftoken');
    const graph = JSON.stringify({ nodes, edges });
    try {
      const resp = await fetch(`${BASE_URL}/api/scenarios/${currentScenario}/`, {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ 
          graph,
          name: scenarioName 
        }),
      });
      if (resp.ok) {
        toast.success('Сценарий успешно сохранён!');
      } else {
        toast.error('Ошибка при сохранении сценария');
      }
    } catch (e) {
      toast.error('Ошибка сети при сохранении сценария');
    }
  };

  return (
    <div style={{ marginBottom: 18, padding: 10, background: '#fff', borderRadius: 6, border: '1px solid #bbb', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <label style={{ fontWeight: 500, marginBottom: 4 }}>Название сценария:</label>
      <input
        type="text"
        value={scenarioName}
        onChange={e => setScenarioName(e.target.value)}
        placeholder="Введите название сценария"
        style={{ 
          marginBottom: 8, 
          padding: '6px 8px', 
          borderRadius: 4, 
          border: '1px solid #ccc',
          fontSize: 14
        }}
      />
      <button
        onClick={handleSaveScenario}
        style={{ 
          padding: '6px 0', 
          borderRadius: 4, 
          border: '1px solid #52c41a', 
          background: '#fff', 
          color: '#52c41a', 
          cursor: 'pointer', 
          fontSize: 14,
          fontWeight: 500
        }}
      >
        💾 Сохранить
      </button>
      
      {/* Кнопка запуска/остановки бота */}
      <button
        onClick={botRunning ? handleStopBot : handleRunBot}
        style={{ 
          padding: '6px 0', 
          borderRadius: 4, 
          border: botRunning ? '1px solid #f5222d' : '1px solid #1890ff', 
          background: '#fff', 
          color: botRunning ? '#f5222d' : '#1890ff', 
          cursor: 'pointer', 
          fontSize: 14,
          fontWeight: 500
        }}
      >
        {botRunning ? '⏹️ Остановить' : '▶️ Запустить'}
      </button>
      
      {/* Информация о боте */}
      {currentBot && (
        <div style={{ 
          fontSize: 12, 
          color: '#666', 
          padding: '8px', 
          background: '#f5f5f5', 
          borderRadius: 4,
          textAlign: 'center'
        }}>
          Бот: {currentBot.name} {botRunning ? '🟢 запущен' : '🔴 остановлен'}
        </div>
      )}
      
      <CreateScenarioModal
        open={showCreateScenarioModal}
        onClose={() => setShowCreateScenarioModal(false)}
        onCreate={handleCreateScenario}
        loading={createScenarioLoading}
      />
      
      <BotSelectionModal
        open={showBotSelectionModal}
        onClose={() => setShowBotSelectionModal(false)}
        onBotSelected={handleBotSelected}
        scenarioId={currentScenario}
      />
    </div>
  );
}
