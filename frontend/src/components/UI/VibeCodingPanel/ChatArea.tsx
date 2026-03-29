import { useEffect, useRef } from 'react';
import { Send, Loader2, Bot, User, Sparkles, CheckCircle2, Clock, History, Gamepad2 } from 'lucide-react';
import type { Plan } from '../../../types';
import { AGENT_COLORS } from '../../../types';

const AGENT_LABELS_CN: Record<string, string> = {
  coder: '代码开发',
  analyst: '数据分析',
  assistant: '协调者',
  tester: '测试工程师',
  custom: '自定义',
  'pua-coder': 'PUA开发',
  'pua-analyst': 'PUA分析',
  'pua-assistant': 'PUA助手',
  'pua-tester': 'PUA测试',
};

interface ChatAreaProps {
  plan: Plan | undefined;
  plans: Plan[];
  request: string;
  setRequest: (value: string) => void;
  onStart: () => void;
  starting: boolean;
  onSelectPlan: (planId: string) => void;
  pendingMessages: string[];
}

const getAgentColor = (agentType: string): string => {
  const colors = AGENT_COLORS[agentType as keyof typeof AGENT_COLORS];
  return colors?.primary || '#6b7280';
};

export function ChatArea({ plan, plans, request, setRequest, onStart, starting, onSelectPlan, pendingMessages }: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [plan?.discussion, plan?.tasks, plan?.iterations, pendingMessages]);

  const handleSubmit = () => {
    if (!request.trim() || starting) return;
    onStart();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const completedTasks = plan?.tasks?.filter(t => t.status === 'completed') || [];
  const totalTasks = plan?.tasks?.length || 0;

  // Check if latest iteration is executing for progress bar
  const latestIteration = plan?.iterations?.[plan.iterations.length - 1];
  const iterationExecuting = latestIteration?.status === 'executing';
  const iterCompletedTasks = latestIteration?.tasks?.filter(t => t.status === 'completed') || [];
  const iterTotalTasks = latestIteration?.tasks?.length || 0;

  // Filter web-app plans for history, sorted by created_at descending
  const gamePlans = plans
    .filter(p => p.target_output === 'web-app')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const messages: Array<{
    id: string;
    type: 'user' | 'agent' | 'task';
    content: string;
    sender?: string;
    senderType?: string;
    timestamp: string;
    isStreaming?: boolean;
    status?: string;
  }> = [];

  if (plan?.original_request) {
    messages.push({
      id: 'user-request',
      type: 'user',
      content: plan.original_request,
      sender: '你',
      timestamp: plan.created_at || new Date().toISOString(),
    });
  }

  if (plan?.discussion && plan.discussion.length > 0) {
    plan.discussion.forEach((msg, idx) => {
      messages.push({
        id: msg.id || `discussion-${idx}`,
        type: 'agent',
        content: msg.content,
        sender: msg.agent_name,
        senderType: msg.agent_type,
        timestamp: msg.timestamp,
      });
    });
  }

  if (plan?.tasks) {
    plan.tasks.forEach((task) => {
      if (task.status === 'completed') {
        messages.push({
          id: `task-${task.id}`,
          type: 'task',
          content: `${task.title}`,
          status: 'completed',
          timestamp: new Date().toISOString(),
        });
      } else if (task.status === 'running') {
        messages.push({
          id: `task-${task.id}`,
          type: 'task',
          content: task.title,
          status: 'running',
          isStreaming: true,
          timestamp: new Date().toISOString(),
        });
      }
    });
  }

  // Show iteration rounds
  if (plan?.iterations && plan.iterations.length > 0) {
    plan.iterations.forEach((iter) => {
      // Iteration request as user message
      messages.push({
        id: `iter-request-${iter.round_number}`,
        type: 'user',
        content: iter.iteration_request,
        sender: '你',
        timestamp: iter.created_at,
      });

      // Iteration discussion
      if (iter.discussion && iter.discussion.length > 0) {
        iter.discussion.forEach((msg, idx) => {
          messages.push({
            id: msg.id || `iter-disc-${iter.round_number}-${idx}`,
            type: 'agent',
            content: msg.content,
            sender: msg.agent_name,
            senderType: msg.agent_type,
            timestamp: msg.timestamp,
          });
        });
      }

      // Iteration tasks
      if (iter.tasks) {
        iter.tasks.forEach((task) => {
          if (task.status === 'completed') {
            messages.push({
              id: `iter-task-${task.id}`,
              type: 'task',
              content: task.title,
              status: 'completed',
              timestamp: new Date().toISOString(),
            });
          } else if (task.status === 'running') {
            messages.push({
              id: `iter-task-${task.id}`,
              type: 'task',
              content: task.title,
              status: 'running',
              isStreaming: true,
              timestamp: new Date().toISOString(),
            });
          }
        });
      }
    });
  }

  // Pending messages (submitted but not yet in plan data)
  pendingMessages.forEach((msg, idx) => {
    messages.push({
      id: `pending-${idx}`,
      type: 'user',
      content: msg,
      sender: '你',
      timestamp: new Date().toISOString(),
    });
  });

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages List */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">

        {messages.length === 0 && !plan && (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-500/20 to-purple-500/20 flex items-center justify-center mb-4">
              <Sparkles size={28} className="text-pink-400" />
            </div>
            <p className="text-center text-sm text-gray-400 mb-6">
              描述你想要的游戏想法<br />
              <span className="text-gray-500">AI 团队将为你协作生成</span>
            </p>

            {/* History Section */}
            {gamePlans.length > 0 && (
              <div className="w-full max-w-sm">
                <div className="flex items-center gap-2 text-gray-500 text-xs mb-2">
                  <History size={12} />
                  <span>历史记录</span>
                </div>
                <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1">
                  {gamePlans.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => onSelectPlan(p.id)}
                      className="w-full flex items-center gap-3 p-3 rounded-xl bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 hover:border-gray-600 transition-all text-left group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-gray-700 group-hover:bg-pink-500/20 flex items-center justify-center flex-shrink-0 transition-colors">
                        <Gamepad2 size={14} className="text-gray-400 group-hover:text-pink-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-300 truncate">{p.title || p.original_request?.slice(0, 30)}</p>
                        <p className="text-xs text-gray-500">{formatTime(p.created_at)}</p>
                      </div>
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        p.status === 'completed' ? 'bg-emerald-500' :
                        p.status === 'executing' ? 'bg-blue-500 animate-pulse' :
                        'bg-gray-500'
                      }`} />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2.5 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            {msg.type === 'agent' && (
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-white text-xs"
                style={{ backgroundColor: getAgentColor(msg.senderType || 'assistant') }}
              >
                <Bot size={14} />
              </div>
            )}
            {msg.type === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center flex-shrink-0 text-white">
                <User size={14} />
              </div>
            )}
            {msg.type === 'task' && (
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                msg.status === 'completed' ? 'bg-emerald-500' : 'bg-blue-500'
              }`}>
                {msg.status === 'completed' ? (
                  <CheckCircle2 size={14} className="text-white" />
                ) : (
                  <Loader2 size={14} className="text-white animate-spin" />
                )}
              </div>
            )}

            {/* Message Content */}
            <div className={`flex-1 min-w-0 ${msg.type === 'user' ? 'text-right' : ''}`}>
              {msg.sender && (
                <div className={`text-[11px] mb-1 ${
                  msg.type === 'user' ? 'text-blue-400' : 'text-gray-500'
                }`}>
                  {msg.sender}
                  {msg.senderType && (
                    <span className="text-gray-600 ml-1">
                      · {AGENT_LABELS_CN[msg.senderType] || msg.senderType}
                    </span>
                  )}
                </div>
              )}
              <div
                className={`inline-block px-3 py-2 rounded-xl max-w-[92%] text-sm ${
                  msg.type === 'user'
                    ? 'bg-blue-500 text-white rounded-tr-sm'
                    : msg.type === 'task'
                    ? msg.status === 'completed'
                      ? 'bg-emerald-500/15 text-emerald-300 rounded-tl-sm border border-emerald-500/20'
                      : 'bg-blue-500/15 text-blue-300 rounded-tl-sm border border-blue-500/20'
                    : 'bg-gray-800 text-gray-200 rounded-tl-sm border border-gray-700/50'
                }`}
              >
                <p className="whitespace-pre-wrap break-words leading-relaxed">{msg.content}</p>
                {msg.isStreaming && (
                  <span className="inline-block w-1.5 h-3 ml-1 bg-current/50 animate-pulse" />
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Task list with progress */}
        {(() => {
          // Determine active task list (iteration or main plan)
          const activeTasks = iterationExecuting
            ? (latestIteration?.tasks || [])
            : (plan?.status === 'executing' ? (plan.tasks || []) : []);
          const activeCompleted = iterationExecuting ? iterCompletedTasks.length : completedTasks.length;
          const activeTotal = iterationExecuting ? iterTotalTasks : totalTasks;
          const isExecuting = iterationExecuting || plan?.status === 'executing';

          if (!isExecuting || activeTotal === 0) return null;

          const label = iterationExecuting ? '迭代进度' : '执行进度';
          const progress = activeTotal > 0 ? (activeCompleted / activeTotal) * 100 : 0;

          return (
            <div className="bg-gray-800/50 rounded-xl p-3 border border-gray-700/50">
              <div className="flex items-center gap-2 text-gray-400 mb-2">
                <Clock size={12} />
                <span className="text-xs">{label} {activeCompleted}/{activeTotal}</span>
              </div>
              <div className="w-full h-1 bg-gray-700 rounded-full overflow-hidden mb-2.5">
                <div
                  className="h-full bg-gradient-to-r from-pink-500 to-purple-500 transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="space-y-1.5">
                {activeTasks.map((task) => (
                  <div key={task.id} className="flex items-center gap-2 text-xs">
                    {task.status === 'completed' ? (
                      <CheckCircle2 size={12} className="text-emerald-400 flex-shrink-0" />
                    ) : task.status === 'running' ? (
                      <Loader2 size={12} className="text-blue-400 animate-spin flex-shrink-0" />
                    ) : (
                      <div className="w-3 h-3 rounded-full border border-gray-600 flex-shrink-0" />
                    )}
                    <span className={
                      task.status === 'completed' ? 'text-emerald-400 line-through opacity-70' :
                      task.status === 'running' ? 'text-blue-300 font-medium' :
                      'text-gray-500'
                    }>
                      {task.title}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-4 py-4 border-t border-gray-800">
        <div className="relative">
          <textarea
            ref={inputRef}
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              plan?.status === 'completed'
                ? "描述你想要的修改，继续优化游戏..."
                : "描述你的游戏想法..."
            }
            className="w-full bg-gray-800/50 text-white rounded-xl px-4 py-3 pr-12 resize-none border border-gray-700 focus:border-pink-500/50 focus:ring-1 focus:ring-pink-500/20 focus:outline-none placeholder-gray-500 text-sm transition-all"
            rows={2}
            disabled={starting}
          />
          <button
            onClick={handleSubmit}
            disabled={!request.trim() || starting}
            className="absolute right-2 bottom-2 w-9 h-9 rounded-lg bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 disabled:from-gray-700 disabled:to-gray-700 text-white transition-all flex items-center justify-center disabled:cursor-not-allowed"
          >
            {starting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </button>
        </div>
        <p className="text-[10px] text-gray-600 mt-2 text-center">
          Enter 发送 · Shift+Enter 换行
        </p>
      </div>
    </div>
  );
}
