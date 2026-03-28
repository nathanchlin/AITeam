import { useState, useRef, useEffect, useCallback } from 'react';
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
  Trash2,
  AlertCircle,
  Info,
  AlertTriangle,
  X
} from 'lucide-react';
import type { Plan } from '../../../types';

interface LogEntry {
  id: number;
  type: 'error' | 'warn' | 'log' | 'info';
  message: string;
  source?: string;
  line?: number;
  column?: number;
  timestamp: number;
}

interface PreviewAreaProps {
  previewUrl: string | null;
  planId: string | undefined;
  plan: Plan | undefined;
  onBack?: () => void;
}

export function PreviewArea({ previewUrl, planId, plan, onBack }: PreviewAreaProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [codeContent, setCodeContent] = useState<string>('');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [errorCount, setErrorCount] = useState(0);
  const logIdRef = useRef(0);
  const logEndRef = useRef<HTMLDivElement>(null);

  const addLog = useCallback((type: LogEntry['type'], message: string, source?: string, line?: number, column?: number) => {
    const entry: LogEntry = {
      id: ++logIdRef.current,
      type,
      message,
      source,
      line,
      column,
      timestamp: Date.now(),
    };
    setLogs(prev => [...prev.slice(-199), entry]);
    if (type === 'error') {
      setErrorCount(prev => prev + 1);
    }
  }, []);

  // Listen for iframe console messages via postMessage
  useEffect(() => {
    if (!previewUrl) return;

    const handleMessage = (e: MessageEvent) => {
      if (e.data?.type === 'iframe-console') {
        addLog(e.data.level, e.data.message, e.data.source, e.data.line, e.data.column);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [previewUrl, addLog]);

  // Inject console hook into iframe after load
  useEffect(() => {
    if (!previewUrl) return;

    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleLoad = () => {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc || !iframe.contentWindow) return;

        const script = doc.createElement('script');
        script.textContent = `
          (function() {
            var origConsole = {};
            ['error','warn','log','info'].forEach(function(level) {
              origConsole[level] = console[level];
              console[level] = function() {
                var args = Array.prototype.slice.call(arguments);
                var msg = args.map(function(a) {
                  try { return typeof a === 'object' ? JSON.stringify(a) : String(a); }
                  catch(e) { return String(a); }
                }).join(' ');
                try {
                  window.parent.postMessage({
                    type: 'iframe-console',
                    level: level,
                    message: msg
                  }, '*');
                } catch(e) {}
                origConsole[level].apply(console, args);
              };
            });
            window.addEventListener('error', function(e) {
              try {
                window.parent.postMessage({
                  type: 'iframe-console',
                  level: 'error',
                  message: e.message,
                  source: e.filename,
                  line: e.lineno,
                  column: e.colno
                }, '*');
              } catch(err) {}
            });
            window.addEventListener('unhandledrejection', function(e) {
              try {
                window.parent.postMessage({
                  type: 'iframe-console',
                  level: 'error',
                  message: 'Unhandled Promise: ' + (e.reason ? (e.reason.stack || e.reason.message || String(e.reason)) : 'Unknown')
                }, '*');
              } catch(err) {}
            });
          })();
        `;
        (doc.head || doc.documentElement).appendChild(script);
      } catch (e) {
        // Cross-origin iframe — can't inject, rely on postMessage if available
      }
    };

    iframe.addEventListener('load', handleLoad);
    return () => iframe.removeEventListener('load', handleLoad);
  }, [previewUrl]);

  // Auto-scroll log panel
  useEffect(() => {
    if (showLogs && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [logs, showLogs]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setLogs([]);
    setErrorCount(0);
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

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'error': return <AlertCircle size={12} className="text-red-400 flex-shrink-0" />;
      case 'warn': return <AlertTriangle size={12} className="text-amber-400 flex-shrink-0" />;
      case 'info': return <Info size={12} className="text-blue-400 flex-shrink-0" />;
      default: return <Info size={12} className="text-gray-500 flex-shrink-0" />;
    }
  };

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'error': return 'text-red-300';
      case 'warn': return 'text-amber-300';
      case 'info': return 'text-blue-300';
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

  const renderLogPanel = () => (
    <div className="border-t border-gray-700 bg-gray-950 flex flex-col" style={{ height: showLogs ? '220px' : '0', transition: 'height 200ms ease' }}>
      {/* Log header */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-gray-800 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Terminal size={12} className="text-gray-500" />
          <span className="text-xs text-gray-400">控制台</span>
          {errorCount > 0 && (
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 font-mono">{errorCount}</span>
          )}
          <span className="text-[10px] text-gray-600 font-mono">{logs.length} 条</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => { setLogs([]); setErrorCount(0); }}
            className="w-6 h-6 rounded hover:bg-gray-800 text-gray-500 hover:text-white transition-colors flex items-center justify-center"
            title="清空日志"
          >
            <Trash2 size={12} />
          </button>
          <button
            onClick={() => setShowLogs(false)}
            className="w-6 h-6 rounded hover:bg-gray-800 text-gray-500 hover:text-white transition-colors flex items-center justify-center"
            title="关闭"
          >
            <X size={12} />
          </button>
        </div>
      </div>
      {/* Log entries */}
      <div className="flex-1 overflow-y-auto px-3 py-1 font-mono text-xs">
        {logs.length === 0 ? (
          <div className="text-gray-600 py-4 text-center">暂无日志</div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="flex items-start gap-2 py-1 border-b border-gray-800/50">
              {getLogIcon(log.type)}
              <div className="flex-1 min-w-0">
                <p className={`${getLogColor(log.type)} break-all leading-relaxed`}>{log.message}</p>
                {log.source && (
                  <p className="text-gray-600 text-[10px] truncate">
                    {log.source}{log.line ? `:${log.line}:${log.column || ''}` : ''}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Toolbar */}
      {previewUrl && (
        <div className="flex items-center justify-between px-4 py-2">
          {/* Back button */}
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white text-xs transition-all"
            >
              <ArrowLeft size={14} />
              <span>返回历史</span>
            </button>
          )}
          {/* Action buttons */}
          <div className="flex items-center gap-1 ml-auto">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className={`w-8 h-8 rounded-lg transition-colors flex items-center justify-center relative ${
              showLogs ? 'bg-gray-800 text-pink-400' : 'hover:bg-gray-800 text-gray-500 hover:text-white'
            }`}
            title="控制台日志"
          >
            <Terminal size={14} />
            {errorCount > 0 && !showLogs && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center font-bold">{errorCount > 9 ? '9+' : errorCount}</span>
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

      {/* Preview Content */}
      <div className="flex-1 overflow-hidden">
        {!previewUrl ? (
          renderEmptyState()
        ) : showCode ? (
          <div className="h-full overflow-auto bg-gray-900 p-4">
            <pre className="text-xs text-gray-400 font-mono whitespace-pre-wrap leading-relaxed">
              {codeContent || '加载中...'}
            </pre>
          </div>
        ) : (
          <iframe
            ref={iframeRef}
            src={previewUrl}
            className="w-full h-full border-0 bg-white rounded-lg mx-2"
            style={{ width: 'calc(100% - 16px)' }}
            title="Game Preview"
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
          />
        )}
      </div>

      {/* Log Panel */}
      {previewUrl && showLogs && renderLogPanel()}
    </div>
  );
}
