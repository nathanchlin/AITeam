import { useState, useRef, useEffect, useLayoutEffect } from 'react';
import {
  RefreshCw,
  Maximize2,
  Minimize2,
  ExternalLink,
  Download,
  Code,
  Loader2,
  Gamepad2,
  ArrowLeft,
  Terminal,
  ClipboardCopy,
  Check,
  Trash2,
  X,
} from 'lucide-react';
import type { Plan } from '../../../types';

interface PreviewAreaProps {
  previewUrl: string | null;
  planId: string | undefined;
  plan: Plan | undefined;
  onBack?: () => void;
}

interface LogEntry {
  level: string;
  message: string;
  time: number;
}

export function PreviewArea({ previewUrl, planId, plan, onBack }: PreviewAreaProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [codeContent, setCodeContent] = useState<string>('');
  const [showConsole, setShowConsole] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [copied, setCopied] = useState(false);
  const [levelFilter, setLevelFilter] = useState<string>('all');

  // Listen for log messages from the injected console hook
  // useLayoutEffect ensures listener is attached synchronously before browser paints,
  // so early iframe messages aren't missed
  useLayoutEffect(() => {
    if (!previewUrl) return;
    const handleMessage = (e: MessageEvent) => {
      if (e.data?.type === 'iframe-log') {
        setLogs(prev => [...prev, { level: e.data.level, message: e.data.message, time: Date.now() }]);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [previewUrl]);

  // Clear logs when preview URL changes
  useEffect(() => {
    setLogs([]);
  }, [previewUrl]);

  // Auto-scroll logs
  useEffect(() => {
    if (showConsole && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [logs.length, showConsole]);

  const handleCopyLogs = () => {
    const filtered = filteredLogs;
    const text = filtered.map(l => `[${l.level.toUpperCase()}] ${l.message}`).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleClearLogs = () => {
    setLogs([]);
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setLogs([]);
    if (iframeRef.current && previewUrl) {
      iframeRef.current.src = previewUrl + '?t=' + Date.now();
    }
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleOpenExternal = () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank');
    }
  };

  const handleDownload = () => {
    if (previewUrl) {
      const a = document.createElement('a');
      a.href = previewUrl;
      a.download = `game-${planId}.html`;
      a.click();
    }
  };

  const handleViewCode = async () => {
    if (!previewUrl) return;
    try {
      const res = await fetch(previewUrl);
      const code = await res.text();
      setCodeContent(code);
      setShowCode(!showCode);
    } catch (error) {
      console.error('Failed to fetch code:', error);
    }
  };

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'draft': return { text: '正在分析需求...', color: 'text-gray-400' };
      case 'discussing': return { text: '团队讨论中...', color: 'text-amber-400' };
      case 'pending_approval': return { text: '等待确认计划...', color: 'text-orange-400' };
      case 'executing': return { text: '正在生成游戏...', color: 'text-blue-400' };
      default: return { text: '', color: '' };
    }
  };

  const filteredLogs = levelFilter === 'all' ? logs : logs.filter(l => l.level === levelFilter);

  const errorCount = logs.filter(l => l.level === 'error').length;
  const warnCount = logs.filter(l => l.level === 'warn').length;

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'error': return <span className="text-red-400 text-xs flex-shrink-0 w-4 text-center">✕</span>;
      case 'warn': return <span className="text-yellow-400 text-xs flex-shrink-0 w-4 text-center">⚠</span>;
      case 'info': return <span className="text-blue-400 text-xs flex-shrink-0 w-4 text-center">ℹ</span>;
      default: return <span className="text-gray-500 text-xs flex-shrink-0 w-4 text-center">›</span>;
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400';
      case 'warn': return 'text-yellow-400';
      case 'info': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const renderEmptyState = () => (
    <div className="flex-1 flex flex-col items-center justify-center bg-gray-900">
      <div className="w-20 h-20 rounded-2xl bg-gray-800 flex items-center justify-center mb-4">
        <Gamepad2 size={36} className="text-gray-600" />
      </div>
      <p className="text-gray-400 text-base mb-1">游戏预览区</p>
      <p className="text-sm text-gray-500 text-center max-w-[200px]">
        在左侧输入游戏想法<br />生成完成后将在这里展示
      </p>
      {plan && plan.status !== 'completed' && (
        <div className={`mt-6 flex items-center gap-2 ${getStatusInfo(plan.status).color}`}>
          <Loader2 size={14} className="animate-spin" />
          <span className="text-sm">{getStatusInfo(plan.status).text}</span>
        </div>
      )}
    </div>
  );

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Toolbar */}
      {previewUrl && (
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800">
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white text-xs transition-all"
            >
              <ArrowLeft size={14} />
              <span>返回历史</span>
            </button>
          )}
          <div className="flex items-center gap-1 ml-auto">
            {/* Console Toggle */}
            <button
              onClick={() => setShowConsole(!showConsole)}
              className={`h-8 px-3 rounded-lg transition-colors flex items-center gap-1.5 text-xs relative ${
                showConsole ? 'bg-gray-700 text-blue-400' : 'hover:bg-gray-800 text-gray-500 hover:text-white'
              }`}
              title="控制台日志"
            >
              <Terminal size={14} />
              <span className="hidden sm:inline">日志</span>
              {errorCount > 0 && (
                <span className="min-w-[16px] h-4 px-1 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center font-bold">
                  {errorCount > 99 ? '99+' : errorCount}
                </span>
              )}
            </button>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="w-8 h-8 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-white transition-colors flex items-center justify-center disabled:opacity-50"
              title="刷新"
            >
              <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            </button>
            <button
              onClick={handleViewCode}
              className={`w-8 h-8 rounded-lg transition-colors flex items-center justify-center ${
                showCode ? 'bg-gray-800 text-pink-400' : 'hover:bg-gray-800 text-gray-500 hover:text-white'
              }`}
              title="查看代码"
            >
              <Code size={14} />
            </button>
            <button
              onClick={handleDownload}
              className="w-8 h-8 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-white transition-colors flex items-center justify-center"
              title="下载"
            >
              <Download size={14} />
            </button>
            <button
              onClick={handleOpenExternal}
              className="w-8 h-8 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-white transition-colors flex items-center justify-center"
              title="新窗口打开"
            >
              <ExternalLink size={14} />
            </button>
            <button
              onClick={handleFullscreen}
              className="w-8 h-8 rounded-lg hover:bg-gray-800 text-gray-500 hover:text-white transition-colors flex items-center justify-center"
              title={isFullscreen ? '退出全屏' : '全屏'}
            >
              {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            </button>
          </div>
        </div>
      )}

      {/* Main Content: Preview + Console split */}
      <div className="flex-1 flex min-h-0 overflow-hidden">
        {!previewUrl ? (
          renderEmptyState()
        ) : showCode ? (
          <div className="flex-1 overflow-auto bg-gray-900 p-4">
            <pre className="text-xs text-gray-400 font-mono whitespace-pre-wrap leading-relaxed">
              {codeContent || '加载中...'}
            </pre>
          </div>
        ) : (
          <>
            {/* Preview iframe */}
            <div className="flex-1 min-w-0 overflow-hidden">
              <iframe
                ref={iframeRef}
                src={previewUrl}
                className="w-full h-full border-0 bg-white"
                title="Game Preview"
                sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
              />
            </div>

            {/* Console Panel - same level as iframe */}
            {showConsole && (
              <div className="w-80 flex-shrink-0 flex flex-col border-l border-gray-700 bg-gray-900">
                {/* Console Header */}
                <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-gray-800/50 flex-shrink-0">
                  <div className="flex items-center gap-2">
                    <Terminal size={12} className="text-blue-400" />
                    <span className="text-xs text-gray-300 font-medium">控制台</span>
                    <span className="text-[10px] text-gray-500">({filteredLogs.length})</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={handleCopyLogs}
                      className={`w-6 h-6 rounded flex items-center justify-center transition-colors ${
                        copied ? 'text-emerald-400' : 'text-gray-500 hover:text-white hover:bg-gray-700'
                      }`}
                      title="复制日志"
                    >
                      {copied ? <Check size={12} /> : <ClipboardCopy size={12} />}
                    </button>
                    <button
                      onClick={handleClearLogs}
                      className="w-6 h-6 rounded flex items-center justify-center text-gray-500 hover:text-white hover:bg-gray-700 transition-colors"
                      title="清除日志"
                    >
                      <Trash2 size={12} />
                    </button>
                    <button
                      onClick={() => setShowConsole(false)}
                      className="w-6 h-6 rounded flex items-center justify-center text-gray-500 hover:text-white hover:bg-gray-700 transition-colors"
                      title="关闭"
                    >
                      <X size={12} />
                    </button>
                  </div>
                </div>
                {/* Level Filter */}
                <div className="flex items-center gap-1 px-3 py-1.5 border-b border-gray-700/50 flex-shrink-0">
                  {[
                    { key: 'all', label: '全部', count: logs.length },
                    { key: 'error', label: '错误', count: errorCount },
                    { key: 'warn', label: '警告', count: warnCount },
                  ].map(f => (
                    <button
                      key={f.key}
                      onClick={() => setLevelFilter(f.key)}
                      className={`px-2 py-0.5 rounded text-[10px] transition-colors flex items-center gap-1 ${
                        levelFilter === f.key
                          ? f.key === 'error' ? 'bg-red-500/20 text-red-400'
                            : f.key === 'warn' ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-purple-500/20 text-purple-400'
                          : 'text-gray-500 hover:text-gray-300'
                      }`}
                    >
                      {f.label}
                      {f.count > 0 && <span className="opacity-70">{f.count}</span>}
                    </button>
                  ))}
                </div>
                {/* Log Entries */}
                <div className="flex-1 overflow-y-auto min-h-0">
                  {filteredLogs.length > 0 ? (
                    filteredLogs.map((log, i) => (
                      <div
                        key={i}
                        className={`flex items-start gap-1.5 px-3 py-1 border-b border-gray-800/50 hover:bg-gray-800/30 ${
                          log.level === 'error' ? 'bg-red-500/5' : ''
                        }`}
                      >
                        {getLogIcon(log.level)}
                        <span className={`text-xs font-mono break-all leading-relaxed select-text ${getLogColor(log.level)}`}>
                          {log.message}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-600">
                      <Terminal size={24} className="mb-2 opacity-30" />
                      <p className="text-xs">暂无日志</p>
                    </div>
                  )}
                  <div ref={logsEndRef} />
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
