import React, { useState, useEffect, useCallback } from 'react';

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
      await onCreate({name});
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


function SaveScenarioModal({ open, onClose, json }) {
  if (!open) return null;
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 420, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
        <button onClick={onClose} type="button" style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} title="Закрыть">×</button>
        <h3>Сценарий в формате JSON</h3>
        <textarea
          value={json}
          readOnly
          style={{ width: '100%', minHeight: 200, fontFamily: 'monospace', marginBottom: 16, padding: 8, borderRadius: 6, border: '1px solid #ccc' }}
        />
        <button
          onClick={() => { navigator.clipboard.writeText(json); }}
          style={{ width: '100%', padding: 10, borderRadius: 6, background: '#1890ff', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
        >
          Скопировать JSON
        </button>
      </div>
    </div>
  );
}

export default function ScenarioSelector({
  onScenarioChange,
  onScenarioCreated,
  nodes,
  edges,
}) {
  const [scenarios, setScenarios] = useState([]);
  const [currentScenario, setCurrentScenario] = useState('');
  const [scenariosLoading, setScenariosLoading] = useState(false);
  const [showCreateScenarioModal, setShowCreateScenarioModal] = useState(false);
  const [createScenarioLoading, setCreateScenarioLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const csrfToken = getCookie('csrftoken') || '';

  // Получить сценарии с API
  const fetchScenarios = useCallback(() => {
    setScenariosLoading(true);
    fetch('http://localhost:8000/api/scenarios/', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setScenarios(data);
        if (data.length && !currentScenario) setCurrentScenario(data[0].id);
        setScenariosLoading(false);
      })
      .catch(() => setScenariosLoading(false));
  }, [currentScenario]);

  useEffect(() => {
    fetchScenarios();
  }, [fetchScenarios]);

  const handleCreateScenario = async (name) => {
    setCreateLoading(true);
    await fetch('http://localhost:8000/api/scenarios/', {
      method: 'POST',
      credentials: 'include',
      headers: {
         'Content-Type': 'application/json' , 
         'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(name),
    });
    setShowCreateScenarioModal(false);
    setCreateLoading(false);
    fetchScenarios();
  };

  return (
    <div>
    <div style={{ marginBottom: 18, padding: 10, background: '#fff', borderRadius: 6, border: '1px solid #bbb', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <label style={{ fontWeight: 500, marginBottom: 4 }}>Сценарий:</label>
      <select
        value={currentScenario}
        onChange={e => onScenarioChange(e.target.value)}
        style={{ marginBottom: 6, padding: 4, borderRadius: 4, border: '1px solid #ccc' }}
        disabled={scenariosLoading}
      >
        {scenariosLoading ? (
          <option>Загрузка...</option>
        ) : (
          scenarios.map(s => <option key={s.id} value={s.id}>{s.name}</option>)
        )}
      </select>
      <button
        onClick={() => setShowCreateScenarioModal(true)}
        style={{ padding: '4px 0', borderRadius: 4, border: '1px solid #1890ff', background: '#fff', color: '#1890ff', cursor: 'pointer', fontSize: 14 }}
      >
        + Создать сценарий
      </button>
      <CreateScenarioModal
        open={showCreateScenarioModal}
        onClose={() => setShowCreateScenarioModal(false)}
        onCreate={handleCreateScenario}
        loading={createScenarioLoading}
      />
    </div>
    <div>
      <button
        onClick={() => setShowSaveModal(true)}
        style={{ padding: '4px 0', borderRadius: 4, border: '1px solid #52c41a', background: '#fff', color: '#52c41a', cursor: 'pointer', fontSize: 14, marginTop: 8 }}
      >
        💾 Сохранить
      </button>
      <SaveScenarioModal
        open={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        json={JSON.stringify({ nodes, edges }, null, 2)}
      />
    </div>
    </div>
    
  );
}
