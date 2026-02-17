import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { Agent, Task } from '../../types';
import { AGENT_COLORS, AGENT_LABELS } from '../../types';
import { X, Send, Loader2, Settings, Trash2, Check, Eraser } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

interface ChatPanelProps {
  agent: Agent;
  streamContent: string;
  tasks: Task[];
}

export function ChatPanel({ agent, streamContent: externalStreamContent, tasks }: ChatPanelProps) {
  const { selectAgent, updateAgent, removeAgent, updateTask, addTask, removeTask } = useAgentStore();
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [editName, setEditName] = useState(agent.name);
  const [editDescription, setEditDescription] = useState(agent.description || '');
  const [editPrompt, setEditPrompt] = useState(agent.custom_prompt || '');
  const [localStreamContent, setLocalStreamContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<number | null>(null);

  // Get running task and completed tasks
  const runningTask = tasks.find((t) => t.status === 'running');
  const completedTasks = tasks.filter((t) => t.status === 'completed' && t.result);

  // Combine external stream content with local
  const streamContent = externalStreamContent || localStreamContent;

  // Auto-scroll when new content arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [streamContent, completedTasks.length]);

  // Sync edit state when agent changes
  useEffect(() => {
    setEditName(agent.name);
    setEditDescription(agent.description || '');
    setEditPrompt(agent.custom_prompt || '');
  }, [agent.id, agent.name, agent.description, agent.custom_prompt]);

  // Poll for task updates when there's a running task
  useEffect(() => {
    if (runningTask) {
      const pollTask = async () => {
        try {
          const res = await fetch(`${API_BASE}/api/tasks/${runningTask.id}`);
          const task = await res.json();
          if (task.status === 'completed' && task.result) {
            updateTask(task.id, {
              status: 'completed',
              result: task.result,
              progress: 1,
            });
            setLocalStreamContent('');
          }
        } catch (e) {
          console.error('Poll error:', e);
        }
      };

      pollingRef.current = window.setInterval(pollTask, 2000);
      return () => {
        if (pollingRef.current) clearInterval(pollingRef.current);
      };
    }
  }, [runningTask?.id, updateTask]);

  const handleSend = async () => {
    if (!message.trim() || sending || agent.status === 'working') return;

    setSending(true);
    try {
      // Create a task for this message
      const taskRes = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: message.trim(),
          agent_id: agent.id,
        }),
      });
      const task = await taskRes.json();
      addTask(task);

      // Start the task
      await fetch(`${API_BASE}/api/tasks/${task.id}/start`, {
        method: 'POST',
      });

      // Update task status locally
      updateTask(task.id, { status: 'running' });

      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSaveSettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/agents/${agent.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editName,
          description: editDescription,
          custom_prompt: editPrompt,
        }),
      });
      const updated = await res.json();
      updateAgent(agent.id, updated);
      setShowSettings(false);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  const handleDeleteAgent = async () => {
    if (!confirm(`确定要删除 Agent "${agent.name}" 吗？`)) return;

    try {
      await fetch(`${API_BASE}/api/agents/${agent.id}`, {
        method: 'DELETE',
      });
      removeAgent(agent.id);
    } catch (error) {
      console.error('Failed to delete agent:', error);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm(`确定要清空 "${agent.name}" 的所有对话记录吗？`)) return;

    try {
      // Delete all tasks for this agent
      const agentTasks = tasks.filter((t) => t.agent_id === agent.id);
      for (const task of agentTasks) {
        await fetch(`${API_BASE}/api/tasks/${task.id}`, {
          method: 'DELETE',
        });
        removeTask(task.id);
      }
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  // Sort completed tasks by creation time (newest first)
  const sortedTasks = [...completedTasks].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="absolute bottom-4 right-4 w-[450px] h-[520px] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center shadow-lg"
            style={{ backgroundColor: AGENT_COLORS[agent.type].primary }}
          >
            <span className="text-white text-sm font-bold">
              {agent.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="text-white text-sm font-bold">{agent.name}</h3>
            <p className="text-gray-400 text-xs flex items-center gap-2">
              <span>{AGENT_LABELS[agent.type]}</span>
              <span className={`w-2 h-2 rounded-full ${
                agent.status === 'working' ? 'bg-green-500 animate-pulse' :
                agent.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
              }`} />
              <span>{agent.status === 'working' ? '思考中...' : '在线'}</span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleClearHistory}
            disabled={completedTasks.length === 0}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-yellow-400 disabled:opacity-30 disabled:cursor-not-allowed"
            title="清空对话记录"
          >
            <Eraser size={16} />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded transition-colors ${
              showSettings ? 'bg-blue-600 text-white' : 'hover:bg-gray-700 text-gray-400'
            }`}
            title="设置"
          >
            <Settings size={16} />
          </button>
          <button
            onClick={() => selectAgent(null)}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
            title="关闭"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings ? (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-800">
          <div>
            <label className="text-gray-400 text-xs block mb-1">名称</label>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-gray-400 text-xs block mb-1">描述</label>
            <input
              type="text"
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="Agent 描述..."
            />
          </div>

          <div>
            <label className="text-gray-400 text-xs block mb-1">自定义提示词 (System Prompt)</label>
            <textarea
              value={editPrompt}
              onChange={(e) => setEditPrompt(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
              placeholder="输入自定义的系统提示词来定制 Agent 的行为..."
              rows={6}
            />
            <p className="text-gray-500 text-xs mt-1">
              提示：设置自定义提示词可以改变 Agent 的行为方式和专业领域
            </p>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleDeleteAgent}
              className="px-3 py-2 bg-red-600/20 text-red-400 rounded hover:bg-red-600/30 transition-colors flex items-center gap-1 text-sm"
            >
              <Trash2 size={14} />
              删除
            </button>
            <div className="flex-1" />
            <button
              onClick={() => setShowSettings(false)}
              className="px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
            >
              取消
            </button>
            <button
              onClick={handleSaveSettings}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors flex items-center gap-1 text-sm"
            >
              <Check size={14} />
              保存
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Chat Content */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-900/50">
            {/* Completed conversations */}
            {sortedTasks.map((task) => (
              <div key={task.id} className="space-y-2">
                <div className="bg-gray-700/70 rounded-lg p-3 text-sm text-gray-300">
                  {task.title}
                </div>
                {task.result && (
                  <div className="bg-gradient-to-r from-blue-600/30 to-purple-600/30 rounded-lg p-3 text-sm text-white whitespace-pre-wrap border-l-2 border-blue-500">
                    {task.result}
                  </div>
                )}
              </div>
            ))}

            {/* Running task indicator */}
            {runningTask && (
              <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300">
                {runningTask.title}
              </div>
            )}

            {/* Stream content */}
            {streamContent && (
              <div className="bg-gradient-to-r from-blue-600/30 to-purple-600/30 rounded-lg p-3 text-sm text-white whitespace-pre-wrap border-l-2 border-green-500 animate-pulse">
                {streamContent}
              </div>
            )}

            {/* No messages placeholder */}
            {sortedTasks.length === 0 && !streamContent && !runningTask && (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <div className="text-5xl mb-3">💬</div>
                <p className="text-sm font-medium">开始和 {agent.name} 对话吧</p>
                <p className="text-xs text-gray-500 mt-1">输入问题或任务，Agent 会实时响应</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="p-3 border-t border-gray-700 bg-gray-800">
            <div className="flex gap-2">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={agent.status === 'working' ? 'Agent 正在思考...' : '输入消息... (Enter 发送)'}
                className="flex-1 px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                rows={2}
                disabled={sending || agent.status === 'working'}
              />
              <button
                onClick={handleSend}
                disabled={!message.trim() || sending || agent.status === 'working'}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
              >
                {sending || agent.status === 'working' ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Send size={18} />
                )}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
