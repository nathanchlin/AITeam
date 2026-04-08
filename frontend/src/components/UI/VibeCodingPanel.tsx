import { useState, useEffect } from 'react';
import { X, Gamepad2, Sparkles, ArrowLeft, FileText, MessageSquare } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { ChatArea } from './VibeCodingPanel/ChatArea';
import { PreviewArea } from './VibeCodingPanel/PreviewArea';
import DeltaSpecViewer from './DeltaSpecViewer';  // Phase 2: Delta Spec 显示组件
import type { Plan } from '../../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

export function VibeCodingPanel() {
  const {
    vibeCodingPanelOpen,
    toggleVibeCodingPanel,
    plans,
    vibeCodingPlanId,
    setVibeCodingPlanId,
    clearDiscussion,
  } = useAgentStore();

  const [request, setRequest] = useState('');
  const [starting, setStarting] = useState(false);
  const [leftWidth, setLeftWidth] = useState(40);
  const [pendingMessages, setPendingMessages] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'chat' | 'specs'>('chat'); // 📋 Tab 切换状态

  const currentPlan = plans.find(p => p.id === vibeCodingPlanId) as Plan | undefined;

  // Clear pending messages once plan data arrives via WebSocket
  useEffect(() => {
    if (pendingMessages.length === 0) return;
    // For new plans: original_request arrived
    if (currentPlan?.original_request) {
      setPendingMessages(prev => prev.filter(msg => msg !== currentPlan.original_request));
    }
    // For iterations: iteration requests arrived
    if (currentPlan?.iterations) {
      const iterRequests = currentPlan.iterations.map(i => i.iteration_request);
      setPendingMessages(prev => prev.filter(msg => !iterRequests.includes(msg)));
    }
  }, [currentPlan?.original_request, currentPlan?.iterations]);

  const getPreviewUrl = (plan: Plan | undefined): string | null => {
    if (!plan) return null;
    if (plan.status === 'completed') {
      return `${API_BASE}/api/pipeline/output/${plan.id}/files/index.html`;
    }
    return null;
  };

  const previewUrl = getPreviewUrl(currentPlan);

  const handleStart = async () => {
    if (!request.trim() || starting) return;
    const msg = request.trim();
    setPendingMessages(prev => [...prev, msg]);
    setRequest('');
    setStarting(true);

    try {
      // If current plan exists, iterate on it instead of creating new one
      if (currentPlan) {
        const res = await fetch(`${API_BASE}/api/pipeline/iterate/${currentPlan.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            iteration_request: msg,
          }),
        });

        if (!res.ok) {
          const error = await res.json();
          console.error('Failed to start iteration:', error);
        }
      } else {
        // No completed plan — create a new one
        const res = await fetch(`${API_BASE}/api/pipeline/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request: msg,
            target_output: 'web-app',
          }),
        });

        if (!res.ok) {
          const error = await res.json();
          console.error('Failed to start pipeline:', error);
          return;
        }

        const data = await res.json();
        setVibeCodingPlanId(data.plan_id);
        clearDiscussion();
      }
    } catch (error) {
      console.error('Failed to start pipeline:', error);
    } finally {
      setStarting(false);
    }
  };

  const handleResize = (e: React.MouseEvent) => {
    e.preventDefault();

    const handleMouseMove = (e: MouseEvent) => {
      const container = document.querySelector('.vibe-coding-panel');
      if (!container) return;
      const containerRect = container.getBoundingClientRect();
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      setLeftWidth(Math.min(Math.max(newWidth, 25), 60));
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && vibeCodingPanelOpen) {
        toggleVibeCodingPanel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [vibeCodingPanelOpen, toggleVibeCodingPanel]);

  if (!vibeCodingPanelOpen) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-emerald-500';
      case 'executing': return 'bg-blue-500';
      case 'discussing': return 'bg-amber-500';
      case 'pending_approval': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'executing': return '生成中';
      case 'discussing': return '讨论中';
      case 'pending_approval': return '待确认';
      default: return status;
    }
  };

  return (
    <div className="vibe-coding-panel fixed inset-0 top-10 z-40 flex items-center justify-center p-4">
      {/* Main Container with border */}
      <div className="relative w-full h-full max-w-[1600px] flex rounded-2xl border border-gray-700/50 overflow-hidden shadow-2xl bg-gray-900">
        {/* Top-right action buttons */}
        <div className="absolute top-3 right-3 z-50 flex items-center gap-2">
          {currentPlan && (
            <button
              onClick={() => setVibeCodingPlanId(null)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white text-xs transition-all"
              title="返回历史"
            >
              <ArrowLeft size={14} />
              <span>返回历史</span>
            </button>
          )}
          <button
            onClick={toggleVibeCodingPanel}
            className="w-8 h-8 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white transition-all flex items-center justify-center"
            title="关闭 (Esc)"
          >
            <X size={16} />
          </button>
        </div>

        {/* Left side: Chat Area */}
        <div
          className="flex flex-col bg-gray-900"
          style={{ width: `${leftWidth}%`, minWidth: '320px', maxWidth: '600px' }}
        >
        {/* Header */}
        <div className="px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Gamepad2 size={18} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="text-base font-semibold text-white">游戏工坊</h2>
              </div>
              {currentPlan ? (
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={`w-1.5 h-1.5 rounded-full ${getStatusColor(currentPlan.status)} ${currentPlan.status === 'executing' ? 'animate-pulse' : ''}`} />
                  <span className="text-xs text-gray-400">{getStatusText(currentPlan.status)}</span>
                </div>
              ) : (
                <p className="text-xs text-gray-500 mt-0.5">AI 协作游戏生成</p>
              )}
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-gray-800">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
              activeTab === 'chat'
                ? 'text-pink-400 border-b-2 border-pink-500 bg-gray-800/30'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/20'
            }`}
          >
            <MessageSquare size={14} />
            <span>对话</span>
          </button>
          <button
            onClick={() => setActiveTab('specs')}
            disabled={!currentPlan?.specs}
            className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
              activeTab === 'specs'
                ? 'text-pink-400 border-b-2 border-pink-500 bg-gray-800/30'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/20'
            } ${!currentPlan?.specs ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <FileText size={14} />
            <span>规范文档</span>
            {currentPlan?.specs && <span className="w-1.5 h-1.5 rounded-full bg-green-500" />}
          </button>
        </div>

        {/* Content Area */}
        {activeTab === 'chat' ? (
          <ChatArea
            plan={currentPlan}
            plans={plans}
            request={request}
            setRequest={setRequest}
            onStart={handleStart}
            starting={starting}
            onSelectPlan={setVibeCodingPlanId}
            pendingMessages={pendingMessages}
          />
        ) : (
          <div className="flex-1 overflow-auto p-5">
            {/* 规范文档 */}
            {currentPlan?.specs ? (
              <div className="prose prose-invert prose-sm max-w-none">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-300">
                    主规范 (v{currentPlan.specs_version || 1})
                  </h3>
                  {currentPlan.deltas && currentPlan.deltas.length > 0 && (
                    <span className="text-xs text-orange-400">
                      待合并变更：{currentPlan.deltas.length}
                    </span>
                  )}
                </div>
                <pre className="whitespace-pre-wrap text-gray-300 text-sm font-mono bg-gray-800/50 p-4 rounded-lg border border-gray-700/50">
                  {currentPlan.specs}
                </pre>
                
                {/* Delta Spec 显示组件 */}
                {currentPlan.deltas && currentPlan.deltas.length > 0 && (
                  <div className="mt-4 border-t border-gray-700 pt-4">
                    <DeltaSpecViewer
                      deltas={currentPlan.deltas}
                      specsVersion={currentPlan.specs_version || 1}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-500">
                <FileText size={48} className="mb-3 opacity-50" />
                <p className="text-sm">规范文档将在讨论阶段自动生成</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Resizer */}
      <div
        className="w-px bg-gray-800 hover:bg-pink-500 cursor-col-resize transition-colors flex-shrink-0 group relative"
        onMouseDown={handleResize}
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-12 rounded-full bg-gray-700 group-hover:bg-pink-500 transition-colors" />
      </div>

      {/* Right side: Preview Area */}
      <div className="flex-1 flex flex-col bg-gray-900">
        {/* Preview Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gray-800 flex items-center justify-center">
              <Sparkles size={18} className="text-gray-400" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">预览</h2>
              <p className="text-xs text-gray-500">
                {currentPlan?.title || '游戏将在这里展示'}
              </p>
            </div>
          </div>
        </div>

        <PreviewArea
          previewUrl={previewUrl}
          planId={currentPlan?.id}
          plan={currentPlan}
          onBack={() => setVibeCodingPlanId(null)}
        />
      </div>
      </div>
    </div>
  );
}
