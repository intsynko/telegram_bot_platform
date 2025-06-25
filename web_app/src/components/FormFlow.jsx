import React, { useCallback, useRef, useState } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  Handle,
  Position,
  useReactFlow,
  ReactFlowProvider,
  applyNodeChanges,
  applyEdgeChanges,
} from 'reactflow';
import { v4 as uuidv4 } from 'uuid';
import 'reactflow/dist/style.css';
import ScenarioSelector from '../components/ScenarioSelector';

const FIELD_TYPES = [
  { value: 'string', label: 'Строка' },
  { value: 'int', label: 'Число' },
  { value: 'date', label: 'Дата' },
];

// --- СЛЕВА ПАНЕЛЬ ---
function Sidebar({ onDragStart, nodes, edges, setNodes, setEdges }) {
  const [showLoadModal, setShowLoadModal] = useState(false);

  return (
    <aside style={{ width: 180, padding: 10, background: '#f0f0f0', height: '100vh', borderRight: '1px solid #ddd' }}>
      {/* Селектор сценария и кнопка */}
      <ScenarioSelector
        nodes={nodes}
        edges={edges}
        setNodes={setNodes}
        setEdges={setEdges}
      />
      {/* Элементы для перетаскивания */}
      <div style={{ borderTop: '1px solid #eee', paddingTop: 14, marginTop: 10 }}>
        <div
          style={{ marginBottom: 10, padding: 10, background: '#fff', borderRadius: 6, cursor: 'grab', border: '1px solid #bbb' }}
          draggable
          onDragStart={e => onDragStart(e, 'form')}
        >
          ➕ Форма
        </div>
        <div
          style={{ marginBottom: 10, padding: 10, background: '#fff', borderRadius: 6, cursor: 'grab', border: '1px solid #bbb' }}
          draggable
          onDragStart={e => onDragStart(e, 'menu')}
        >
          ➕ Меню
        </div>
        <div
          style={{ marginBottom: 10, padding: 10, background: '#fff', borderRadius: 6, cursor: 'grab', border: '1px solid #bbb' }}
          draggable
          onDragStart={e => onDragStart(e, 'start')}
        >
          🚀 Старт
        </div>
      </div>
    </aside>
  );
}

