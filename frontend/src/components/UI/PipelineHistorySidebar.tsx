import { useAgentStore } from '../../stores/agentStore';
import { GitBranch, X, CheckCircle, Loader2, MessageCircle, Clock } from 'lucide-react';
import type { Plan } from '../../types';

export function PipelineHistorySidebar() {
  const { sidebarOpen, pipelineHistoryOpen, togglePipelineHistory, plans, currentPlanId, setCurrentPlan, togglePipelinePanel } = useAgentStore();

  const handlePlanClick = (planId: string) => {
    setCurrentPlan(planId);
    // Open PipelinePanel if not already open
    const { pipelinePanelOpen } = useAgentStore.getState();
    if (!pipelinePanelOpen) {
      togglePipelinePanel();
    }
  };

  // Calculate position based on Agent Sidebar state
  const sidebarLeft = sidebarOpen ? 320 : 0;
  const sidebarWidth = 280;

  const getStatusIcon = (status: Plan['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={14} className="text-green-400" />;
      case 'executing':
        return <Loader2 size={14} className="text-yellow-400 animate-spin" />;
      case 'discussing':
        return <MessageCircle size={14} className="text-blue-400" />;
      default:
        return <div className="w-3.5 h-3.5 rounded-full bg-gray-400" />;
    }
  };

  const getStatusLabel = (status: Plan['status']) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'executing':
        return '执行中';
      case 'discussing':
        return '讨论中';
      case 'draft':
        return '草稿';
      case 'approved':
        return '已批准';
      default:
        return status;
    }
  };

  const getStatusColor = (status: Plan['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400';
      case 'executing':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'discussing':
        return 'bg-blue-500/20 text-blue-400';
      case 'approved':
        return 'bg-purple-500/20 text-purple-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  const getTaskProgress = (plan: Plan) => {
    if (!plan.tasks || plan.tasks.length === 0) return null;
    const completed = plan.tasks.filter(t => t.status === 'completed').length;
    const total = plan.tasks.length;
    const percentage = (completed / total) * 100;
    return { completed, total, percentage };
  };

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={togglePipelineHistory}
        className="absolute z-20 p-2 bg-gray-800 rounded-lg text-white hover:bg-gray-700 transition-colors"
        style={{
          left: `${sidebarLeft + (pipelineHistoryOpen ? sidebarWidth - 44 : 4)}px`,
          top: '56px',
          transition: 'left 300ms ease-in-out'
        }}
      >
        {pipelineHistoryOpen ? <X size={18} /> : <GitBranch size={18} />}
      </button>

      {/* Sidebar */}
      <div
        className={`absolute top-0 h-full bg-gray-800/95 backdrop-blur transition-all duration-300 z-10 ${
          pipelineHistoryOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{
          left: `${sidebarLeft}px`,
          width: `${sidebarWidth}px`,
        }}
      >
        <div className="h-full flex flex-col overflow-hidden pt-14">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-700 flex-shrink-0">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <GitBranch size={18} className="text-purple-400" />
              Pipeline 历史
            </h2>
            <p className="text-xs text-gray-400 mt-1">
              {plans.length} 个 Pipeline
            </p>
          </div>

          {/* Plan List */}
          <div className="flex-1 overflow-y-auto p-2">
            {plans.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <GitBranch size={32} className="mb-2 opacity-30" />
                <p className="text-sm">暂无 Pipeline</p>
                <p className="text-xs text-gray-500 mt-1">点击顶部按钮创建</p>
              </div>
            ) : (
              <div className="space-y-2">
                {plans.map((plan) => {
                  const progress = getTaskProgress(plan);
                  const isSelected = currentPlanId === plan.id;

                  return (
                    <div
                      key={plan.id}
                      onClick={() => handlePlanClick(plan.id)}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-purple-600/30 ring-2 ring-purple-500'
                          : 'bg-gray-700/50 hover:bg-gray-700'
                      }`}
                    >
                      {/* Top Row: Status Icon + Title */}
                      <div className="flex items-start gap-2">
                        <div className="flex-shrink-0 mt-0.5">
                          {getStatusIcon(plan.status)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-white truncate">
                            {plan.title || '未命名 Pipeline'}
                          </h3>
                        </div>
                      </div>

                      {/* Bottom Row: Badge + Time */}
                      <div className="flex items-center gap-2 mt-2 pl-5">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(plan.status)}`}>
                          {getStatusLabel(plan.status)}
                        </span>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Clock size={10} />
                          <span>{formatTime(plan.created_at)}</span>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      {progress && (
                        <div className="mt-2 pl-5">
                          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                            <span>任务进度</span>
                            <span>{progress.completed}/{progress.total}</span>
                          </div>
                          <div className="h-1.5 bg-gray-600 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-blue-400 rounded-full transition-all duration-300"
                              style={{ width: `${progress.percentage}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
