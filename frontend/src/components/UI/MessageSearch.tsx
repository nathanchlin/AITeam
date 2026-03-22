import { useState, useMemo } from 'react';
import { Search, X, Filter } from 'lucide-react';

export interface SearchFilters {
  keyword: string;
  senderType: 'all' | 'user' | 'agent';
  dateRange: 'all' | 'today' | 'week' | 'month';
}

interface MessageSearchProps {
  isOpen: boolean;
  onClose: () => void;
  messages: Array<{
    id: string;
    content: string;
    sender_name: string;
    sender_type: 'user' | 'agent';
    timestamp: string;
  }>;
  onJumpToMessage: (messageId: string) => void;
  placeholder?: string;
}

export function MessageSearch({
  isOpen,
  onClose,
  messages,
  onJumpToMessage,
  placeholder = '搜索消息...'
}: MessageSearchProps) {
  const [keyword, setKeyword] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    keyword: '',
    senderType: 'all',
    dateRange: 'all',
  });

  // Filter messages based on keyword and filters
  const filteredMessages = useMemo(() => {
    let result = messages;

    // Filter by keyword
    if (keyword.trim()) {
      const lowerKeyword = keyword.toLowerCase();
      result = result.filter(msg =>
        msg.content.toLowerCase().includes(lowerKeyword)
      );
    }

    // Filter by sender type
    if (filters.senderType !== 'all') {
      result = result.filter(msg => msg.sender_type === filters.senderType);
    }

    // Filter by date range
    if (filters.dateRange !== 'all') {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

      result = result.filter(msg => {
        const msgDate = new Date(msg.timestamp);
        switch (filters.dateRange) {
          case 'today':
            return msgDate >= today;
          case 'week':
            return msgDate >= weekAgo;
          case 'month':
            return msgDate >= monthAgo;
          default:
            return true;
        }
      });
    }

    return result;
  }, [messages, keyword, filters]);

  // Highlight matching text
  const highlightText = (text: string, highlight: string): React.ReactNode => {
    if (!highlight.trim()) return text;
    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return parts.map((part, i) =>
      i % 2 === 1 ? (
        <mark key={i} className="bg-yellow-500/30 text-yellow-200 px-0.5 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  // Format time for display
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 bg-black/90 z-50 flex flex-col">
      {/* Search Header */}
      <div className="w-full bg-gray-900 border-b border-gray-700 p-3 flex items-center gap-2">
        <Search size={16} className="text-gray-400" />
        <span className="text-white text-sm font-medium">搜索消息</span>
        <div className="flex-1" />
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`p-1.5 hover:bg-gray-700 rounded flex items-center gap-1 text-gray-400 hover:text-white transition-colors ${showFilters ? 'bg-gray-600 text-white' : ''}`}
          title="筛选"
        >
          <Filter size={14} />
        </button>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
          title="关闭"
        >
          <X size={14} />
        </button>
      </div>

      {/* Search Input */}
      <div className="p-3 border-b border-gray-700">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder={placeholder}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-800 text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none rounded"
            autoFocus
          />
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="p-3 border-b border-gray-700 bg-gray-800/50 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">发送者:</span>
            <div className="flex gap-1">
              {[
                { value: 'all', label: '全部' },
                { value: 'user', label: '用户' },
                { value: 'agent', label: 'Agent' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setFilters(f => ({ ...f, senderType: opt.value as SearchFilters['senderType'] }))}
                  className={`px-2 py-1 text-xs rounded ${
                    filters.senderType === opt.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">时间范围:</span>
            <div className="flex gap-1">
              {[
                { value: 'all', label: '全部' },
                { value: 'today', label: '今天' },
                { value: 'week', label: '一周内' },
                { value: 'month', label: '一月内' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setFilters(f => ({ ...f, dateRange: opt.value as SearchFilters['dateRange'] }))}
                  className={`px-2 py-1 text-xs rounded ${
                    filters.dateRange === opt.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="flex-1 overflow-y-auto">
        {filteredMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Search size={32} className="mb-2 opacity-50" />
            <p className="text-sm">未找到匹配的消息</p>
          </div>
        ) : (
          <div className="space-y-2 p-2">
            {filteredMessages.map((msg, index) => (
              <button
                key={msg.id}
                onClick={() => {
                  onJumpToMessage(msg.id);
                  onClose();
                }}
                className="w-full text-left p-2 rounded hover:bg-gray-700 transition-colors group"
              >
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                  <span className="font-medium text-gray-300">
                    #{index + 1} / {filteredMessages.length}
                  </span>
                  <span>|</span>
                  <span>{formatTime(msg.timestamp)}</span>
                </div>
                <div className="flex items-start gap-2">
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                    style={{
                      backgroundColor: msg.sender_type === 'user' ? '#3B82F6' : '#6B7280',
                    }}
                  >
                    {msg.sender_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-medium text-white truncate block">
                      {msg.sender_name}
                    </span>
                    <span className="text-xs text-gray-400">
                      {msg.sender_type === 'user' ? '用户' : 'Agent'}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-300 line-clamp-2 mt-1 pl-8">
                  {highlightText(msg.content, keyword)}
                </p>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
