import { useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { Activity, CheckCircle, Clock, Loader2 } from 'lucide-react';

export function GlobalTaskIndicator() {
  const { tasks, toggleTaskPanel, taskPanelOpen } = useAgentStore();

  // Calculate task statistics
  const stats = useMemo(() => {
    const running = tasks.filter(t => t.status === 'running').length;
    const pending = tasks.filter(t => t.status === 'pending').length;
    const completed = tasks.filter(t => t.status === 'completed').length;
    const failed = tasks.filter(t => t.status === 'failed').length;
    const completionRate = tasks.length > 0 ? Math.round((completed / tasks.length) * 100) : 0;
    return { running, pending, completed, failed, total: tasks.length, completionRate };
  }, [tasks]);

  // Get current running task info
  const runningTask = useMemo(() => {
    const running = tasks.find(t => t.status === 'running');
    if (!running) return null;
    return {
      title: running.title.length > 20 ? running.title.slice(0, 20) + '...' : running.title,
      progress: running.progress || 0,
    };
  }, [tasks]);

  // Don't show if no tasks
  if (stats.total === 0) return null;

  return (
    <button
      onClick={toggleTaskPanel}
      className={`absolute top-2 left-[calc(50%-180px)] z-20 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-2 ${
        taskPanelOpen ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
      }`}
      title={`${stats.running} running, ${stats.pending} pending, ${stats.completed} completed`}
    >
      {/* Progress bar (mini) */}
      {stats.total > 0 && (
        <div className="w-12 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-blue-400 transition-all duration-300"
            style={{ width: `${stats.completionRate}%` }}
          />
        </div>
      )}

      {/* Completion rate */}
      <span className="text-xs text-gray-400">{stats.completionRate}%</span>

      <div className="w-px h-4 bg-gray-600" />

      {/* Running indicator with animation */}
      {stats.running > 0 && (
        <div className="flex items-center gap-1">
          <Loader2 size={14} className="text-green-400 animate-spin" />
          <span className="text-xs font-medium text-green-400">{stats.running}</span>
        </div>
      )}

      {/* Pending indicator */}
      {stats.pending > 0 && (
        <div className="flex items-center gap-1">
          <Clock size={14} className="text-yellow-400" />
          <span className="text-xs font-medium text-yellow-400">{stats.pending}</span>
        </div>
      )}

      {/* Completed indicator */}
      {stats.completed > 0 && (
        <div className="flex items-center gap-1">
          <CheckCircle size={14} className="text-blue-400" />
          <span className="text-xs font-medium text-blue-400">{stats.completed}</span>
        </div>
      )}

      {/* Running task name (if space available) */}
      {runningTask && (
        <span className="hidden lg:inline text-xs text-gray-500 max-w-[100px] truncate">
          {runningTask.title}
        </span>
      )}

      {/* Shortcut hint */}
      <kbd className="hidden md:inline-block px-1 py-0.5 text-[9px] bg-gray-700/50 rounded border border-gray-600 text-gray-500">T</kbd>

      {/* Activity pulse when running */}
      {stats.running > 0 && (
        <Activity size={12} className="text-green-400 animate-pulse" />
      )}
    </button>
  );
}
