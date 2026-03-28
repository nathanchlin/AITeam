import { useState, useEffect } from 'react';
import { X, Gamepad2, Sparkles, ArrowLeft } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { ChatArea } from './VibeCodingPanel/ChatArea';
import { PreviewArea } from './VibeCodingPanel/PreviewArea';
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
    setStarting(true);

    try {
      // If current plan is completed, iterate on it instead of creating new one
      if (currentPlan && currentPlan.status === 'completed') {
        const res = await fetch(`${API_BASE}/api/pipeline/iterate/${currentPlan.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            iteration_request: request.trim(),
          }),
        });

        if (!res.ok) {
          const error = await res.json();
          console.error('Failed to start iteration:', error);
          return;
        }

        setRequest('');
      } else {
        // No completed plan — create a new one
        const res = await fetch(`${API_BASE}/api/pipeline/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request: request.trim(),
            target_output: 'web-app',
            skip_discussion: true,
          }),
        });

        if (!res.ok) {
          const error = await res.json();
          console.error('Failed to start pipeline:', error);
          return;
        }

        const data = await res.json();
        setVibeCodingPlanId(data.plan_id);
        setRequest('');
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

        {/* Chat Area */}
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
