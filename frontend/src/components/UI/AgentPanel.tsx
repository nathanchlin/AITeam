import { useState, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType, type Task } from '../../types';
import { X, Trash2, Edit2, Check, Loader2, TrendingUp, CheckCircle, Clock, AlertCircle, List, BarChart3, User, MousePointerClick, Plus, Sparkles } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

// Recent Tasks Section Component
function RecentTasksSection({ agentId, tasks }: { agentId: string; tasks: Task[] }) {
  const recentTasks = useMemo(() => {
    const agentTasks = tasks.filter(t => t.agent_id === agentId);
    // Sort by updated_at desc and take top 5
    return [...agentTasks]
      .sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
      .slice(0, 5);
  }, [agentId, tasks]);

  if (recentTasks.length === 0) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle size={10} className="text-green-400" />;
      case 'running': return <Loader2 size={10} className="text-blue-400 animate-spin" />;
      case 'failed': return <AlertCircle size={10} className="text-red-400" />;
      default: return <Clock size={10} className="text-gray-400" />;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="bg-gray-700/50 rounded-lg p-3 mb-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-xs font-medium flex items-center gap-1">
          <List size={12} />
          最近任务
        </span>
      </div>
      <div className="space-y-1.5">
        {recentTasks.map(task => (
          <div key={task.id} className="flex items-center gap-2 text-xs">
            {getStatusIcon(task.status)}
            <span className="text-gray-300 truncate flex-1">{task.title}</span>
            <span className="text-gray-500 text-[10px]">
              {formatTime(task.updated_at || task.created_at)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Task Activity Chart - shows completions over last 7 days
function TaskActivityChart({ agentId, tasks }: { agentId: string; tasks: Task[] }) {
  const activityData = useMemo(() => {
    const agentTasks = tasks.filter(t => t.agent_id === agentId && t.status === 'completed');
    const days: { label: string; count: number }[] = [];

    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);

      const count = agentTasks.filter(t => {
        const taskDate = new Date(t.updated_at || t.created_at);
        return taskDate >= date && taskDate < nextDate;
      }).length;

      const label = i === 0 ? '今天' : i === 1 ? '昨天' : `${date.getMonth() + 1}/${date.getDate()}`;
      days.push({ label, count });
    }

    return days;
  }, [agentId, tasks]);

  const maxCount = Math.max(...activityData.map(d => d.count), 1);

  return (
    <div className="bg-gray-700/50 rounded-lg p-3 mb-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-xs font-medium flex items-center gap-1">
          <BarChart3 size={12} />
          活动趋势 (7天)
        </span>
      </div>
      <div className="flex items-end gap-1 h-12">
        {activityData.map((day, i) => (
          <div key={i} className="flex-1 flex flex-col items-center">
            <div
              className="w-full bg-blue-500/60 rounded-t transition-all duration-300 hover:bg-blue-400"
              style={{ height: `${(day.count / maxCount) * 100}%`, minHeight: day.count > 0 ? '4px' : '2px' }}
              title={`${day.count} 个任务`}
            />
            <span className="text-[8px] text-gray-500 mt-0.5">{day.label}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-4 mt-2 text-[10px] text-gray-400">
        <span>总计: {activityData.reduce((sum, d) => sum + d.count, 0)} 个完成任务</span>
      </div>
    </div>
  );
}

export function AgentPanel() {
  const { agents, selectedAgentId, selectAgent, removeAgent, updateAgent, tasks } = useAgentStore();

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDisplayType, setEditDisplayType] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [saving, setSaving] = useState(false);

  // Calculate task statistics for this agent
  const taskStats = useMemo(() => {
    if (!selectedAgent) return { total: 0, completed: 0, pending: 0, running: 0, failed: 0, successRate: 0 };

    const agentTasks = tasks.filter(t => t.agent_id === selectedAgent.id);
    const total = agentTasks.length;
    const completed = agentTasks.filter(t => t.status === 'completed').length;
    const pending = agentTasks.filter(t => t.status === 'pending').length;
    const running = agentTasks.filter(t => t.status === 'running').length;
    const failed = agentTasks.filter(t => t.status === 'failed').length;
    const finishedTasks = completed + failed;
    const successRate = finishedTasks > 0 ? Math.round((completed / finishedTasks) * 100) : 0;

    return { total, completed, pending, running, failed, successRate };
  }, [tasks, selectedAgent]);

  if (!selectedAgent) {
    return (
      <div className="w-80 h-full bg-gray-800/95 backdrop-blur border-l border-gray-700 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-full bg-gray-700/50 flex items-center justify-center mb-4 animate-float">
          <User size={32} className="text-gray-500" />
        </div>
        <h3 className="text-white font-semibold mb-2">选择一个 Agent</h3>
        <p className="text-gray-400 text-sm mb-6 leading-relaxed">
          从左侧列表中选择一个 Agent<br />查看详情和管理任务
        </p>
        <div className="space-y-3 w-full max-w-[200px]">
          <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-700/30 rounded-lg p-2">
            <MousePointerClick size={14} className="text-blue-400" />
            <span>点击 Agent 卡片选中</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-700/30 rounded-lg p-2">
            <Plus size={14} className="text-green-400" />
            <span>点击 + 创建新 Agent</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-700/30 rounded-lg p-2">
            <Sparkles size={14} className="text-purple-400" />
            <span>双击 Agent 开始聊天</span>
          </div>
        </div>
        {agents.length === 0 && (
          <div className="mt-6 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p className="text-yellow-400 text-xs">
              还没有 Agent，点击左侧 + 按钮创建一个
            </p>
          </div>
        )}
      </div>
    );
  }

  const handleDelete = async () => {
    try {
      await fetch(`${API_BASE}/api/agents/${selectedAgent.id}`, {
        method: 'DELETE',
      });
      removeAgent(selectedAgent.id);
    } catch (error) {
      console.error('Failed to delete agent:', error);
    }
  };

  const startEditing = () => {
    setEditName(selectedAgent.name);
    setEditDisplayType(selectedAgent.display_type || '');
    setEditDescription(selectedAgent.description || '');
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setEditName('');
    setEditDisplayType('');
    setEditDescription('');
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/agents/${selectedAgent.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editName || undefined,
          display_type: editDisplayType || null,
          description: editDescription || null,
        }),
      });

      if (res.ok) {
        const updatedAgent = await res.json();
        updateAgent(selectedAgent.id, updatedAgent);
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Failed to update agent:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800/95 backdrop-blur rounded-lg p-4 z-10 min-w-80 max-w-md">
      {isEditing ? (
        // Edit Mode
        <div className="space-y-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white font-bold">Edit Agent</h3>
            <div className="flex gap-1">
              <button
                onClick={cancelEditing}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                disabled={saving}
              >
                <X size={16} className="text-gray-400" />
              </button>
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">Name</label>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="Agent name"
            />
          </div>

          {/* Display Type */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">
              Display Type <span className="text-gray-500">(e.g., UI设计师, 前端工程师)</span>
            </label>
            <input
              type="text"
              value={editDisplayType}
              onChange={(e) => setEditDisplayType(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="Custom display name (optional)"
            />
            <p className="text-gray-500 text-xs mt-1">
              Base type: <span className="text-gray-400">{selectedAgent.type}</span>
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">Description</label>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
              rows={2}
              placeholder="Agent description (optional)"
            />
          </div>

          {/* Save Button */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={cancelEditing}
              className="flex-1 px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 transition-colors text-sm flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Check size={14} />
                  Save
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        // View Mode
        <>
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: AGENT_COLORS[selectedAgent.type]?.primary || '#6B7280' }}
              >
                <span className="text-white font-bold">
                  {(selectedAgent.name || '?').charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h3 className="text-white font-bold">{selectedAgent.name}</h3>
                <p className="text-gray-400 text-sm">{getAgentDisplayType(selectedAgent)}</p>
              </div>
            </div>
            <div className="flex gap-1">
              <button
                onClick={startEditing}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                title="Edit agent"
              >
                <Edit2 size={16} className="text-gray-400" />
              </button>
              <button
                onClick={() => selectAgent(null)}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
              >
                <X size={16} className="text-gray-400" />
              </button>
              <button
                onClick={handleDelete}
                className="p-1 hover:bg-red-600 rounded transition-colors"
                title="Delete agent"
              >
                <Trash2 size={16} className="text-gray-400" />
              </button>
            </div>
          </div>

          {selectedAgent.description && (
            <p className="text-gray-300 text-sm mb-3">{selectedAgent.description}</p>
          )}

          {/* Task Statistics Section */}
          {taskStats.total > 0 && (
            <div className="bg-gray-700/50 rounded-lg p-3 mb-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-xs font-medium flex items-center gap-1">
                  <TrendingUp size={12} />
                  任务统计
                </span>
                <span className="text-gray-500 text-xs">{taskStats.total} 个任务</span>
              </div>
              <div className="grid grid-cols-4 gap-2">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-0.5">
                    <CheckCircle size={10} className="text-green-400" />
                    <span className="text-green-400 text-sm font-bold">{taskStats.completed}</span>
                  </div>
                  <span className="text-gray-500 text-[10px]">完成</span>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-0.5">
                    <Clock size={10} className="text-yellow-400" />
                    <span className="text-yellow-400 text-sm font-bold">{taskStats.pending}</span>
                  </div>
                  <span className="text-gray-500 text-[10px]">待处理</span>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-0.5">
                    <Loader2 size={10} className="text-blue-400 animate-spin" />
                    <span className="text-blue-400 text-sm font-bold">{taskStats.running}</span>
                  </div>
                  <span className="text-gray-500 text-[10px]">进行中</span>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-0.5">
                    <AlertCircle size={10} className="text-red-400" />
                    <span className="text-red-400 text-sm font-bold">{taskStats.failed}</span>
                  </div>
                  <span className="text-gray-500 text-[10px]">失败</span>
                </div>
              </div>
              {/* Success Rate Bar */}
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-500 text-[10px]">成功率</span>
                  <span className={`text-xs font-bold ${
                    taskStats.successRate >= 80 ? 'text-green-400' :
                    taskStats.successRate >= 50 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {taskStats.successRate}%
                  </span>
                </div>
                <div className="h-1.5 bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      taskStats.successRate >= 80 ? 'bg-green-500' :
                      taskStats.successRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${taskStats.successRate}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Recent Tasks Section */}
          {selectedAgent && (
            <>
              <RecentTasksSection agentId={selectedAgent.id} tasks={tasks} />
              <TaskActivityChart agentId={selectedAgent.id} tasks={tasks} />
            </>
          )}

          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-400">Status:</span>
            <span
              className={`px-2 py-0.5 rounded ${
                selectedAgent.status === 'idle'
                  ? 'bg-gray-600 text-gray-300'
                  : selectedAgent.status === 'working'
                  ? 'bg-green-600/50 text-green-300'
                  : selectedAgent.status === 'error'
                  ? 'bg-red-600/50 text-red-300'
                  : 'bg-yellow-600/50 text-yellow-300'
              }`}
            >
              {selectedAgent.status}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
