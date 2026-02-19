import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, AGENT_LABELS } from '../../types';
import { X, Play, GitBranch, MessageCircle, CheckCircle, Loader2, Users, ExternalLink, Copy, Check, RotateCw, Trash2 } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

export function PipelinePanel() {
  const {
    pipelinePanelOpen,
    togglePipelinePanel,
    plans,
    currentPlanId,
    setCurrentPlan,
    streamContent,
    agents,
    updatePlan,
    setPlans,
  } = useAgentStore();

  const [request, setRequest] = useState('');
  const [targetOutput, setTargetOutput] = useState('web-app');
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([]);
  const [starting, setStarting] = useState(false);
  const [resuming, setResuming] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [restartMessage, setRestartMessage] = useState('');
  const [copiedUrl, setCopiedUrl] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<number | null>(null);

  const currentPlan = plans.find((p) => p.id === currentPlanId);
  const currentStream = currentPlanId ? streamContent[currentPlanId] || '' : '';

  // Get current running task info
  const runningTask = currentPlan?.tasks.find(t => t.status === 'running');
  const completedTasksCount = currentPlan?.tasks.filter(t => t.status === 'completed').length || 0;
  const totalTasks = currentPlan?.tasks.length || 0;

  // Get discussion messages from current plan (they're stored in the plan itself)
  const planDiscussions = currentPlan?.discussion || [];

  // Fetch all plans
  const fetchPlans = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/plans`);
      if (res.ok) {
        const plansData = await res.json();
        setPlans(plansData);
      }
    } catch (e) {
      console.error('Fetch plans error:', e);
    }
  };

  // Poll for plan updates when plan is active
  // Also polls when WebSocket is disconnected (fallback sync)
  useEffect(() => {
    if (currentPlanId && currentPlan && !['completed', 'draft'].includes(currentPlan.status)) {
      const pollPlan = async () => {
        try {
          const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
          if (res.ok) {
            const plan = await res.json();
            updatePlan(currentPlanId, plan);
          }
        } catch (e) {
          console.error('Poll plan error:', e);
        }
      };

      // Poll every 3 seconds when active
      pollingRef.current = window.setInterval(pollPlan, 3000);
      // Also poll immediately
      pollPlan();

      return () => {
        if (pollingRef.current) clearInterval(pollingRef.current);
      };
    }
  }, [currentPlanId, currentPlan?.status, updatePlan]);

  // Fallback: periodic sync even when status appears stuck (e.g., missed WebSocket updates)
  useEffect(() => {
    if (!currentPlanId || !currentPlan) return;
    if (['completed', 'draft'].includes(currentPlan.status)) return;

    // Check every 10 seconds if we need to sync
    const fallbackSync = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
        if (res.ok) {
          const serverPlan = await res.json();
          // If server shows completed but local doesn't, sync it
          if (serverPlan.status === 'completed' && currentPlan.status !== 'completed') {
            console.log('[PipelinePanel] Fallback sync detected completed status');
            updatePlan(currentPlanId, serverPlan);
          }
          // If server shows different task status, sync it
          const localRunningTasks = currentPlan.tasks.filter(t => t.status === 'running');
          if (localRunningTasks.length > 0) {
            const serverTaskMap = new Map(serverPlan.tasks.map((t: { id: string; status: string }) => [t.id, t.status]));
            for (const task of localRunningTasks) {
              const serverStatus = serverTaskMap.get(task.id);
              if (serverStatus === 'completed' && task.status === 'running') {
                console.log('[PipelinePanel] Fallback sync detected task completion');
                updatePlan(currentPlanId, serverPlan);
                break;
              }
            }
          }
        }
      } catch (e) {
        console.error('[PipelinePanel] Fallback sync error:', e);
      }
    };

    const fallbackInterval = window.setInterval(fallbackSync, 10000);
    return () => clearInterval(fallbackInterval);
  }, [currentPlanId, currentPlan, updatePlan]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [planDiscussions.length, currentStream]);

  const handleStartPipeline = async () => {
    if (!request.trim() || starting) return;

    setStarting(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request: request.trim(),
          target_output: targetOutput,
          selected_agent_ids: selectedAgentIds,
        }),
      });
      const data = await res.json();
      console.log('Pipeline started:', data);
      setCurrentPlan(data.plan_id);
      setRequest('');
      setSelectedAgentIds([]);

      // Immediately fetch the new plan to refresh the list
      await fetchPlans();
    } catch (error) {
      console.error('Failed to start pipeline:', error);
    } finally {
      setStarting(false);
    }
  };

  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgentIds(prev =>
      prev.includes(agentId)
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const selectAllAgents = () => {
    setSelectedAgentIds(agents.map(a => a.id));
  };

  const clearAgentSelection = () => {
    setSelectedAgentIds([]);
  };

  const handleResumePipeline = async () => {
    if (!currentPlanId || resuming) return;
    setResuming(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/resume/${currentPlanId}`, { method: 'POST' });
      if (res.ok) {
        await fetchPlans();
        const data = await res.json();
        console.log('Pipeline resumed:', data);
      }
    } catch (e) {
      console.error('Resume pipeline error:', e);
    } finally {
      setResuming(false);
    }
  };

  const handleRestartPipeline = async () => {
    if (!currentPlanId || restarting) return;
    if (!confirm('确定要重启该流水线吗？将清空当前任务与讨论，从需求分析重新开始。')) return;
    setRestarting(true);
    try {
      const url = `${API_BASE}/api/pipeline/restart/${currentPlanId}`;
      const res = await fetch(url, { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        // 先刷新列表，再单独拉取当前计划，确保 UI 拿到最新状态
        await fetchPlans();
        const planRes = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
        if (planRes.ok) {
          const updatedPlan = await planRes.json();
          updatePlan(currentPlanId, updatedPlan);
        }
        setRestartMessage('流水线已重启，正在重新分析需求…');
        setTimeout(() => setRestartMessage(''), 4000);
        console.log('Pipeline restarted:', data);
      } else {
        const msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || '重启失败');
        alert(msg);
      }
    } catch (e) {
      console.error('Restart pipeline error:', e);
      alert('重启失败：' + (e instanceof Error ? e.message : '网络或服务器错误'));
    } finally {
      setRestarting(false);
    }
  };

  const handleDeletePipeline = async () => {
    if (!currentPlanId || deleting) return;
    if (!confirm('确定要删除该流水线吗？删除后无法恢复。')) return;
    setDeleting(true);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchPlans();
        const remaining = plans.filter((p) => p.id !== currentPlanId);
        setCurrentPlan(remaining.length > 0 ? remaining[0].id : null);
        console.log('Pipeline deleted:', currentPlanId);
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || '删除失败');
      }
    } catch (e) {
      console.error('Delete pipeline error:', e);
      alert('删除失败');
    } finally {
      setDeleting(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'text-gray-400',
      discussing: 'text-yellow-400',
      approved: 'text-blue-400',
      executing: 'text-green-400',
      completed: 'text-green-500',
    };
    return colors[status] || 'text-gray-400';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      draft: '草稿',
      discussing: '讨论中',
      approved: '已批准',
      executing: '执行中',
      completed: '已完成',
    };
    return labels[status] || status;
  };

  const getStatusBgColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-500',
      discussing: 'bg-yellow-500',
      approved: 'bg-blue-500',
      executing: 'bg-green-500',
      completed: 'bg-green-600',
    };
    return colors[status] || 'bg-gray-500';
  };

  const getPhaseInfo = (status: string) => {
    const phases = [
      { key: 'draft', label: '需求分析', icon: '📋' },
      { key: 'discussing', label: '团队讨论', icon: '💬' },
      { key: 'approved', label: '计划确认', icon: '✅' },
      { key: 'executing', label: '执行开发', icon: '⚙️' },
      { key: 'completed', label: '完成交付', icon: '🎉' },
    ];
    const currentIndex = phases.findIndex(p => p.key === status);
    return { phases, currentIndex };
  };

  const getMessageTypeStyle = (type: string) => {
    const styles: Record<string, string> = {
      proposal: 'border-l-blue-500 bg-blue-500/10',
      question: 'border-l-yellow-500 bg-yellow-500/10',
      answer: 'border-l-green-500 bg-green-500/10',
      agreement: 'border-l-purple-500 bg-purple-500/10',
      comment: 'border-l-gray-500 bg-gray-500/10',
    };
    return styles[type] || styles.comment;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2000);
  };

  if (!pipelinePanelOpen) return null;

  const { phases, currentIndex } = getPhaseInfo(currentPlan?.status || 'draft');
  const outputUrl = currentPlan?.status === 'completed' ? `${API_BASE}/api/pipeline/output/${currentPlan.id}/files/index.html` : null;

  return (
    <div className="absolute top-16 left-1/2 transform -translate-x-1/2 w-[900px] max-h-[700px] bg-gray-900/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between bg-gray-800">
        <div className="flex items-center gap-3">
          <GitBranch size={20} className="text-purple-400" />
          <h2 className="text-white font-bold">协作流水线</h2>
          <span className="text-xs text-gray-400">讨论 → 计划 → 执行</span>
        </div>
        <button
          onClick={togglePipelinePanel}
          className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
        >
          <X size={16} />
        </button>
      </div>

      {/* Input Section */}
      <div className="p-4 border-b border-gray-700 bg-gray-800/50">
        <div className="space-y-3">
          <textarea
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            placeholder="输入你的需求，例如：我需要做一个贪吃蛇游戏..."
            className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-purple-500 focus:outline-none resize-none"
            rows={2}
            disabled={starting}
          />

          {/* Agent Selection */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">选择协作 Agent：</span>
              <div className="flex gap-2">
                <button
                  onClick={selectAllAgents}
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  全选
                </button>
                <span className="text-gray-600">|</span>
                <button
                  onClick={clearAgentSelection}
                  className="text-xs text-gray-400 hover:text-gray-300"
                >
                  清除
                </button>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {agents.map((agent) => {
                const isSelected = selectedAgentIds.includes(agent.id);
                const agentColor = AGENT_COLORS[agent.type as keyof typeof AGENT_COLORS]?.primary || '#888';
                return (
                  <button
                    key={agent.id}
                    onClick={() => toggleAgentSelection(agent.id)}
                    className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-all ${
                      isSelected
                        ? 'ring-2 ring-offset-1 ring-offset-gray-800'
                        : 'opacity-60 hover:opacity-100'
                    }`}
                    style={{
                      backgroundColor: isSelected ? agentColor : `${agentColor}40`,
                      color: isSelected ? 'white' : '#ccc',
                    }}
                  >
                    <div
                      className="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold"
                      style={{ backgroundColor: agentColor }}
                    >
                      {agent.name.charAt(0)}
                    </div>
                    <span>{agent.name}</span>
                    <span className="text-[10px] opacity-70">
                      ({AGENT_LABELS[agent.type as keyof typeof AGENT_LABELS] || agent.type})
                    </span>
                    {isSelected && (
                      <Check size={12} className="ml-0.5" />
                    )}
                  </button>
                );
              })}
            </div>
            {selectedAgentIds.length === 0 && (
              <p className="text-xs text-yellow-500">
                未选择 Agent，将使用所有可用 Agent
              </p>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">目标输出：</span>
              <select
                value={targetOutput}
                onChange={(e) => setTargetOutput(e.target.value)}
                className="px-2 py-1 bg-gray-700 rounded text-white text-xs border border-gray-600"
              >
                <option value="web-app">Web应用</option>
                <option value="api">API服务</option>
                <option value="report">分析报告</option>
                <option value="documentation">文档</option>
              </select>
            </div>
            <button
              onClick={handleStartPipeline}
              disabled={!request.trim() || starting}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {starting ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  启动中...
                </>
              ) : (
                <>
                  <Play size={16} />
                  启动流水线
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {currentPlan ? (
          <>
            {/* Progress Bar */}
            <div className="p-4 border-b border-gray-700 bg-gray-800/30">
              <div className="flex items-center justify-between mb-2">
                <span className={`text-sm font-medium ${getStatusColor(currentPlan.status)}`}>
                  {getStatusLabel(currentPlan.status)}
                </span>
                <div className="flex items-center gap-2 flex-wrap">
                  {totalTasks > 0 && (
                    <span className="text-xs text-gray-400">
                      任务进度: {completedTasksCount}/{totalTasks}
                    </span>
                  )}
                  {currentPlan.status === 'executing' && completedTasksCount < totalTasks && (
                    <button
                      onClick={handleResumePipeline}
                      disabled={resuming}
                      className="px-3 py-1 text-xs font-medium rounded bg-amber-600 hover:bg-amber-500 text-white disabled:opacity-50 flex items-center gap-1"
                    >
                      {resuming ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                      {resuming ? '恢复中...' : '继续执行'}
                    </button>
                  )}
                  <button
                    onClick={handleRestartPipeline}
                    disabled={restarting}
                    title="清空任务与讨论，从需求分析重新开始"
                    className="px-3 py-1 text-xs font-medium rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 flex items-center gap-1"
                  >
                    {restarting ? <Loader2 size={12} className="animate-spin" /> : <RotateCw size={12} />}
                    重启流水线
                  </button>
                  <button
                    onClick={handleDeletePipeline}
                    disabled={deleting}
                    title="删除该流水线，不可恢复"
                    className="px-3 py-1 text-xs font-medium rounded bg-red-600/80 hover:bg-red-500 text-white disabled:opacity-50 flex items-center gap-1"
                  >
                    {deleting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                    删除流水线
                  </button>
                </div>
              </div>

              {/* Phase Progress */}
              <div className="flex items-center gap-1 mb-3">
                {phases.map((phase, index) => (
                  <div key={phase.key} className="flex items-center flex-1">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-full text-sm transition-all ${
                        index <= currentIndex
                          ? `${getStatusBgColor(currentPlan.status)} text-white`
                          : 'bg-gray-700 text-gray-500'
                      } ${index === currentIndex ? 'ring-2 ring-white/30' : ''}`}
                    >
                      {index < currentIndex ? '✓' : phase.icon}
                    </div>
                    {index < phases.length - 1 && (
                      <div className={`flex-1 h-1 mx-1 rounded ${
                        index < currentIndex ? 'bg-green-500' : 'bg-gray-700'
                      }`} />
                    )}
                  </div>
                ))}
              </div>

              {/* Restart success hint */}
              {restartMessage && (
                <div className="flex items-center gap-2 p-2 bg-blue-500/10 rounded border border-blue-500/30">
                  <CheckCircle size={14} className="text-blue-400" />
                  <span className="text-sm text-blue-300">{restartMessage}</span>
                </div>
              )}
              {/* Current Activity */}
              {runningTask && (
                <div className="flex items-center gap-2 p-2 bg-green-500/10 rounded border border-green-500/30">
                  <Loader2 size={14} className="animate-spin text-green-400" />
                  <span className="text-sm text-green-300">
                    正在执行: {runningTask.title}
                  </span>
                </div>
              )}
            </div>

            {/* Main Content Area - Split View */}
            <div className="flex-1 flex overflow-hidden">
              {/* Left: Group Chat */}
              <div className="w-1/2 flex flex-col border-r border-gray-700">
                <div className="p-3 border-b border-gray-700 bg-gray-800/50 flex items-center gap-2">
                  <Users size={16} className="text-blue-400" />
                  <span className="text-sm font-medium text-white">团队群聊</span>
                  <span className="text-xs text-gray-500">({planDiscussions.length} 条消息)</span>
                </div>
                <div className="flex-1 overflow-y-auto p-3 space-y-2">
                  {planDiscussions.length > 0 ? (
                    planDiscussions.map((msg) => (
                      <div
                        key={msg.id}
                        className={`p-3 rounded border-l-2 ${getMessageTypeStyle(msg.message_type)}`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <div
                            className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                            style={{
                              backgroundColor: msg.agent_name === '系统' ? '#10B981' : (AGENT_COLORS[msg.agent_type as keyof typeof AGENT_COLORS]?.primary || '#888'),
                            }}
                          >
                            {msg.agent_name.charAt(0)}
                          </div>
                          <span className="text-sm font-medium text-white">{msg.agent_name}</span>
                          {msg.agent_name !== '系统' && (
                            <span className="text-xs text-gray-500">
                              {AGENT_LABELS[msg.agent_type as keyof typeof AGENT_LABELS] || msg.agent_type}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-300 whitespace-pre-wrap">{msg.content}</p>
                        {/* If message contains URL, make it clickable */}
                        {msg.content.includes('http://') && (
                          <div className="mt-2 flex gap-2">
                            {msg.content.match(/http:\/\/[^\s]+/g)?.map((url, i) => (
                              <a
                                key={i}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 px-2 py-1 bg-blue-600/30 hover:bg-blue-600/50 rounded text-xs text-blue-300 transition-colors"
                              >
                                <ExternalLink size={12} />
                                打开网页
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500">
                      <MessageCircle size={32} className="mb-2 opacity-30" />
                      <p className="text-sm">等待讨论开始...</p>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* Right: Agent Work Panels */}
              <div className="w-1/2 flex flex-col">
                <div className="p-3 border-b border-gray-700 bg-gray-800/50 flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-400" />
                  <span className="text-sm font-medium text-white">任务执行</span>
                </div>
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {/* Task List */}
                  {currentPlan.tasks.length > 0 ? (
                    <div className="space-y-2">
                      {currentPlan.tasks.map((task) => {
                        const assignedAgent = agents.find((a) => a.id === task.assigned_agent_id);
                        const isRunning = task.status === 'running';
                        const taskStream = streamContent[task.id] || '';

                        return (
                          <div
                            key={task.id}
                            className={`p-3 rounded border transition-all ${
                              isRunning
                                ? 'bg-green-500/10 border-green-500/50'
                                : task.status === 'completed'
                                ? 'bg-gray-700/30 border-gray-600'
                                : 'bg-gray-800/50 border-gray-700'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div
                                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                                  task.status === 'completed'
                                    ? 'bg-green-500'
                                    : isRunning
                                    ? 'bg-yellow-500 animate-pulse'
                                    : 'bg-gray-600'
                                }`}
                              >
                                {task.status === 'completed' ? '✓' : task.order}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="text-sm text-white truncate">{task.title}</div>
                                {assignedAgent && (
                                  <div className="flex items-center gap-1 mt-1">
                                    <div
                                      className="w-4 h-4 rounded-full flex items-center justify-center text-[10px]"
                                      style={{ backgroundColor: AGENT_COLORS[assignedAgent.type]?.primary || '#888' }}
                                    >
                                      {assignedAgent.name.charAt(0)}
                                    </div>
                                    <span className="text-xs text-gray-400">{assignedAgent.name}</span>
                                  </div>
                                )}
                              </div>
                              <div
                                className={`text-xs px-2 py-1 rounded ${
                                  task.status === 'completed'
                                    ? 'bg-green-500/20 text-green-400'
                                    : isRunning
                                    ? 'bg-yellow-500/20 text-yellow-400'
                                    : 'bg-gray-600/50 text-gray-400'
                                }`}
                              >
                                {task.status === 'completed' ? '完成' : isRunning ? '执行中' : '等待'}
                              </div>
                            </div>

                            {/* Show stream content for running task */}
                            {isRunning && taskStream && (
                              <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs text-gray-300 max-h-32 overflow-y-auto whitespace-pre-wrap border border-gray-700">
                                {taskStream.slice(-500)}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500">
                      <CheckCircle size={32} className="mb-2 opacity-30" />
                      <p className="text-sm">
                        {currentPlan.status === 'discussing' ? '计划生成中...' : '等待计划生成...'}
                      </p>
                      <p className="text-xs mt-1 text-gray-600">通常 1～2 分钟内完成，超时将自动使用兜底计划</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Final Result Section */}
            {currentPlan.status === 'completed' && outputUrl && (
              <div className="p-4 border-t border-gray-700 bg-green-900/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                      <CheckCircle size={20} className="text-white" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white">项目已完成</div>
                      <div className="text-xs text-gray-400">点击下方链接查看结果</div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => copyToClipboard(outputUrl)}
                      className="px-3 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors flex items-center gap-2 text-sm"
                    >
                      {copiedUrl ? <Check size={14} /> : <Copy size={14} />}
                      {copiedUrl ? '已复制' : '复制链接'}
                    </button>
                    <a
                      href={outputUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500 transition-colors flex items-center gap-2 text-sm"
                    >
                      <ExternalLink size={14} />
                      打开网页
                    </a>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
            <GitBranch size={48} className="mb-4 opacity-30" />
            <p className="text-sm">输入需求开始协作</p>
            <p className="text-xs text-gray-500 mt-1">
              Agents 将自动讨论、制定计划并执行
            </p>
          </div>
        )}
      </div>

      {/* Plans List */}
      {plans.length > 0 && (
        <div className="p-3 border-t border-gray-700 bg-gray-800/50">
          <div className="flex gap-2 overflow-x-auto">
            {plans.map((plan) => (
              <button
                key={plan.id}
                onClick={() => setCurrentPlan(plan.id)}
                className={`px-3 py-1.5 rounded text-xs whitespace-nowrap transition-colors flex items-center gap-2 ${
                  currentPlanId === plan.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${
                  plan.status === 'completed' ? 'bg-green-400' :
                  plan.status === 'executing' ? 'bg-yellow-400 animate-pulse' :
                  plan.status === 'discussing' ? 'bg-blue-400' : 'bg-gray-400'
                }`} />
                {plan.title.substring(0, 25)}...
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
