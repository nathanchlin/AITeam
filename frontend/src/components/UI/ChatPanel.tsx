import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { Agent, Task, MessageReaction } from '../../types';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { X, Send, Loader2, Settings, Trash2, Check, Eraser, Copy, CheckCheck, Download, Brain, ChevronDown, ChevronRight, Search, FileText, Save } from 'lucide-react';
import { useAutoResize } from '../../hooks/useAutoResize';
import { MessageSearch } from './MessageSearch';
import { ReactionPicker, ReactionDisplay } from './ReactionPicker';
import { highlightCode, parseCodeBlocks } from '../../utils/syntaxHighlight';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

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
  const [showSearch, setShowSearch] = useState(false);
  const [editName, setEditName] = useState(agent.name);
  const [editDisplayType, setEditDisplayType] = useState(agent.display_type || '');
  const [editDescription, setEditDescription] = useState(agent.description || '');
  const [editPrompt, setEditPrompt] = useState(agent.custom_prompt || '');
  const [editTags, setEditTags] = useState<string[]>(agent.tags || []);
  const [newTagInput, setNewTagInput] = useState('');
  const [localStreamContent, setLocalStreamContent] = useState('');
  const [copiedTaskId, setCopiedTaskId] = useState<string | null>(null);
  const [expandedThinking, setExpandedThinking] = useState<Set<string>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<number | null>(null);
  const textareaRef = useAutoResize({ value: message, minHeight: 40, maxHeight: 200 });
  const [highlightedMessageId, setHighlightedMessageId] = useState<string | null>(null);
  const [taskReactions, setTaskReactions] = useState<Record<string, MessageReaction[]>>({});

  // Workspace file editing state
  const [workspaceFiles, setWorkspaceFiles] = useState<Record<string, string>>({});
  const [workspaceLoaded, setWorkspaceLoaded] = useState(false);
  const [workspaceSaving, setWorkspaceSaving] = useState<string | null>(null);
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<string>('IDENTITY.md');
  const workspaceTabs = ['IDENTITY.md', 'SOUL.md', 'USER.md', 'MEMORY.md'];

  const currentUserName = 'You';

  // Get reactions for a task
  const getReactions = (taskId: string): MessageReaction[] => {
    return taskReactions[taskId] || [];
  };

  // Handle add reaction
  const handleAddReaction = (taskId: string, emoji: string) => {
    setTaskReactions(prev => {
      const current = prev[taskId] || [];
      const existing = current.find(r => r.emoji === emoji);

      if (existing) {
        if (!existing.users.includes(currentUserName)) {
          return {
            ...prev,
            [taskId]: current.map(r =>
              r.emoji === emoji ? { ...r, users: [...r.users, currentUserName] } : r
            ),
          };
        }
        return prev;
      } else {
        return {
          ...prev,
          [taskId]: [...current, { emoji, users: [currentUserName] }],
        };
      }
    });
  };

  // Handle remove reaction
  const handleRemoveReaction = (taskId: string, emoji: string) => {
    setTaskReactions(prev => {
      const current = prev[taskId] || [];
      return {
        ...prev,
        [taskId]: current
          .map(r =>
            r.emoji === emoji ? { ...r, users: r.users.filter(u => u !== currentUserName) } : r
          )
          .filter(r => r.users.length > 0),
      };
    });
  };

  // Toggle reaction
  const handleToggleReaction = (taskId: string, emoji: string) => {
    const reactions = getReactions(taskId);
    const existing = reactions.find(r => r.emoji === emoji);
    if (existing && existing.users.includes(currentUserName)) {
      handleRemoveReaction(taskId, emoji);
    } else {
      handleAddReaction(taskId, emoji);
    }
  };

  // Quick prompts by agent type
  const getQuickPrompts = (type: string): string[] => {
    const prompts: Record<string, string[]> = {
      coder: ['帮我写一个函数...', '解释这段代码的作用', '优化这段代码', '写一个单元测试', '重构这段代码'],
      analyst: ['分析这组数据', '生成数据报告', '找出数据中的规律', '可视化建议'],
      assistant: ['帮我整理一下思路', '总结一下要点', '翻译成英文', '写一封邮件', '制定一个计划'],
      tester: ['写一个测试用例', '检查边界条件', '性能测试', '测试这个功能', '回归测试'],
      'pua-coder': ['用最高效的方式实现...', '严格审视代码质量', '确保零缺陷'],
      'pua-analyst': ['深度分析数据', '全面评估', '找出关键指标'],
      'pua-assistant': ['确保任务完成', '对结果负责', '闭环验证'],
      'pua-tester': ['穷尽所有测试场景', '验证每个边界', '确保质量'],
      custom: ['帮我设计一下', '给出建议', '优化方案'],
    };
    return prompts[type] || prompts.assistant || [];
  };

  const quickPrompts = getQuickPrompts(agent.type);

  // Jump to message handler
  const handleJumpToMessage = (messageId: string) => {
    const messageElement = messagesContainerRef.current?.querySelector(`[data-message-id="${messageId}"]`);
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setHighlightedMessageId(messageId);
      setTimeout(() => setHighlightedMessageId(null), 2000);
    }
  };

  // Format timestamp for display
  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

    if (isToday) {
      return timeStr;
    }
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) + ' ' + timeStr;
  };

  // Copy text to clipboard
  const handleCopy = async (text: string, taskId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedTaskId(taskId);
      setTimeout(() => setCopiedTaskId(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Get running task and completed tasks
  const runningTask = tasks.find((t) => t.status === 'running');
  const completedTasks = tasks.filter((t) => t.status === 'completed' && t.result);

  // Combine external stream content with local
  const streamContent = externalStreamContent || localStreamContent;

  // Auto-scroll when new content arrives
  useEffect(() => {
    // Only scroll within the container, not the whole page
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [streamContent, completedTasks.length]);

  // Sync edit state when agent changes
  useEffect(() => {
    setEditName(agent.name);
    setEditDisplayType(agent.display_type || '');
    setEditDescription(agent.description || '');
    setEditPrompt(agent.custom_prompt || '');
    setEditTags(agent.tags || []);
  }, [agent.id, agent.name, agent.display_type, agent.description, agent.custom_prompt, agent.tags]);

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
          display_type: editDisplayType || null,
          description: editDescription,
          custom_prompt: editPrompt,
          tags: editTags,
        }),
      });
      const updated = await res.json();
      updateAgent(agent.id, updated);
      setShowSettings(false);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  // Load workspace files when settings open
  useEffect(() => {
    if (showSettings && !workspaceLoaded) {
      (async () => {
        try {
          const res = await fetch(`${API_BASE}/api/agents/${agent.id}/workspace`);
          if (res.ok) {
            const data = await res.json();
            setWorkspaceFiles(data.files || {});
            setWorkspaceLoaded(true);
          }
        } catch (err) {
          console.error('Failed to load workspace:', err);
        }
      })();
    }
    if (!showSettings) {
      setWorkspaceLoaded(false);
    }
  }, [showSettings, agent.id]);

  const handleSaveWorkspaceFile = async (filename: string) => {
    const content = workspaceFiles[filename] || '';
    setWorkspaceSaving(filename);
    try {
      const res = await fetch(`${API_BASE}/api/agents/${agent.id}/workspace/${filename}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      if (!res.ok) {
        alert(`保存 ${filename} 失败`);
      }
    } catch (err) {
      console.error('Failed to save workspace file:', err);
      alert(`保存 ${filename} 失败`);
    } finally {
      setWorkspaceSaving(null);
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

  // Export chat history
  const handleExportChat = (format: 'json' | 'txt') => {
    const agentTasks = tasks.filter((t) => t.agent_id === agent.id && t.status === 'completed' && t.result);

    if (agentTasks.length === 0) {
      alert('No conversations to export');
      return;
    }

    let content: string;
    let filename: string;
    let mimeType: string;

    if (format === 'json') {
      const exportData = {
        agent: {
          name: agent.name,
          type: agent.type,
          display_type: agent.display_type,
        },
        exported_at: new Date().toISOString(),
        conversations: agentTasks.map(t => ({
          id: t.id,
          title: t.title,
          result: t.result,
          created_at: t.created_at,
          updated_at: t.updated_at,
        })),
      };
      content = JSON.stringify(exportData, null, 2);
      filename = `${agent.name.replace(/\s+/g, '_')}_chat_${new Date().toISOString().slice(0, 10)}.json`;
      mimeType = 'application/json';
    } else {
      // TXT format
      const lines = [
        `# Chat History with ${agent.name}`,
        `# Agent Type: ${getAgentDisplayType(agent)}`,
        `# Exported: ${new Date().toLocaleString()}`,
        '',
        '---',
        '',
      ];

      agentTasks.forEach((task, index) => {
        lines.push(`## Conversation ${index + 1}`);
        lines.push(`Date: ${task.created_at ? new Date(task.created_at).toLocaleString() : 'N/A'}`);
        lines.push('');
        lines.push(`**User:** ${task.title}`);
        lines.push('');
        lines.push(`**${agent.name}:**`);
        lines.push(task.result || '');
        lines.push('');
        lines.push('---');
        lines.push('');
      });

      content = lines.join('\n');
      filename = `${agent.name.replace(/\s+/g, '_')}_chat_${new Date().toISOString().slice(0, 10)}.txt`;
      mimeType = 'text/plain';
    }

    // Download file
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Render message content with code highlighting
  const renderMessageContent = (content: string) => {
    const parsedParts = parseCodeBlocks(content);
    const result: React.ReactNode[] = [];

    parsedParts.forEach((part, partIndex) => {
      if (part.type === 'code') {
        result.push(
          <div key={`code-${partIndex}`} className="my-2 relative group">
            <div className="flex items-center justify-between bg-gray-900 px-3 py-1 rounded-t-lg border-b border-gray-700">
              <span className="text-xs text-gray-400 font-mono">{part.language || 'code'}</span>
              <button
                onClick={() => navigator.clipboard.writeText(part.content)}
                className="text-gray-400 hover:text-white p-1 rounded transition-colors"
                title="复制代码"
              >
                <Copy size={12} />
              </button>
            </div>
            <pre className="bg-gray-900/80 p-3 rounded-b-lg overflow-x-auto text-sm font-mono">
              <code>{highlightCode(part.content, part.language || 'plaintext')}</code>
            </pre>
          </div>
        );
      } else if (part.type === 'inline-code') {
        result.push(
          <code
            key={`inline-${partIndex}`}
            className="bg-gray-700 text-pink-400 px-1.5 py-0.5 rounded text-sm font-mono"
          >
            {part.content}
          </code>
        );
      } else {
        result.push(part.content);
      }
    });

    return result.length > 0 ? result : content;
  };

  // Sort completed tasks by creation time (newest first)
  const sortedTasks = [...completedTasks].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="absolute bottom-4 right-4 w-[450px] h-[520px] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Global shimmer animation style */}
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>
      {/* Header */}
      <div className="p-3 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center shadow-lg"
            style={{ backgroundColor: AGENT_COLORS[agent.type]?.primary || '#6B7280' }}
          >
            <span className="text-white text-sm font-bold">
              {(agent.name || '?').charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="text-white text-sm font-bold">{agent.name}</h3>
            <p className="text-gray-400 text-xs flex items-center gap-2">
              <span>{getAgentDisplayType(agent)}</span>
              <span className={`w-2 h-2 rounded-full ${
                agent.status === 'working' ? 'bg-green-500 animate-pulse' :
                agent.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
              }`} />
              <span>{agent.status === 'working' ? '思考中...' : '在线'}</span>
            </p>
            {/* Task Progress Bar */}
            {agent.status === 'working' && (
              <div className="mt-1 w-32">
                <div className="h-1 bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: '100%',
                      background: 'linear-gradient(90deg, #3B82F6, #06B6D4, #3B82F6)',
                      backgroundSize: '200% 100%',
                      animation: 'shimmer 1.5s infinite linear'
                    }}
                  />
                </div>
              </div>
            )}
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
            onClick={() => setShowSearch(!showSearch)}
            disabled={completedTasks.length === 0}
            className={`p-2 rounded transition-colors ${
              showSearch ? 'bg-purple-600 text-white' : 'hover:bg-gray-700 text-gray-400'
            } disabled:opacity-30 disabled:cursor-not-allowed`}
            title="搜索消息"
          >
            <Search size={16} />
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
            <label className="text-gray-400 text-xs block mb-1">
              显示类型 <span className="text-gray-500">(如: UI设计师, 前端工程师)</span>
            </label>
            <input
              type="text"
              value={editDisplayType}
              onChange={(e) => setEditDisplayType(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="自定义显示类型..."
            />
            <p className="text-gray-500 text-xs mt-1">
              基础类型: <span className="text-gray-400">{agent.type}</span>
            </p>
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

          {/* Tags Section */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">标签</label>
            <div className="flex flex-wrap gap-1.5 mb-2">
              {editTags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs flex items-center gap-1"
                >
                  {tag}
                  <button
                    onClick={() => setEditTags(editTags.filter((_, i) => i !== index))}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newTagInput}
                onChange={(e) => setNewTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && newTagInput.trim()) {
                    e.preventDefault();
                    if (!editTags.includes(newTagInput.trim())) {
                      setEditTags([...editTags, newTagInput.trim()]);
                    }
                    setNewTagInput('');
                  }
                }}
                placeholder="输入标签后按 Enter 添加"
                className="flex-1 px-3 py-1.5 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
              <button
                onClick={() => {
                  if (newTagInput.trim() && !editTags.includes(newTagInput.trim())) {
                    setEditTags([...editTags, newTagInput.trim()]);
                  }
                  setNewTagInput('');
                }}
                className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-500 transition-colors"
              >
                添加
              </button>
            </div>
            <p className="text-gray-500 text-xs mt-1">
              标签可以帮助分类和筛选 Agent
            </p>
          </div>

          {/* Workspace Files Editor */}
          <div>
            <label className="text-gray-400 text-xs block mb-2 flex items-center gap-1">
              <FileText size={12} />
              Workspace 人格文件
            </label>

            {/* File Tabs */}
            <div className="flex gap-1 mb-2">
              {workspaceTabs.map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveWorkspaceTab(tab)}
                  className={`px-2.5 py-1.5 text-xs rounded-t transition-colors ${
                    activeWorkspaceTab === tab
                      ? 'bg-gray-700 text-white border-b-2 border-blue-500'
                      : 'text-gray-400 hover:text-gray-300 hover:bg-gray-700/50'
                  }`}
                >
                  {tab.replace('.md', '')}
                </button>
              ))}
            </div>

            {/* Editor Area */}
            <div className="relative">
              {workspaceLoaded ? (
                <>
                  <textarea
                    value={workspaceFiles[activeWorkspaceTab] || ''}
                    onChange={(e) =>
                      setWorkspaceFiles((prev) => ({
                        ...prev,
                        [activeWorkspaceTab]: e.target.value,
                      }))
                    }
                    className="w-full px-3 py-2 bg-gray-900 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none font-mono"
                    placeholder={`编辑 ${activeWorkspaceTab} 的内容...`}
                    rows={10}
                    spellCheck={false}
                  />
                  <div className="flex items-center justify-between mt-1.5">
                    <p className="text-gray-500 text-[10px]">
                      {activeWorkspaceTab === 'IDENTITY.md' && '定义 Agent 的名字、性格、沟通风格等人格信息'}
                      {activeWorkspaceTab === 'SOUL.md' && '定义 Agent 的角色、专业领域、方法论'}
                      {activeWorkspaceTab === 'USER.md' && '定义用户画像、偏好、项目背景'}
                      {activeWorkspaceTab === 'MEMORY.md' && 'Agent 的持久记忆，包含关键学习和经验'}
                    </p>
                    <button
                      onClick={() => handleSaveWorkspaceFile(activeWorkspaceTab)}
                      disabled={workspaceSaving === activeWorkspaceTab}
                      className="px-2.5 py-1 bg-blue-600/80 text-white rounded text-xs hover:bg-blue-500 transition-colors flex items-center gap-1 disabled:opacity-50"
                    >
                      {workspaceSaving === activeWorkspaceTab ? (
                        <Loader2 size={10} className="animate-spin" />
                      ) : (
                        <Save size={10} />
                      )}
                      保存
                    </button>
                  </div>
                </>
              ) : (
                <div className="w-full px-3 py-6 bg-gray-900/50 rounded text-center">
                  <Loader2 size={16} className="animate-spin text-gray-500 mx-auto mb-2" />
                  <p className="text-gray-500 text-xs">加载 Workspace 文件...</p>
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleDeleteAgent}
              className="px-3 py-2 bg-red-600/20 text-red-400 rounded hover:bg-red-600/30 transition-colors flex items-center gap-1 text-sm"
            >
              <Trash2 size={14} />
              删除
            </button>
            {/* Export Buttons */}
            <button
              onClick={() => handleExportChat('json')}
              className="px-3 py-2 bg-green-600/20 text-green-400 rounded hover:bg-green-600/30 transition-colors flex items-center gap-1 text-sm"
              title="Export as JSON"
            >
              <Download size={14} />
              JSON
            </button>
            <button
              onClick={() => handleExportChat('txt')}
              className="px-3 py-2 bg-blue-600/20 text-blue-400 rounded hover:bg-blue-600/30 transition-colors flex items-center gap-1 text-sm"
              title="Export as TXT"
            >
              <Download size={14} />
              TXT
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
          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-900/50 relative">
            {/* Completed conversations */}
            {sortedTasks.map((task) => (
              <div
                key={task.id}
                data-message-id={task.id}
                className={`space-y-2 transition-all duration-300 ${
                  highlightedMessageId === task.id ? 'ring-2 ring-purple-500 rounded-lg p-2 -m-2 bg-purple-500/10' : ''
                }`}
              >
                {/* User message */}
                <div className="group relative">
                  <div className="bg-gray-700/70 rounded-lg p-3 text-sm text-gray-300">
                    {task.title}
                  </div>
                  {task.created_at && (
                    <span className="absolute -bottom-4 right-2 text-[10px] text-gray-500">
                      {formatTimestamp(task.created_at)}
                    </span>
                  )}
                </div>
                {/* Thinking Process */}
                {task.thinking_process && task.thinking_process.length > 0 && (
                  <div className="mt-3 mb-2">
                    <button
                      onClick={() => {
                        const newSet = new Set(expandedThinking);
                        if (newSet.has(task.id)) {
                          newSet.delete(task.id);
                        } else {
                          newSet.add(task.id);
                        }
                        setExpandedThinking(newSet);
                      }}
                      className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-300 transition-colors"
                    >
                      <Brain size={12} className="text-purple-400" />
                      <span>思考过程</span>
                      {expandedThinking.has(task.id) ? (
                        <ChevronDown size={12} />
                      ) : (
                        <ChevronRight size={12} />
                      )}
                      <span className="text-gray-500">({task.thinking_process.length} 步)</span>
                    </button>
                    {expandedThinking.has(task.id) && (
                      <div className="mt-2 space-y-1.5 pl-3 border-l-2 border-purple-500/30">
                        {task.thinking_process.map((step, idx) => (
                          <div key={idx} className="text-xs">
                            <span className="text-purple-400 font-medium">步骤 {step.step}:</span>
                            <span className="text-gray-400 ml-1">{step.thought}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                {/* Agent response */}
                {task.result && (
                  <div className="group relative mt-5">
                    <div className="bg-gradient-to-r from-blue-600/30 to-purple-600/30 rounded-lg p-3 text-sm text-white border-l-2 border-blue-500">
                      {renderMessageContent(task.result)}
                    </div>
                    {/* Copy button */}
                    <button
                      onClick={() => handleCopy(task.result || '', task.id)}
                      className="absolute top-2 right-2 p-1.5 bg-gray-700/80 hover:bg-gray-600 rounded text-gray-400 hover:text-white opacity-0 group-hover:opacity-100 transition-all"
                      title={copiedTaskId === task.id ? '已复制' : '复制回复'}
                    >
                      {copiedTaskId === task.id ? (
                        <CheckCheck size={14} className="text-green-400" />
                      ) : (
                        <Copy size={14} />
                      )}
                    </button>
                    {/* Reaction button */}
                    <div className="absolute top-2 right-10 opacity-0 group-hover:opacity-100 transition-opacity">
                      <ReactionPicker
                        reactions={getReactions(task.id)}
                        currentUserName={currentUserName}
                        onAddReaction={(emoji) => handleAddReaction(task.id, emoji)}
                        onRemoveReaction={(emoji) => handleRemoveReaction(task.id, emoji)}
                        showTrigger={true}
                      />
                    </div>
                    {task.updated_at && (
                      <span className="absolute -bottom-4 right-2 text-[10px] text-gray-500">
                        {formatTimestamp(task.updated_at)}
                      </span>
                    )}
                    {/* Reaction display */}
                    {getReactions(task.id).length > 0 && (
                      <div className="mt-1 flex justify-end">
                        <ReactionDisplay
                          reactions={getReactions(task.id)}
                          currentUserName={currentUserName}
                          onToggleReaction={(emoji) => handleToggleReaction(task.id, emoji)}
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

            {/* Running task indicator */}
            {runningTask && (
              <div className="space-y-2">
                <div className="bg-gray-700/70 rounded-lg p-3 text-sm text-gray-300">
                  {runningTask.title}
                </div>
                {/* Typing indicator */}
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-700/50 rounded-lg w-fit">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-xs text-gray-400 ml-1">正在思考...</span>
                </div>
              </div>
            )}

            {/* Stream content */}
            {streamContent && (
              <div className="bg-gradient-to-r from-blue-600/30 to-purple-600/30 rounded-lg p-3 text-sm text-white border-l-2 border-green-500 animate-pulse">
                {renderMessageContent(streamContent)}
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
            {/* Quick Prompts */}
            {quickPrompts.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {quickPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setMessage(prompt)}
                    disabled={sending || agent.status === 'working'}
                    className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
            <div className="flex gap-2">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={agent.status === 'working' ? 'Agent 正在思考...' : '输入消息... (Enter 发送)'}
                className="flex-1 px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none overflow-y-auto"
                style={{ minHeight: '40px', maxHeight: '200px' }}
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

      {/* Message Search */}
      <MessageSearch
        isOpen={showSearch}
        onClose={() => setShowSearch(false)}
        messages={completedTasks.map(t => ({
          id: t.id,
          content: t.result || t.title,
          sender_name: t.title ? 'You' : agent.name,
          sender_type: t.result ? 'agent' : 'user',
          timestamp: t.updated_at || t.created_at || new Date().toISOString(),
        }))}
        onJumpToMessage={handleJumpToMessage}
        placeholder="搜索对话记录..."
      />
    </div>
  );
}
