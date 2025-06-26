import React, { useCallback, useRef, useState, useEffect } from 'react';
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
  { value: 'int', label: 'Число целое' },
  { value: 'decimal', label: 'Число дробное' },
  { value: 'date', label: 'Дата' },
  { value: 'time', label: 'Время' },
  { value: 'phone', label: 'Телефон' },
  { value: 'list', label: 'Список (через запятую)' },
  { value: 'bool', label: 'Галочка' },
  { value: 'file', label: 'Файл' },
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
          onDragStart={e => onDragStart(e, 'start')}
        >
          🚀 Старт
        </div>
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
          onDragStart={e => onDragStart(e, 'message')}
        >
          💬 Сообщение
        </div>
        <div
          style={{ marginBottom: 10, padding: 10, background: '#fff', borderRadius: 6, cursor: 'grab', border: '1px solid #bbb' }}
          draggable
          onDragStart={e => onDragStart(e, 'condition')}
        >
          🔀 Условие
        </div>
        <div
          style={{ marginBottom: 10, padding: 10, background: '#fff', borderRadius: 6, cursor: 'grab', border: '1px solid #bbb' }}
          draggable
          onDragStart={e => onDragStart(e, 'datawrite')}
        >
          📝 Запись данных
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
    setFields([...fields, { id: uuidv4(), name: '', type: 'string', hidden: false, required: false, default_value: '' }]);
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
            <input
              value={field.default_value}
              onChange={e => updateField(field.id, 'default_value', e.target.value)}
              placeholder="Значение по умолчанию"
              style={{ flex: 2, marginRight: 4, border: '1px solid #ccc', borderRadius: 4, padding: 2 }}
            />
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

function MessageNode({ id, data, selected }) {
const { updateNode, deleteNode } = data;
  const [text, setText] = useState(data.text || '');

  useEffect(() => {
    updateNode(id, { text });
    // eslint-disable-next-line
  }, [text]);

  return (
    <div style={{
      minWidth: 180,
      background: selected ? '#f6ffed' : '#fff',
      border: '2px solid #52c41a',
      borderRadius: 8,
      padding: 10,
      position: 'relative'
    }}>
      <button
        onClick={() => deleteNode(id)}
        style={{ position: 'absolute', top: 4, right: 4, border: 'none', background: 'none', cursor: 'pointer', color: '#f5222d', fontSize: 18 }}
        title="Удалить"
      >🗑️</button>
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Текст сообщения"
        style={{ width: '100%', minHeight: 60, border: '1px solid #ccc', borderRadius: 4, padding: 4 }}
      />
      <Handle type="source" position={Position.Right} />
      <Handle type="target" position={Position.Left} />
    </div>
  );
}

function ConditionNode({ id, data, selected }) {
  const { updateNode, deleteNode } = data;
  const [expression, setExpression] = useState(data.expression || '');

  useEffect(() => {
    updateNode(id, { expression });
    // eslint-disable-next-line
  }, [expression]);

  return (
    <div style={{
      minWidth: 200,
      background: selected ? '#fffbe6' : '#fff',
      border: '2px solid #faad14',
      borderRadius: 8,
      padding: 10,
      position: 'relative'
    }}>
      <button
        onClick={() => deleteNode(id)}
        style={{ position: 'absolute', top: 4, right: 4, border: 'none', background: 'none', cursor: 'pointer', color: '#f5222d', fontSize: 18 }}
        title="Удалить"
      >🗑️</button>
      <div style={{ fontWeight: 'bold', marginBottom: 6 }}>Условие</div>
      <input
        value={expression}
        onChange={e => setExpression(e.target.value)}
        placeholder="Введите выражение"
        style={{ width: '100%', border: '1px solid #ccc', borderRadius: 4, padding: 4, marginBottom: 8 }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <span style={{ color: '#52c41a', fontWeight: 500 }}>✔ Соблюдено</span>
        <span style={{ color: '#f5222d', fontWeight: 500 }}>✖ Не соблюдено</span>
      </div>
      <Handle type="source" position={Position.Right} id="true" style={{ top: 60, background: '#52c41a' }} />
      <Handle type="source" position={Position.Right} id="false" style={{ top: 90, background: '#f5222d' }} />
      <Handle type="target" position={Position.Left} />
    </div>
  );
}

function DataWriteNode({ id, data, selected }) {
  const { updateNode, deleteNode } = data;
  const [pairs, setPairs] = useState(data.pairs || []);

  // Добавить новую пару
  const addPair = () => {
    setPairs([...pairs, { id: uuidv4(), variable: '', value: '' }]);
  };

  // Удалить пару
  const removePair = (pid) => {
    setPairs(pairs.filter(p => p.id !== pid));
  };

  // Обновить пару
  const updatePair = (pid, key, value) => {
    setPairs(pairs.map(p => p.id === pid ? { ...p, [key]: value } : p));
  };

  // Сохранять изменения в React Flow
  useEffect(() => {
    updateNode(id, { pairs });
    // eslint-disable-next-line
  }, [pairs]);

  return (
    <div style={{
      minWidth: 220,
      background: selected ? '#fff0f6' : '#fff',
      border: '2px solid #eb2f96',
      borderRadius: 8,
      padding: 10,
      position: 'relative'
    }}>
      <button
        onClick={() => deleteNode(id)}
        style={{ position: 'absolute', top: 4, right: 4, border: 'none', background: 'none', cursor: 'pointer', color: '#f5222d', fontSize: 18 }}
        title="Удалить"
      >🗑️</button>
      <div style={{ fontWeight: 'bold', marginBottom: 8 }}>Запись данных</div>
      {pairs.map((pair, idx) => (
        <div key={pair.id} style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
          <input
            value={pair.variable}
            onChange={e => updatePair(pair.id, 'variable', e.target.value)}
            placeholder="Переменная"
            style={{ flex: 2, marginRight: 4, border: '1px solid #ccc', borderRadius: 4, padding: 2 }}
          />
          <input
            value={pair.value}
            onChange={e => updatePair(pair.id, 'value', e.target.value)}
            placeholder="Значение"
            style={{ flex: 2, marginRight: 4, border: '1px solid #ccc', borderRadius: 4, padding: 2 }}
          />
          <button onClick={() => removePair(pair.id)} style={{ color: '#f5222d', border: 'none', background: 'none', cursor: 'pointer' }}>✖</button>
        </div>
      ))}
      <button onClick={addPair} style={{ marginTop: 4, width: '100%' }}>+ Пара</button>
      <Handle type="source" position={Position.Right} />
      <Handle type="target" position={Position.Left} />
    </div>
  );
}

const nodeTypes = {
  form: FormNode,
  menu: MenuNode,
  start: StartNode,
  message: MessageNode,
  condition: ConditionNode,
  datawrite: DataWriteNode,
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
    } else if (type === 'message') {
      node = {
        id: uuidv4(),
        type: 'message',
        position,
        data: { text: '' },
      };
    } else if (type === 'condition') {
      node = {
        id: uuidv4(),
        type: 'condition',
        position,
        data: { expression: '' },
      };
    } else if (type === 'datawrite') {
      node = {
        id: uuidv4(),
        type: 'datawrite',
        position,
        data: { pairs: [] },
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