import { useState, useMemo } from 'react';
import { parseUTCTime } from '../../utils/time';
import { useAgentStore } from '../../stores/agentStore';
import { X, TrendingUp, TrendingDown, Minus, Clock, CheckCircle, XCircle, Users, BarChart3, Activity, Zap, Target, Award, Play, History, PieChart } from 'lucide-react';
import { AGENT_COLORS } from '../../types';

interface DashboardPanelProps {
  onClose: () => void;
}

export function DashboardPanel({ onClose }: DashboardPanelProps) {
  const { agents, tasks, plans } = useAgentStore();
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'comparison' | 'pipelines' | 'timeline'>('overview');

  // Calculate statistics
  const stats = useMemo(() => {
    // Pipeline statistics
    const totalPlans = plans.length;
    const completedPlans = plans.filter(p => p.status === 'completed').length;
    const executingPlans = plans.filter(p => p.status === 'executing').length;
    const failedPlans = plans.filter(p =>
      p.tasks?.some(t => t.status === 'failed') &&
      p.status !== 'completed'
    ).length;
    const pipelineSuccessRate = totalPlans > 0 ? Math.round((completedPlans / totalPlans) * 100) : 0;

    // Task statistics
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const runningTasks = tasks.filter(t => t.status === 'running').length;
    const pendingTasks = tasks.filter(t => t.status === 'pending').length;
    const failedTasks = tasks.filter(t => t.status === 'failed').length;
    const taskCompletionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    // Calculate average task duration
    const completedTasksWithTime = tasks.filter(t =>
      t.status === 'completed' && t.started_at && t.completed_at
    );
    const avgTaskDuration = completedTasksWithTime.length > 0
      ? completedTasksWithTime.reduce((sum, t) => {
          const duration = new Date(t.completed_at!).getTime() - new Date(t.started_at!).getTime();
          return sum + duration;
        }, 0) / completedTasksWithTime.length / 1000
      : 0;

    // Agent statistics
    const activeAgents = agents.filter(a => a.status === 'working').length;
    const idleAgents = agents.filter(a => a.status === 'idle').length;

    // Agent task completion ranking
    const agentTaskCounts = agents.map(agent => {
      const agentTasks = tasks.filter(t => t.agent_id === agent.id);
      const completed = agentTasks.filter(t => t.status === 'completed').length;
      const total = agentTasks.length;
      return {
        agent,
        total,
        completed,
        failed: agentTasks.filter(t => t.status === 'failed').length,
        rate: total > 0 ? Math.round((completed / total) * 100) : 0
      };
    }).sort((a, b) => b.completed - a.completed);

    return {
      totalPlans,
      completedPlans,
      executingPlans,
      failedPlans,
      pipelineSuccessRate,
      totalTasks,
      completedTasks,
      runningTasks,
      pendingTasks,
      failedTasks,
      taskCompletionRate,
      avgTaskDuration,
      activeAgents,
      idleAgents,
      agentTaskCounts
    };
  }, [agents, tasks, plans]);

  // Build activity timeline
  const activityTimeline = useMemo(() => {
    interface ActivityEvent {
      id: string;
      type: 'task_started' | 'task_completed' | 'task_failed' | 'agent_working' | 'agent_idle';
      timestamp: string;
      agent_id?: string;
      agent_name: string;
      agent_type: string;
      task_title?: string;
      task_id?: string;
    }

    const events: ActivityEvent[] = [];

    // Process tasks for timeline events
    tasks.forEach(task => {
      const agent = agents.find(a => a.id === task.agent_id);
      const agentName = agent?.name || 'Unknown';
      const agentType = agent?.type || 'unknown';

      // Task started event
      if (task.started_at) {
        events.push({
          id: `${task.id}-started`,
          type: 'task_started',
          timestamp: task.started_at,
          agent_id: task.agent_id,
          agent_name: agentName,
          agent_type: agentType,
          task_title: task.title,
          task_id: task.id
        });
      }

      // Task completed event
      if (task.status === 'completed' && task.completed_at) {
        events.push({
          id: `${task.id}-completed`,
          type: 'task_completed',
          timestamp: task.completed_at,
          agent_id: task.agent_id,
          agent_name: agentName,
          agent_type: agentType,
          task_title: task.title,
          task_id: task.id
        });
      }

      // Task failed event
      if (task.status === 'failed') {
        events.push({
          id: `${task.id}-failed`,
          type: 'task_failed',
          timestamp: task.updated_at,
          agent_id: task.agent_id,
          agent_name: agentName,
          agent_type: agentType,
          task_title: task.title,
          task_id: task.id
        });
      }
    });

    // Sort by timestamp (most recent first)
    return events.sort((a, b) =>
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    ).slice(0, 20); // Show last 20 events
  }, [agents, tasks]);

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  };

  const getTrendIcon = (value: number, threshold: number = 50) => {
    if (value >= threshold + 20) return <TrendingUp size={14} className="text-green-400" />;
    if (value <= threshold - 20) return <TrendingDown size={14} className="text-red-400" />;
    return <Minus size={14} className="text-gray-400" />;
  };

  return (
    <div className="absolute bottom-4 right-4 w-[500px] h-[600px] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 bg-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 size={18} className="text-purple-400" />
          <h3 className="text-white text-sm font-bold">效能仪表盘</h3>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
        >
          <X size={16} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {[
          { id: 'overview', label: '概览', icon: Activity },
          { id: 'agents', label: 'Agent 排名', icon: Users },
          { id: 'comparison', label: '对比', icon: PieChart },
          { id: 'pipelines', label: 'Pipeline', icon: Target },
          { id: 'timeline', label: '时间线', icon: History }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={`flex-1 px-4 py-2 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors ${
              activeTab === tab.id
                ? 'text-purple-400 border-b-2 border-purple-400 bg-gray-800'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* KPI Cards */}
            <div className="grid grid-cols-2 gap-3">
              {/* Pipeline Success Rate */}
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">Pipeline 成功率</span>
                  {getTrendIcon(stats.pipelineSuccessRate)}
                </div>
                <div className="text-2xl font-bold text-white">{stats.pipelineSuccessRate}%</div>
                <div className="text-xs text-gray-500 mt-1">
                  {stats.completedPlans}/{stats.totalPlans} 已完成
                </div>
              </div>

              {/* Task Completion Rate */}
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">任务完成率</span>
                  {getTrendIcon(stats.taskCompletionRate)}
                </div>
                <div className="text-2xl font-bold text-white">{stats.taskCompletionRate}%</div>
                <div className="text-xs text-gray-500 mt-1">
                  {stats.completedTasks}/{stats.totalTasks} 已完成
                </div>
              </div>

              {/* Average Duration */}
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">平均任务耗时</span>
                  <Clock size={14} className="text-blue-400" />
                </div>
                <div className="text-2xl font-bold text-white">
                  {stats.avgTaskDuration > 0 ? formatDuration(stats.avgTaskDuration) : '--'}
                </div>
                <div className="text-xs text-gray-500 mt-1">基于已完成任务</div>
              </div>

              {/* Active Agents */}
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">活跃 Agent</span>
                  <Zap size={14} className="text-yellow-400" />
                </div>
                <div className="text-2xl font-bold text-white">
                  {stats.activeAgents}/{agents.length}
                </div>
                <div className="text-xs text-gray-500 mt-1">{stats.idleAgents} 空闲中</div>
              </div>
            </div>

            {/* Task Status Overview */}
            <div className="bg-gray-700/50 rounded-lg p-3">
              <h4 className="text-xs text-gray-400 mb-3">任务状态分布</h4>
              <div className="flex gap-2">
                <div className="flex-1 flex items-center gap-2 bg-green-500/20 rounded px-2 py-1.5">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-xs text-green-300">{stats.completedTasks} 完成</span>
                </div>
                <div className="flex-1 flex items-center gap-2 bg-blue-500/20 rounded px-2 py-1.5">
                  <Activity size={12} className="text-blue-400" />
                  <span className="text-xs text-blue-300">{stats.runningTasks} 运行</span>
                </div>
                <div className="flex-1 flex items-center gap-2 bg-yellow-500/20 rounded px-2 py-1.5">
                  <Clock size={12} className="text-yellow-400" />
                  <span className="text-xs text-yellow-300">{stats.pendingTasks} 等待</span>
                </div>
                <div className="flex-1 flex items-center gap-2 bg-red-500/20 rounded px-2 py-1.5">
                  <XCircle size={12} className="text-red-400" />
                  <span className="text-xs text-red-300">{stats.failedTasks} 失败</span>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="bg-gray-700/50 rounded-lg p-3">
              <h4 className="text-xs text-gray-400 mb-2">整体进度</h4>
              <div className="h-3 bg-gray-600 rounded-full overflow-hidden flex">
                {stats.totalTasks > 0 && (
                  <>
                    <div
                      className="bg-green-500 h-full transition-all"
                      style={{ width: `${(stats.completedTasks / stats.totalTasks) * 100}%` }}
                    />
                    <div
                      className="bg-blue-500 h-full transition-all"
                      style={{ width: `${(stats.runningTasks / stats.totalTasks) * 100}%` }}
                    />
                    <div
                      className="bg-red-500 h-full transition-all"
                      style={{ width: `${(stats.failedTasks / stats.totalTasks) * 100}%` }}
                    />
                  </>
                )}
              </div>
              <div className="flex justify-between mt-2 text-xs text-gray-500">
                <span>完成 {stats.taskCompletionRate}%</span>
                <span>剩余 {stats.pendingTasks + stats.runningTasks} 任务</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs text-gray-400">Agent 任务完成排名</h4>
              <Award size={14} className="text-yellow-400" />
            </div>
            {stats.agentTaskCounts.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Users size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">暂无 Agent 数据</p>
              </div>
            ) : (
              stats.agentTaskCounts.map((item, index) => {
                const agentColor = AGENT_COLORS[item.agent.type as keyof typeof AGENT_COLORS]?.primary || '#888';
                return (
                  <div
                    key={item.agent.id}
                    className="bg-gray-700/50 rounded-lg p-3 flex items-center gap-3"
                  >
                    <div className="text-lg font-bold text-gray-500 w-6">#{index + 1}</div>
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                      style={{ backgroundColor: agentColor }}
                    >
                      {item.agent.name.charAt(0)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white text-sm font-medium truncate">{item.agent.name}</span>
                        <span className="text-xs text-gray-400">({item.agent.type})</span>
                      </div>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-green-400">{item.completed} 完成</span>
                        {item.failed > 0 && (
                          <span className="text-xs text-red-400">{item.failed} 失败</span>
                        )}
                        <span className="text-xs text-gray-500">{item.total} 总计</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold" style={{ color: agentColor }}>
                        {item.rate}%
                      </div>
                      <div className="text-xs text-gray-500">完成率</div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-4">
            {/* Task Distribution Bar Chart */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs text-gray-400">任务分配对比</h4>
                <BarChart3 size={14} className="text-blue-400" />
              </div>
              {stats.agentTaskCounts.length === 0 ? (
                <div className="text-center text-gray-500 py-4">
                  <PieChart size={24} className="mx-auto mb-2 opacity-50" />
                  <p className="text-xs">暂无数据</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {stats.agentTaskCounts.map((item) => {
                    const maxTasks = Math.max(...stats.agentTaskCounts.map(a => a.total), 1);
                    const barWidth = (item.total / maxTasks) * 100;
                    return (
                      <div key={item.agent.id} className="flex items-center gap-2">
                        <div className="w-20 text-xs text-gray-300 truncate">{item.agent.name}</div>
                        <div className="flex-1 h-4 bg-gray-700 rounded overflow-hidden">
                          <div
                            className="h-full transition-all flex"
                            style={{ width: `${barWidth}%` }}
                          >
                            {/* Completed portion */}
                            <div
                              className="h-full bg-green-500"
                              style={{ width: `${item.total > 0 ? (item.completed / item.total) * 100 : 0}%` }}
                            />
                            {/* Failed portion */}
                            {item.failed > 0 && (
                              <div
                                className="h-full bg-red-500"
                                style={{ width: `${item.total > 0 ? (item.failed / item.total) * 100 : 0}%` }}
                              />
                            )}
                          </div>
                        </div>
                        <div className="w-8 text-xs text-right text-gray-400">{item.total}</div>
                      </div>
                    );
                  })}
                </div>
              )}
              {/* Legend */}
              <div className="flex items-center gap-4 mt-2 text-[10px]">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-green-500 rounded" />
                  <span className="text-gray-400">Completed</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-red-500 rounded" />
                  <span className="text-gray-400">Failed</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-gray-600 rounded" />
                  <span className="text-gray-400">Pending</span>
                </div>
              </div>
            </div>

            {/* Success Rate Comparison */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs text-gray-400">成功率对比</h4>
                <Award size={14} className="text-yellow-400" />
              </div>
              {stats.agentTaskCounts.length === 0 ? (
                <div className="text-center text-gray-500 py-4">
                  <p className="text-xs">暂无数据</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  {stats.agentTaskCounts.map((item, index) => {
                    const agentColor = AGENT_COLORS[item.agent.type as keyof typeof AGENT_COLORS]?.primary || '#888';
                    return (
                      <div
                        key={item.agent.id}
                        className="bg-gray-700/50 rounded-lg p-2"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <div
                            className="w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px] font-bold"
                            style={{ backgroundColor: agentColor }}
                          >
                            {item.agent.name.charAt(0)}
                          </div>
                          <span className="text-xs text-white truncate flex-1">{item.agent.name}</span>
                          {index === 0 && <Award size={10} className="text-yellow-400" />}
                        </div>
                        {/* Circular progress */}
                        <div className="flex items-center justify-center">
                          <div className="relative w-12 h-12">
                            <svg className="w-full h-full transform -rotate-90">
                              <circle
                                cx="24"
                                cy="24"
                                r="20"
                                fill="none"
                                stroke="#374151"
                                strokeWidth="4"
                              />
                              <circle
                                cx="24"
                                cy="24"
                                r="20"
                                fill="none"
                                stroke={item.rate >= 80 ? '#22c55e' : item.rate >= 50 ? '#eab308' : '#ef4444'}
                                strokeWidth="4"
                                strokeDasharray={`${item.rate * 1.256} 125.6`}
                                strokeLinecap="round"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
                              {item.rate}%
                            </div>
                          </div>
                        </div>
                        <div className="text-center mt-1 text-[10px] text-gray-400">
                          {item.completed}/{item.total} tasks
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Average Duration Comparison */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs text-gray-400">平均耗时对比</h4>
                <Clock size={14} className="text-orange-400" />
              </div>
              {stats.agentTaskCounts.length === 0 ? (
                <div className="text-center text-gray-500 py-4">
                  <p className="text-xs">暂无数据</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {stats.agentTaskCounts.map((item) => {
                    const agentTasks = tasks.filter(t => t.agent_id === item.agent.id && t.started_at && t.completed_at);
                    const avgDuration = agentTasks.length > 0
                      ? agentTasks.reduce((sum, t) => {
                          const duration = (new Date(t.completed_at!).getTime() - new Date(t.started_at!).getTime()) / 1000;
                          return sum + duration;
                        }, 0) / agentTasks.length
                      : 0;
                    const agentColor = AGENT_COLORS[item.agent.type as keyof typeof AGENT_COLORS]?.primary || '#888';
                    const maxDuration = Math.max(...stats.agentTaskCounts.map(a => {
                      const at = tasks.filter(t => t.agent_id === a.agent.id && t.started_at && t.completed_at);
                      return at.length > 0 ? at.reduce((s, t) => s + (new Date(t.completed_at!).getTime() - new Date(t.started_at!).getTime()) / 1000, 0) / at.length : 0;
                    }), 1);
                    const barWidth = (avgDuration / maxDuration) * 100;

                    return (
                      <div key={item.agent.id} className="flex items-center gap-2">
                        <div
                          className="w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px] font-bold"
                          style={{ backgroundColor: agentColor }}
                        >
                          {item.agent.name.charAt(0)}
                        </div>
                        <div className="flex-1 h-3 bg-gray-700 rounded overflow-hidden">
                          <div
                            className="h-full transition-all"
                            style={{
                              width: `${barWidth}%`,
                              backgroundColor: agentColor
                            }}
                          />
                        </div>
                        <div className="w-16 text-xs text-right text-gray-400">
                          {avgDuration < 60 ? `${avgDuration.toFixed(0)}s` : `${(avgDuration / 60).toFixed(1)}m`}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'pipelines' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs text-gray-400">Pipeline 状态概览</h4>
              <Target size={14} className="text-purple-400" />
            </div>
            {plans.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Target size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">暂无 Pipeline 数据</p>
              </div>
            ) : (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-3 gap-2 mb-3">
                  <div className="bg-green-500/20 rounded-lg p-2 text-center">
                    <div className="text-lg font-bold text-green-400">{stats.completedPlans}</div>
                    <div className="text-xs text-green-300">已完成</div>
                  </div>
                  <div className="bg-blue-500/20 rounded-lg p-2 text-center">
                    <div className="text-lg font-bold text-blue-400">{stats.executingPlans}</div>
                    <div className="text-xs text-blue-300">执行中</div>
                  </div>
                  <div className="bg-red-500/20 rounded-lg p-2 text-center">
                    <div className="text-lg font-bold text-red-400">{stats.failedPlans}</div>
                    <div className="text-xs text-red-300">失败</div>
                  </div>
                </div>

                {/* Recent Pipelines */}
                <h5 className="text-xs text-gray-500 mb-2">最近 Pipeline</h5>
                {plans.slice(0, 5).map(plan => {
                  const hasFailedTasks = plan.tasks?.some(t => t.status === 'failed');
                  const statusColor =
                    plan.status === 'completed' ? 'bg-green-500' :
                    plan.status === 'executing' ? 'bg-blue-500' :
                    hasFailedTasks ? 'bg-red-500' : 'bg-gray-500';
                  return (
                    <div
                      key={plan.id}
                      className="bg-gray-700/50 rounded-lg p-2 flex items-center gap-3"
                    >
                      <div className={`w-2 h-2 rounded-full ${statusColor}`} />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-white truncate">
                          {plan.original_request?.substring(0, 40)}...
                        </div>
                        <div className="text-xs text-gray-500">
                          {plan.tasks?.length || 0} 任务 · {plan.status}
                        </div>
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(plan.created_at).toLocaleDateString('zh-CN')}
                      </div>
                    </div>
                  );
                })}
              </>
            )}
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs text-gray-400">Agent 活动时间线</h4>
              <History size={14} className="text-blue-400" />
            </div>
            {activityTimeline.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <History size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">暂无活动记录</p>
              </div>
            ) : (
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-gray-700" />

                {activityTimeline.map((event) => {
                  const agentColor = AGENT_COLORS[event.agent_type as keyof typeof AGENT_COLORS]?.primary || '#888';

                  // Event type styling
                  const getEventStyle = () => {
                    switch (event.type) {
                      case 'task_started':
                        return { icon: Play, color: 'text-blue-400', bg: 'bg-blue-500/20' };
                      case 'task_completed':
                        return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/20' };
                      case 'task_failed':
                        return { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/20' };
                      default:
                        return { icon: Activity, color: 'text-gray-400', bg: 'bg-gray-500/20' };
                    }
                  };

                  const style = getEventStyle();
                  const EventIcon = style.icon;

                  // Format time
                  const formatEventTime = (timestamp: string) => {
                    const date = parseUTCTime(timestamp);
                    const now = new Date();
                    const diff = now.getTime() - date.getTime();
                    if (diff < 60000) return '刚刚';
                    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
                    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
                    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
                  };

                  // Get event description
                  const getEventDescription = () => {
                    switch (event.type) {
                      case 'task_started':
                        return '开始任务';
                      case 'task_completed':
                        return '完成任务';
                      case 'task_failed':
                        return '任务失败';
                      default:
                        return '活动';
                    }
                  };

                  return (
                    <div key={event.id} className="relative pl-8 pb-3">
                      {/* Timeline dot */}
                      <div
                        className={`absolute left-1.5 top-1.5 w-3 h-3 rounded-full ${style.bg} ${style.color} flex items-center justify-center`}
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-current" />
                      </div>

                      {/* Event card */}
                      <div className={`${style.bg} rounded-lg p-2`}>
                        <div className="flex items-center gap-2 mb-1">
                          <EventIcon size={12} className={style.color} />
                          <span className={`text-xs font-medium ${style.color}`}>
                            {getEventDescription()}
                          </span>
                          <span className="text-xs text-gray-500 ml-auto">
                            {formatEventTime(event.timestamp)}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div
                            className="w-5 h-5 rounded-full flex items-center justify-center text-white text-xs"
                            style={{ backgroundColor: agentColor }}
                          >
                            {event.agent_name.charAt(0)}
                          </div>
                          <span className="text-sm text-white truncate flex-1">
                            {event.task_title || 'Unknown Task'}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
