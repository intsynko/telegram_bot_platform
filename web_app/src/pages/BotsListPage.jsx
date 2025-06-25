import React, { useEffect, useState } from 'react';

export default function BotsListPage({ user }) {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    fetch('http://localhost:8000/api/bots/', {
      credentials: 'include',
    })
      .then(res => res.json())
      .then(data => {
        setBots(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Ошибка загрузки ботов');
        setLoading(false);
      });
  }, [user]);

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить бота?')) return;
    await fetch(`http://localhost:8000/api/bots/${id}/`, {
      method: 'DELETE',
      credentials: 'include',
    });
    setBots(bots => bots.filter(b => b.id !== id));
  };

  // TODO: добавить создание/редактирование бота (модалка или отдельная форма)

  if (!user) return <div style={{ margin: 40, textAlign: 'center' }}>Войдите, чтобы просматривать ботов.</div>;
  if (loading) return <div style={{ margin: 40, textAlign: 'center' }}>Загрузка...</div>;
  if (error) return <div style={{ margin: 40, color: 'red', textAlign: 'center' }}>{error}</div>;

  return (
    <div style={{ maxWidth: 900, margin: '40px auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>Мои боты</h2>
        <button style={{ padding: '8px 18px', borderRadius: 6, background: '#1890ff', color: '#fff', border: 'none', fontWeight: 600, fontSize: 16, cursor: 'pointer' }}>
          + Новый бот
        </button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        {bots.map(bot => (
          <div key={bot.id} style={{ background: '#f7f7f7', borderRadius: 10, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8 }}>{bot.name}</div>
            <div style={{ color: '#888', marginBottom: 12 }}>{bot.description || 'Без описания'}</div>
            <div style={{ marginTop: 'auto', display: 'flex', gap: 8 }}>
              <button style={{ padding: '4px 12px', borderRadius: 4, border: '1px solid #1890ff', background: '#fff', color: '#1890ff', cursor: 'pointer' }}>Редактировать</button>
              <button onClick={() => handleDelete(bot.id)} style={{ padding: '4px 12px', borderRadius: 4, border: '1px solid #f5222d', background: '#fff', color: '#f5222d', cursor: 'pointer' }}>Удалить</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 