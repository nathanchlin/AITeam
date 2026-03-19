import { useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { X, Clock, CheckCircle, Trophy, TrendingUp, MessageCircle, Zap, Target, BarChart3 } from 'lucide-react';

interface AgentActivityPanelProps {
  onClose: () => void;
}

export function AgentActivityPanel({ onClose }: AgentActivityPanelProps) {
  const { agents, selectedAgentId, tasks, plans, agentStats } = useAgentStore();
  const selectedAgent = agents.find(a => a.id === selectedAgentId);
  const stats = selectedAgentId ? agentStats[selectedAgentId] : null;

  if (!selectedAgent) {
    return (
      <div className="fixed right-0 top-0 h-full w-80 bg-gray-800/95 backdrop-blur border-l border-gray-700 p-4 z-30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold">Agent Activity</h3>
          <button onClick={onClose} className="p-1 rounded hover:bg-gray-700 text-gray-400">
            <X size={18} />
          </button>
        </div>
        <p className="text-gray-400 text-sm">Select an agent to view activity</p>
      </div>
    );
  }

  // Get agent's tasks and discussion history
  const agentTasks = tasks.filter(t => t.agent_id === selectedAgentId);
  const completedTasks = agentTasks.filter(t => t.status === 'completed');
  const runningTasks = agentTasks.filter(t => t.status === 'running');
  const failedTasks = agentTasks.filter(t => t.status === 'failed');
  const pendingTasks = agentTasks.filter(t => t.status === 'pending');

  // Calculate task performance metrics
  const taskMetrics = useMemo(() => {
    const total = agentTasks.length;
    const completed = completedTasks.length;
    const failed = failedTasks.length;
    const successRate = total > 0 ? Math.round((completed / total) * 100) : 0;
    const failRate = total > 0 ? Math.round((failed / total) * 100) : 0;

    // Calculate average completion time if available
    const tasksWithDuration = completedTasks.filter(t => t.created_at && t.completed_at);
    const avgDuration = tasksWithDuration.length > 0
      ? tasksWithDuration.reduce((sum, t) => {
          const duration = new Date(t.completed_at!).getTime() - new Date(t.created_at).getTime();
          return sum + duration;
        }, 0) / tasksWithDuration.length
      : null;

    return {
      total,
      completed,
      failed,
      pending: pendingTasks.length,
      running: runningTasks.length,
      successRate,
      failRate,
      avgDuration,
    };
  }, [agentTasks, completedTasks, failedTasks, pendingTasks, runningTasks]);

  // Get discussions from plans where this agent participated
  const agentDiscussions = plans.flatMap(p =>
    (p.discussion || []).filter(d => d.agent_id === selectedAgentId)
  );

  const color = AGENT_COLORS[selectedAgent.type]?.primary || '#6B7280';

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-gray-800/95 backdrop-blur border-l border-gray-700 flex flex-col z-30">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: color }}
          >
            <span className="text-white font-bold">
              {selectedAgent.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="text-white font-semibold">{selectedAgent.name}</h3>
            <p className="text-gray-400 text-xs">{getAgentDisplayType(selectedAgent)}</p>
          </div>
        </div>
        <button onClick={onClose} className="p-2 rounded hover:bg-gray-700 text-gray-400">
          <X size={18} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Stats Overview */}
        {stats && (
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp size={16} className="text-blue-400" />
              <span className="text-white font-medium text-sm">Statistics</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-800 rounded p-2 text-center">
                <div className="text-yellow-400 font-bold text-lg">Lv.{stats.level}</div>
                <div className="text-gray-500 text-xs">Level</div>
              </div>
              <div className="bg-gray-800 rounded p-2 text-center">
                <div className="text-amber-400 font-bold text-lg">{stats.score}</div>
                <div className="text-gray-500 text-xs">Score</div>
              </div>
              <div className="bg-gray-800 rounded p-2 text-center">
                <div className="text-green-400 font-bold text-lg">{stats.tasks_completed}</div>
                <div className="text-gray-500 text-xs">Tasks</div>
              </div>
              <div className="bg-gray-800 rounded p-2 text-center">
                <div className="text-purple-400 font-bold text-lg">{stats.discussion_count}</div>
                <div className="text-gray-500 text-xs">Messages</div>
              </div>
            </div>
            {/* XP Bar */}
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>XP Progress</span>
                <span>{stats.xp} / {stats.xp_to_next_level}</span>
              </div>
              <div className="h-2 bg-gray-600 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-yellow-500 to-amber-400 rounded-full transition-all"
                  style={{ width: `${Math.min((stats.xp / stats.xp_to_next_level) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Task Performance Metrics */}
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 size={16} className="text-green-400" />
            <span className="text-white font-medium text-sm">Task Performance</span>
          </div>

          {/* Success Rate */}
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Target size={12} />
                <span>Success Rate</span>
              </div>
              <span className={`font-bold text-sm ${
                taskMetrics.successRate >= 80 ? 'text-green-400' :
                taskMetrics.successRate >= 50 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {taskMetrics.successRate}%
              </span>
            </div>
            <div className="h-2 bg-gray-600 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  taskMetrics.successRate >= 80 ? 'bg-gradient-to-r from-green-500 to-emerald-400' :
                  taskMetrics.successRate >= 50 ? 'bg-gradient-to-r from-yellow-500 to-amber-400' :
                  'bg-gradient-to-r from-red-500 to-orange-400'
                }`}
                style={{ width: `${taskMetrics.successRate}%` }}
              />
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="bg-gray-800 rounded p-2">
              <div className="text-white font-bold">{taskMetrics.total}</div>
              <div className="text-gray-500 text-[9px]">Total</div>
            </div>
            <div className="bg-gray-800 rounded p-2">
              <div className="text-green-400 font-bold">{taskMetrics.completed}</div>
              <div className="text-gray-500 text-[9px]">Done</div>
            </div>
            <div className="bg-gray-800 rounded p-2">
              <div className="text-yellow-400 font-bold">{taskMetrics.running}</div>
              <div className="text-gray-500 text-[9px]">Running</div>
            </div>
            <div className="bg-gray-800 rounded p-2">
              <div className={`font-bold ${taskMetrics.failed > 0 ? 'text-red-400' : 'text-gray-400'}`}>
                {taskMetrics.failed}
              </div>
              <div className="text-gray-500 text-[9px]">Failed</div>
            </div>
          </div>

          {/* Average Duration */}
          {taskMetrics.avgDuration && (
            <div className="mt-3 flex items-center justify-between text-xs">
              <span className="text-gray-400">Avg. Duration</span>
              <span className="text-blue-400">
                {taskMetrics.avgDuration < 60000
                  ? `${Math.round(taskMetrics.avgDuration / 1000)}s`
                  : taskMetrics.avgDuration < 3600000
                    ? `${Math.round(taskMetrics.avgDuration / 60000)}m`
                    : `${(taskMetrics.avgDuration / 3600000).toFixed(1)}h`}
              </span>
            </div>
          )}
        </div>

        {/* Current Status */}
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Zap size={16} className="text-yellow-400" />
            <span className="text-white font-medium text-sm">Current Status</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              selectedAgent.status === 'idle' ? 'bg-gray-400' :
              selectedAgent.status === 'working' ? 'bg-green-500 animate-pulse' :
              selectedAgent.status === 'waiting' ? 'bg-yellow-500' :
              'bg-red-500'
            }`} />
            <span className="text-gray-300 text-sm capitalize">{selectedAgent.status}</span>
          </div>
          {runningTasks.length > 0 && (
            <div className="mt-2 text-xs text-gray-400">
              Running {runningTasks.length} task(s)
            </div>
          )}
        </div>

        {/* Recent Activity Timeline */}
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Clock size={16} className="text-green-400" />
            <span className="text-white font-medium text-sm">Activity Timeline</span>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto">
            {completedTasks.length === 0 && agentDiscussions.length === 0 && (
              <p className="text-gray-500 text-xs">No recent activity</p>
            )}

            {/* Task completions */}
            {completedTasks.slice(0, 5).map((task) => (
              <div key={task.id} className="flex items-start gap-2 p-2 rounded hover:bg-gray-700/50">
                <div className="mt-1">
                  <CheckCircle size={14} className="text-green-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-gray-300 text-sm truncate">{task.title}</div>
                  <div className="text-gray-500 text-xs">
                    {task.completed_at ? new Date(task.completed_at).toLocaleDateString() : 'Completed'}
                  </div>
                </div>
              </div>
            ))}

            {/* Discussions */}
            {agentDiscussions.slice(0, 3).map((msg, i) => (
              <div key={msg.id || i} className="flex items-start gap-2 p-2 rounded hover:bg-gray-700/50">
                <div className="mt-1">
                  <MessageCircle size={14} className="text-purple-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-gray-300 text-sm truncate">{msg.content.slice(0, 50)}...</div>
                  <div className="text-gray-500 text-xs">
                    {new Date(msg.timestamp).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Achievements */}
        {stats && stats.achievements && stats.achievements.length > 0 && (
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Trophy size={16} className="text-yellow-400" />
              <span className="text-white font-medium text-sm">Achievements</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {stats.achievements.slice(0, 6).map((achievement, i) => (
                <div
                  key={i}
                  className="px-3 py-1.5 bg-yellow-500/20 rounded-full text-yellow-400 text-xs"
                >
                  {achievement}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
