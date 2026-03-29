import { useState, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS } from '../../types';
import { X, Clock, CheckCircle, MessageCircle, User, Activity, Search, TrendingUp, Calendar, Download, FileText } from 'lucide-react';
import { parseUTCTime } from '../../utils/time';

interface ActivityLogPanelProps {
  onClose: () => void;
}

type ActivityType = 'task_completed' | 'status_change' | 'discussion';
type TimeRange = 'today' | 'week' | 'month' | 'all';

interface ActivityItem {
  id: string;
  type: ActivityType;
  agentId: string;
  agentName: string;
  agentType: string;
  timestamp: string;
  content: string;
}

export function ActivityLogPanel({ onClose }: ActivityLogPanelProps) {
  const { agents, tasks, plans } = useAgentStore();
  const [filterAgent, setFilterAgent] = useState<string>('all');
  const [filterType, setFilterType] = useState<ActivityType | 'all'>('all');
  const [timeRange, setTimeRange] = useState<TimeRange>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Build activity log from tasks and discussions
  const activities = useMemo(() => {
    const items: ActivityItem[] = [];

    // Task completions
    tasks.forEach(task => {
      if (task.status === 'completed' && task.completed_at) {
        const agent = agents.find(a => a.id === task.agent_id);
        if (agent) {
          items.push({
            id: `task-${task.id}`,
            type: 'task_completed',
            agentId: agent.id,
            agentName: agent.name,
            agentType: agent.type,
            timestamp: task.completed_at,
            content: `Completed task: ${task.title}`,
          });
        }
      }
    });

    // Status changes (from agent status)
    agents.forEach(agent => {
      if (agent.updated_at) {
        items.push({
          id: `status-${agent.id}-${agent.updated_at}`,
          type: 'status_change',
          agentId: agent.id,
          agentName: agent.name,
          agentType: agent.type,
          timestamp: agent.updated_at,
          content: `Status: ${agent.status}`,
        });
      }
    });

    // Discussion messages
    plans.forEach(plan => {
      (plan.discussion || []).forEach(msg => {
        items.push({
          id: `discussion-${msg.id}`,
          type: 'discussion',
          agentId: msg.agent_id,
          agentName: msg.agent_name,
          agentType: msg.agent_type,
          timestamp: msg.timestamp,
          content: msg.content.slice(0, 100) + (msg.content.length > 100 ? '...' : ''),
        });
      });
    });

    // Sort by timestamp (most recent first)
    items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return items;
  }, [tasks, agents, plans]);

  // Apply filters
  const filteredActivities = useMemo(() => {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthStart = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());

    return activities.filter(item => {
      // Agent filter
      if (filterAgent !== 'all' && item.agentId !== filterAgent) return false;

      // Type filter
      if (filterType !== 'all' && item.type !== filterType) return false;

      // Time range filter
      if (timeRange !== 'all') {
        const itemDate = new Date(item.timestamp);
        if (timeRange === 'today' && itemDate < todayStart) return false;
        if (timeRange === 'week' && itemDate < weekStart) return false;
        if (timeRange === 'month' && itemDate < monthStart) return false;
      }

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const nameMatch = item.agentName.toLowerCase().includes(query);
        const contentMatch = item.content.toLowerCase().includes(query);
        if (!nameMatch && !contentMatch) return false;
      }

      return true;
    });
  }, [activities, filterAgent, filterType, timeRange, searchQuery]);

  // Calculate time-based stats
  const stats = useMemo(() => {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    const today = activities.filter(a => new Date(a.timestamp) >= todayStart).length;
    const week = activities.filter(a => new Date(a.timestamp) >= weekStart).length;
    const tasks = activities.filter(a => a.type === 'task_completed').length;
    const discussions = activities.filter(a => a.type === 'discussion').length;

    return { today, week, tasks, discussions, total: activities.length };
  }, [activities]);

  const getActivityIcon = (type: ActivityType) => {
    switch (type) {
      case 'task_completed':
        return <CheckCircle size={14} className="text-green-400 animate-success-pop" />;
      case 'status_change':
        return <User size={14} className="text-blue-400 animate-status-pulse" />;
      case 'discussion':
        return <MessageCircle size={14} className="text-purple-400 animate-message-bounce" />;
    }
  };

  const getActivityBg = (type: ActivityType) => {
    switch (type) {
      case 'task_completed':
        return 'bg-green-500/10 border-green-500/30';
      case 'status_change':
        return 'bg-blue-500/10 border-blue-500/30';
      case 'discussion':
        return 'bg-purple-500/10 border-purple-500/30';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = parseUTCTime(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-gray-800/95 backdrop-blur border-l border-gray-700 flex flex-col z-30">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-blue-400" />
          <h3 className="text-white font-semibold">Activity Log</h3>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              const exportData = filteredActivities.map(a => ({
                agent: a.agentName,
                type: a.type,
                content: a.content,
                timestamp: a.timestamp,
              }));
              const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `activity-log-${new Date().toISOString().slice(0, 10)}.json`;
              link.click();
              URL.revokeObjectURL(url);
            }}
            className="p-2 rounded hover:bg-gray-700 text-gray-400 hover:text-white"
            title="导出活动日志"
          >
            <Download size={16} />
          </button>
          <button
            onClick={() => {
              const date = new Date().toISOString().slice(0, 10);
              let md = `# Activity Log - ${date}\n\n`;
              md += `## Summary\n\n`;
              md += `- Total Activities: ${filteredActivities.length}\n`;
              md += `- Agents: ${new Set(filteredActivities.map(a => a.agentName)).size}\n\n`;
              md += `---\n\n`;
              md += `## Activities\n\n`;
              const typeEmoji: Record<ActivityType, string> = {
                task_completed: '✅',
                status_change: '🔄',
                discussion: '💬',
              };
              filteredActivities.forEach(a => {
                const emoji = typeEmoji[a.type] || '📝';
                const time = new Date(a.timestamp).toLocaleString();
                md += `### ${emoji} ${a.agentName}\n`;
                md += `- **Type**: ${a.type}\n`;
                md += `- **Time**: ${time}\n`;
                md += `\n${a.content}\n\n`;
              });
              const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `activity-log-${date}.md`;
              link.click();
              URL.revokeObjectURL(url);
            }}
            className="p-2 rounded hover:bg-gray-700 text-gray-400 hover:text-white"
            title="导出为 Markdown"
          >
            <FileText size={16} />
          </button>
          <button onClick={onClose} className="p-2 rounded hover:bg-gray-700 text-gray-400">
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        {/* Search */}
        <div className="relative">
          <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索活动..."
            className="w-full pl-7 pr-2 py-1.5 bg-gray-700 rounded text-xs text-white placeholder-gray-500 border border-gray-600 focus:border-blue-500 focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
            >
              <X size={10} />
            </button>
          )}
        </div>

        {/* Time Range Chips */}
        <div className="flex items-center gap-1">
          <Calendar size={10} className="text-gray-500" />
          <button
            onClick={() => setTimeRange('today')}
            className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
              timeRange === 'today' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            今天
          </button>
          <button
            onClick={() => setTimeRange('week')}
            className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
              timeRange === 'week' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            本周
          </button>
          <button
            onClick={() => setTimeRange('month')}
            className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
              timeRange === 'month' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            本月
          </button>
          <button
            onClick={() => setTimeRange('all')}
            className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
              timeRange === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            全部
          </button>
        </div>

        {/* Agent & Type Filters */}
        <div className="flex gap-2">
          <select
            value={filterAgent}
            onChange={(e) => setFilterAgent(e.target.value)}
            className="flex-1 px-2 py-1.5 bg-gray-700 border border-gray-600 rounded text-white text-xs focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Agents</option>
            {agents.map(agent => (
              <option key={agent.id} value={agent.id}>{agent.name}</option>
            ))}
          </select>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as ActivityType | 'all')}
            className="flex-1 px-2 py-1.5 bg-gray-700 border border-gray-600 rounded text-white text-xs focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Types</option>
            <option value="task_completed">Tasks</option>
            <option value="status_change">Status</option>
            <option value="discussion">Discussions</option>
          </select>
        </div>

        {/* Stats Summary */}
        <div className="flex items-center gap-2 pt-1 border-t border-gray-700">
          <TrendingUp size={10} className="text-green-400" />
          <span className="text-[10px] text-gray-400">今日: <span className="text-green-400">{stats.today}</span></span>
          <span className="text-[10px] text-gray-400">本周: <span className="text-blue-400">{stats.week}</span></span>
          <span className="text-[10px] text-gray-400">任务: <span className="text-purple-400">{stats.tasks}</span></span>
          <span className="text-[10px] text-gray-400">讨论: <span className="text-orange-400">{stats.discussions}</span></span>
        </div>
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredActivities.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-8">
            No activity to display
          </div>
        ) : (
          <div className="space-y-3">
            {filteredActivities.slice(0, 50).map((item) => {
              const color = AGENT_COLORS[item.agentType as keyof typeof AGENT_COLORS]?.primary || '#6B7280';
              return (
                <div
                  key={item.id}
                  className={`p-3 rounded-lg border ${getActivityBg(item.type)}`}
                >
                  <div className="flex items-start gap-3">
                    {/* Agent Avatar */}
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: color }}
                    >
                      <span className="text-white text-xs font-bold">
                        {item.agentName.charAt(0).toUpperCase()}
                      </span>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-white text-sm font-medium">{item.agentName}</span>
                        {getActivityIcon(item.type)}
                      </div>
                      <p className="text-gray-300 text-xs">{item.content}</p>
                      <div className="flex items-center gap-1 mt-2 text-gray-500 text-xs">
                        <Clock size={10} />
                        <span>{formatTime(item.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-3 border-t border-gray-700 bg-gray-800/50">
        <div className="flex justify-between text-xs text-gray-400">
          <span>Total: {filteredActivities.length} activities</span>
          <span>Showing: {Math.min(filteredActivities.length, 50)}</span>
        </div>
      </div>
    </div>
  );
}
