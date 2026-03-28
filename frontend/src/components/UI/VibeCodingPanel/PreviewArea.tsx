import { useState, useRef } from 'react';
import {
  RefreshCw,
  Maximize2,
  Minimize2,
  ExternalLink,
  Download,
  Code,
  Loader2,
  Gamepad2,
  ArrowLeft
} from 'lucide-react';
import type { Plan } from '../../../types';

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
  const [codeContent, setCodeContent] = useState<string>('');

  const handleRefresh = () => {
    setIsRefreshing(true);
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
    </div>
  );
}
