import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, AGENT_LABELS } from '../../types';
import { X, Play, GitBranch, MessageCircle, CheckCircle, Loader2, Send } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

export function PipelinePanel() {
  const {
    pipelinePanelOpen,
    togglePipelinePanel,
    plans,
    currentPlanId,
    setCurrentPlan,
    discussionMessages,
    streamContent,
    agents,
  } = useAgentStore();

  const [request, setRequest] = useState('');
  const [targetOutput, setTargetOutput] = useState('web-app');
  const [starting, setStarting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentPlan = plans.find((p) => p.id === currentPlanId);
  const currentStream = currentPlanId ? streamContent[currentPlanId] || '' : '';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [discussionMessages.length, currentStream]);

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
        }),
      });
      const data = await res.json();
      console.log('Pipeline started:', data);
      setRequest('');
    } catch (error) {
      console.error('Failed to start pipeline:', error);
    } finally {
      setStarting(false);
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

  if (!pipelinePanelOpen) return null;

  return (
    <div className="absolute top-16 left-1/2 transform -translate-x-1/2 w-[700px] max-h-[600px] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
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
            placeholder="输入你的需求，例如：我需要做一个俄罗斯方块的游戏..."
            className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-purple-500 focus:outline-none resize-none"
            rows={3}
            disabled={starting}
          />
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
      <div className="flex-1 overflow-y-auto">
        {currentPlan ? (
          <div className="p-4 space-y-4">
            {/* Plan Status */}
            <div className="flex items-center gap-2">
              <span className={`text-sm font-medium ${getStatusColor(currentPlan.status)}`}>
                {getStatusLabel(currentPlan.status)}
              </span>
              <span className="text-xs text-gray-500">|</span>
              <span className="text-xs text-gray-400">{currentPlan.title}</span>
            </div>

            {/* Discussion Thread */}
            {discussionMessages.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <MessageCircle size={14} />
                  Agent 讨论
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {discussionMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`p-3 rounded border-l-2 ${getMessageTypeStyle(msg.message_type)}`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <div
                          className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                          style={{
                            backgroundColor: AGENT_COLORS[msg.agent_type as keyof typeof AGENT_COLORS]?.primary || '#888',
                          }}
                        >
                          {msg.agent_name.charAt(0)}
                        </div>
                        <span className="text-sm font-medium text-white">{msg.agent_name}</span>
                        <span className="text-xs text-gray-500">
                          {AGENT_LABELS[msg.agent_type as keyof typeof AGENT_LABELS] || msg.agent_type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tasks */}
            {currentPlan.tasks.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <CheckCircle size={14} />
                  执行计划
                </h3>
                <div className="space-y-2">
                  {currentPlan.tasks.map((task) => {
                    const assignedAgent = agents.find((a) => a.id === task.assigned_agent_id);
                    return (
                      <div
                        key={task.id}
                        className="p-3 bg-gray-700/50 rounded flex items-center gap-3"
                      >
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                            task.status === 'completed'
                              ? 'bg-green-500'
                              : task.status === 'running'
                              ? 'bg-yellow-500 animate-pulse'
                              : 'bg-gray-600'
                          }`}
                        >
                          {task.status === 'completed' ? '✓' : task.order}
                        </div>
                        <div className="flex-1">
                          <div className="text-sm text-white">{task.title}</div>
                          {assignedAgent && (
                            <div className="text-xs text-gray-400">
                              负责人: {assignedAgent.name}
                            </div>
                          )}
                        </div>
                        <div
                          className={`text-xs ${
                            task.status === 'completed'
                              ? 'text-green-400'
                              : task.status === 'running'
                              ? 'text-yellow-400'
                              : 'text-gray-500'
                          }`}
                        >
                          {task.status}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Stream Content */}
            {currentStream && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-300">实时输出</h3>
                <div className="p-3 bg-gray-900/50 rounded text-sm text-white whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {currentStream}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
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
                className={`px-3 py-1.5 rounded text-xs whitespace-nowrap transition-colors ${
                  currentPlanId === plan.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {plan.title.substring(0, 20)}...
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