// --- КАРТОЧКА ФОРМЫ ---
function FormNode({ id, data, selected }) {
  const { updateNode, deleteNode } = data;
  const [title, setTitle] = useState(data.label);
  const [fields, setFields] = useState(data.fields);

  // Добавить поле
  const addField = () => {
    setFields([...fields, { id: uuidv4(), name: '', type: 'string', hidden: false, required: false }]);
  };

  // Удалить поле
  const removeField = (fid) => {
    setFields(fields.filter(f => f.id !== fid));
  };

  // Обновить поле
  const updateField = (fid, key, value) => {
    setFields(fields.map(f => f.id === fid ? { ...f, [key]: value } : f));
  };

  // Сохранять изменения в React Flow
  React.useEffect(() => {
    updateNode(id, { label: title, fields });
    // eslint-disable-next-line
  }, [title, fields]);

  return (
    <div style={{
      minWidth: 220,
      background: selected ? '#e6f7ff' : '#fff',
      border: '2px solid #1890ff',
      borderRadius: 8,
      padding: 10,
      position: 'relative'
    }}>
      <button
        onClick={() => deleteNode(id)}
        style={{ position: 'absolute', top: 4, right: 4, border: 'none', background: 'none', cursor: 'pointer', color: '#f5222d', fontSize: 18, zIndex: 2 }}
        title="Удалить"
      >🗑️</button>
      <input
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="Название формы"
        style={{ width: '100%', fontWeight: 'bold', marginBottom: 8, border: '1px solid #ccc', borderRadius: 4, padding: 4 }}
      />
      <div>
        {fields.map((field, idx) => (
          <div key={field.id} style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <input
              value={field.name}
              onChange={e => updateField(field.id, 'name', e.target.value)}
              placeholder="Название поля"
              style={{ flex: 2, marginRight: 4, border: '1px solid #ccc', borderRadius: 4, padding: 2 }}
            />
            <select
              value={field.type}
              onChange={e => updateField(field.id, 'type', e.target.value)}
              style={{ flex: 1, marginRight: 4 }}
            >
              {FIELD_TYPES.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
            <label style={{ marginRight: 2 }}>
              <input
                type="checkbox"
                checked={field.hidden}
                onChange={e => updateField(field.id, 'hidden', e.target.checked)}
              /> Скрыть
            </label>
            <label style={{ marginRight: 2 }}>
              <input
                type="checkbox"
                checked={field.required}
                onChange={e => updateField(field.id, 'required', e.target.checked)}
              /> *
            </label>
            <button onClick={() => removeField(field.id)} style={{ color: '#f5222d', border: 'none', background: 'none', cursor: 'pointer' }}>✖</button>
          </div>
        ))}
        <button onClick={addField} style={{ marginTop: 4, width: '100%' }}>+ Поле</button>
      </div>
      <Handle type="source" position={Position.Right} />
      <Handle type="target" position={Position.Left} />
    </div>
  );
}

// --- КАРТОЧКА МЕНЮ ---
function MenuNode({ id, data, selected }) {
  const { updateNode, deleteNode } = data;
  const [title, setTitle] = useState(data.label);
  const [buttons, setButtons] = useState(data.buttons);

  // Добавить кнопку
  const addButton = () => setButtons([...buttons, { id: uuidv4(), label: '' }]);
  // Удалить кнопку
  const removeButton = (bid) => setButtons(buttons.filter(b => b.id !== bid));
  // Обновить кнопку
  const updateButton = (bid, value) => setButtons(buttons.map(b => b.id === bid ? { ...b, label: value } : b));

  React.useEffect(() => {
    updateNode(id, { label: title, buttons });
    // eslint-disable-next-line
  }, [title, buttons]);

  return (
    <div style={{
      minWidth: 180,
      background: selected ? '#fffbe6' : '#fff',
      border: '2px solid #faad14',
      borderRadius: 8,
      padding: 10,
      position: 'relative'
    }}>
      <button
        onClick={() => deleteNode(id)}
        style={{ position: 'absolute', top: 4, right: 4, border: 'none', background: 'none', cursor: 'pointer', color: '#f5222d', fontSize: 18, zIndex: 2 }}
        title="Удалить"
      >🗑️</button>
      <input
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="Название меню"
        style={{ width: '100%', fontWeight: 'bold', marginBottom: 8, border: '1px solid #ccc', borderRadius: 4, padding: 4 }}
      />
      <div>
        {buttons.map((btn, idx) => (
          <div key={btn.id} style={{ display: 'flex', alignItems: 'center', marginBottom: 4, position: 'relative' }}>
            <input
              value={btn.label}
              onChange={e => updateButton(btn.id, e.target.value)}
              placeholder="Текст кнопки"
              style={{ flex: 2, marginRight: 4, border: '1px solid #ccc', borderRadius: 4, padding: 2 }}
            />
            {/* Точка связывания для каждой кнопки */}
            <Handle type="source" position={Position.Right} id={`btn-${btn.id}`} style={{ top: '50%', transform: 'translateY(-50%)', background: '#faad14', right: -8 }} />
            <button onClick={() => removeButton(btn.id)} style={{ color: '#f5222d', border: 'none', background: 'none', cursor: 'pointer' }}>✖</button>
          </div>
        ))}
        <button onClick={addButton} style={{ marginTop: 4, width: '100%' }}>+ Кнопка</button>
      </div>
      <Handle type="target" position={Position.Left} />
    </div>
  );
}

// --- ДЕФОЛТНЫЙ БЛОК /start ---
function StartNode({ id, data }) {
  return (
    <div style={{
      minWidth: 120,
      background: '#e6f7ff',
      border: '2px solid #1890ff',
      borderRadius: 8,
      padding: 10,
      fontWeight: 'bold',
      textAlign: 'center'
    }}>
      /start
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = {
  form: FormNode,
  menu: MenuNode,
  start: StartNode,
};

function FlowCanvas() {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const { project } = useReactFlow();

  // --- Drag & Drop ---
  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;

    // Проверка координат
    if (typeof event.clientX !== 'number' || typeof event.clientY !== 'number') {
      alert('Ошибка: event.clientX или event.clientY не определены!');
      return;
    }
    if (typeof project !== 'function') {
      alert('Ошибка: project не функция!');
      return;
    }

    const position = project({
      x: event.clientX - 200,
      y: event.clientY,
    });

    // Проверка результата project
    if (!position || typeof position.x !== 'number' || typeof position.y !== 'number') {
      alert('Ошибка: position невалиден!');
      return;
    }

    let node;
    if (type === 'form') {
      node = {
        id: uuidv4(),
        type: 'form',
        position,
        data: { label: 'Новая форма', fields: [] },
      };
    } else if (type === 'menu') {
      node = {
        id: uuidv4(),
        type: 'menu',
        position,
        data: { label: 'Новое меню', buttons: [] },
      };
    } else if (type === 'start') {
      if (nodes.some(n => n.type === 'start')) return;
      node = {
        id: uuidv4(),
        type: 'start',
        position,
        data: {},
      };
    }
    if (node) setNodes(nds => nds.concat(node));
  }, [project, nodes]);

  // --- Drag Start ---
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  // --- Обновление данных узла ---
  const updateNode = (id, newData) => {
    setNodes(nds => nds.map(n => n.id === id ? { ...n, data: { ...n.data, ...newData } } : n));
  };

  // --- Удаление узла ---
  const deleteNode = (id) => {
    setNodes(nds => nds.filter(n => n.id !== id));
    setEdges(eds => eds.filter(e => e.source !== id && e.target !== id));
  };

  // --- Удаление связи (edge) ---
  const onEdgeClick = useCallback((event, edge) => {
    event.stopPropagation();
    setEdges(eds => eds.filter(e => e.id !== edge.id));
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar
        onDragStart={onDragStart}
        nodes={nodes}
        edges={edges}
        setNodes={setNodes}
        setEdges={setEdges}
      />
      <div style={{ flex: 1, height: '100vh' }} ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes.map(n => ({
            ...n,
            data: {
              ...n.data,
              updateNode,
              deleteNode,
            }
          }))}
          edges={edges}
          onNodesChange={changes => setNodes(nds => applyNodeChanges(changes, nds))}
          onEdgesChange={changes => setEdges(eds => applyEdgeChanges(changes, eds))}
          onConnect={params => setEdges(eds => eds.concat({ ...params, id: uuidv4() }))}
          nodeTypes={nodeTypes}
          onDrop={onDrop}
          onDragOver={onDragOver}
          fitView
          onEdgeClick={onEdgeClick}
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
}

export default function FormFlowApp() {
  return (
    <ReactFlowProvider>
      <FlowCanvas />
    </ReactFlowProvider>
  );
}