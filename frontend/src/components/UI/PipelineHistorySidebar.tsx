import { useState, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { GitBranch, X, CheckCircle, Loader2, MessageCircle, Clock, Search, Filter } from 'lucide-react';
import type { Plan } from '../../types';

type StatusFilter = 'all' | Plan['status'];

export function PipelineHistorySidebar() {
  const { sidebarOpen, pipelineHistoryOpen, togglePipelineHistory, plans, currentPlanId, setCurrentPlan, togglePipelinePanel } = useAgentStore();

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [showFilters, setShowFilters] = useState(false);

  const handlePlanClick = (planId: string) => {
    setCurrentPlan(planId);
    // Open PipelinePanel if not already open
    const { pipelinePanelOpen } = useAgentStore.getState();
    if (!pipelinePanelOpen) {
      togglePipelinePanel();
    }
  };

  // Calculate position: stack horizontally after Agent Sidebar
  const agentSidebarWidth = sidebarOpen ? 320 : 0;
  const sidebarLeft = agentSidebarWidth + 8;
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

  // Filter plans based on search and status
  const filteredPlans = useMemo(() => {
    return plans.filter(plan => {
      // Status filter
      if (statusFilter !== 'all' && plan.status !== statusFilter) return false;

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const titleMatch = (plan.title || '').toLowerCase().includes(query);
        if (!titleMatch) return false;
      }

      return true;
    });
  }, [plans, searchQuery, statusFilter]);

  // Calculate stats
  const stats = useMemo(() => {
    const total = plans.length;
    const completed = plans.filter(p => p.status === 'completed').length;
    const executing = plans.filter(p => p.status === 'executing').length;
    const discussing = plans.filter(p => p.status === 'discussing').length;
    return { total, completed, executing, discussing };
  }, [plans]);

  return (
    <>
      {/* Open button - shown when panel is closed */}
      {!pipelineHistoryOpen && (
        <button
          onClick={togglePipelineHistory}
          className="absolute z-20 p-2 bg-gray-800 rounded-r-lg text-white hover:bg-gray-700 transition-colors"
          style={{
            left: `${sidebarLeft}px`,
            top: '48px'
          }}
        >
          <GitBranch size={18} />
        </button>
      )}

      {/* Sidebar - position based on Agent Sidebar */}
      <div
        className={`absolute top-0 h-full bg-gray-800/95 backdrop-blur transition-all duration-300 z-10 ${
          pipelineHistoryOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        style={{
          left: `${sidebarLeft}px`,
          width: `${sidebarWidth}px`,
          transform: pipelineHistoryOpen ? 'translateX(0)' : `translateX(-${sidebarWidth + 10}px)`
        }}
      >
        {/* Close button - top right corner */}
        <button
          onClick={togglePipelineHistory}
          className="absolute top-3 right-3 z-20 p-2 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors"
        >
          <X size={18} />
        </button>

        <div className="h-full flex flex-col overflow-hidden pt-12">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-700 flex-shrink-0">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <GitBranch size={18} className="text-purple-400" />
                Pipeline 历史
              </h2>
              <span className="text-xs text-gray-400">
                {filteredPlans.length}/{plans.length}
              </span>
            </div>

            {/* Stats Mini Bar */}
            <div className="flex items-center gap-2 mt-2">
              <span className="text-[10px] px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded">
                {stats.completed} 完成
              </span>
              <span className="text-[10px] px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">
                {stats.executing} 执行中
              </span>
              <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/20 text-blue-400 rounded">
                {stats.discussing} 讨论中
              </span>
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="px-3 py-2 border-b border-gray-700 space-y-2">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="搜索 Pipeline..."
                  className="w-full pl-7 pr-2 py-1 bg-gray-700 rounded text-xs text-white placeholder-gray-500 border border-gray-600 focus:border-purple-500 focus:outline-none"
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
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`p-1 rounded transition-colors ${
                  showFilters || statusFilter !== 'all'
                    ? 'bg-purple-600 text-white'
                    : 'hover:bg-gray-700 text-gray-400'
                }`}
              >
                <Filter size={12} />
              </button>
            </div>

            {/* Status Filter Chips */}
            {showFilters && (
              <div className="flex flex-wrap gap-1">
                <button
                  onClick={() => setStatusFilter('all')}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                    statusFilter === 'all' ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  全部
                </button>
                <button
                  onClick={() => setStatusFilter('completed')}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                    statusFilter === 'completed' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  已完成
                </button>
                <button
                  onClick={() => setStatusFilter('executing')}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                    statusFilter === 'executing' ? 'bg-yellow-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  执行中
                </button>
                <button
                  onClick={() => setStatusFilter('discussing')}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                    statusFilter === 'discussing' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  讨论中
                </button>
                <button
                  onClick={() => setStatusFilter('draft')}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                    statusFilter === 'draft' ? 'bg-gray-500 text-white' : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  草稿
                </button>
              </div>
            )}
          </div>

          {/* Plan List */}
          <div className="flex-1 overflow-y-auto p-2">
            {filteredPlans.length === 0 ? (
              plans.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <GitBranch size={32} className="mb-2 opacity-30" />
                  <p className="text-sm">暂无 Pipeline</p>
                  <p className="text-xs text-gray-500 mt-1">点击顶部按钮创建</p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <Search size={24} className="mb-2 opacity-50" />
                  <p className="text-sm">未找到匹配的 Pipeline</p>
                  <button
                    onClick={() => { setSearchQuery(''); setStatusFilter('all'); }}
                    className="text-xs text-purple-400 hover:text-purple-300 mt-2"
                  >
                    清除筛选
                  </button>
                </div>
              )
            ) : (
              <div className="space-y-2">
                {filteredPlans.map((plan) => {
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
