import React, { useState } from 'react';

export default function LoadScenarioModal({ open, onClose, onLoad }) {
  const [json, setJson] = useState('');
  const [error, setError] = useState('');

  const handleLoad = () => {
    try {
      const data = JSON.parse(json);
      if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
        setError('JSON должен содержать поля nodes и edges (массивы)');
        return;
      }
      setError('');
      onLoad(data.nodes, data.edges);
      setJson('');
      onClose();
    } catch (e) {
      setError('Некорректный JSON');
    }
  };

  if (!open) return null;
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.25)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <div style={{ background: '#fff', borderRadius: 10, padding: 32, minWidth: 420, boxShadow: '0 4px 24px rgba(0,0,0,0.10)', position: 'relative' }}>
        <button onClick={onClose} type="button" style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 2 }} title="Закрыть">×</button>
        <h3>Загрузить сценарий из JSON</h3>
        <textarea
          value={json}
          onChange={e => setJson(e.target.value)}
          placeholder='Вставьте JSON с полями "nodes" и "edges"'
          style={{ width: '100%', minHeight: 200, fontFamily: 'monospace', marginBottom: 16, padding: 8, borderRadius: 6, border: '1px solid #ccc' }}
        />
        {error && <div style={{ color: '#f5222d', marginBottom: 10 }}>{error}</div>}
        <button
          onClick={handleLoad}
          style={{ width: '100%', padding: 10, borderRadius: 6, background: '#52c41a', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}
        >
          Загрузить
        </button>
      </div>
    </div>
  );
}