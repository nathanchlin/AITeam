import { useState, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType, type AgentType } from '../../types';
import { MessageCircle, User, Search, X, Filter } from 'lucide-react';

interface ContactListProps {
  onStartPrivateChat: (agentId: string) => void;
}

export function ContactList({ onStartPrivateChat }: ContactListProps) {
  const { agents } = useAgentStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<AgentType | 'all'>('all');
  const [showFilters, setShowFilters] = useState(false);

  // Filter agents
  const filteredAgents = useMemo(() => {
    return agents.filter(agent => {
      // Type filter
      if (typeFilter !== 'all' && agent.type !== typeFilter) return false;

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const nameMatch = agent.name.toLowerCase().includes(query);
        const typeMatch = getAgentDisplayType(agent).toLowerCase().includes(query);
        if (!nameMatch && !typeMatch) return false;
      }

      return true;
    });
  }, [agents, searchQuery, typeFilter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
        return 'bg-green-500 animate-pulse';
      case 'error':
        return 'bg-red-500';
      case 'waiting':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'working':
        return '思考中...';
      case 'error':
        return '错误';
      case 'waiting':
        return '等待中';
      default:
        return '在线';
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-white text-sm font-bold">通讯录</h3>
          <span className="text-gray-400 text-xs">
            {filteredAgents.length}/{agents.length}
          </span>
        </div>

        {/* Search Bar */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索 Agent..."
              className="w-full pl-8 pr-2 py-1.5 bg-gray-700 rounded text-sm text-white placeholder-gray-500 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
              >
                <X size={12} />
              </button>
            )}
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-1.5 rounded transition-colors ${
              showFilters || typeFilter !== 'all'
                ? 'bg-blue-600 text-white'
                : 'hover:bg-gray-700 text-gray-400'
            }`}
            title="筛选"
          >
            <Filter size={14} />
          </button>
        </div>

        {/* Type Filter Chips */}
        {showFilters && (
          <div className="flex flex-wrap gap-1 mt-2">
            <button
              onClick={() => setTypeFilter('all')}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                typeFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              全部
            </button>
            <button
              onClick={() => setTypeFilter('coder')}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                typeFilter === 'coder' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              开发
            </button>
            <button
              onClick={() => setTypeFilter('analyst')}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                typeFilter === 'analyst' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              分析
            </button>
            <button
              onClick={() => setTypeFilter('assistant')}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                typeFilter === 'assistant' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              协调
            </button>
            <button
              onClick={() => setTypeFilter('tester')}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                typeFilter === 'tester' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              测试
            </button>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {filteredAgents.length === 0 ? (
          agents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <User size={48} className="mb-3 opacity-50" />
              <p className="text-sm font-medium">暂无 Agent</p>
              <p className="text-xs text-gray-500 mt-1">请在 Sidebar 中创建</p>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <Search size={32} className="mb-2 opacity-50" />
              <p className="text-sm">未找到匹配的 Agent</p>
              <button
                onClick={() => { setSearchQuery(''); setTypeFilter('all'); }}
                className="text-xs text-blue-400 hover:text-blue-300 mt-2"
              >
                清除筛选
              </button>
            </div>
          )
        ) : (
          <div className="divide-y divide-gray-700">
            {filteredAgents.map((agent) => (
              <div
                key={agent.id}
                className="p-3 hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg relative"
                    style={{ backgroundColor: AGENT_COLORS[agent.type]?.primary || '#6B7280' }}
                  >
                    <span className="text-white text-base font-bold">
                      {(agent.name || '?').charAt(0).toUpperCase()}
                    </span>
                    <span
                      className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-gray-800 ${getStatusColor(agent.status)}`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-white text-sm font-medium truncate">{agent.name}</h4>
                    <p className="text-gray-400 text-xs">{getAgentDisplayType(agent)}</p>
                    <p className="text-gray-500 text-xs flex items-center gap-1 mt-0.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${getStatusColor(agent.status)}`} />
                      {getStatusText(agent.status)}
                    </p>
                  </div>
                </div>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => onStartPrivateChat(agent.id)}
                    className="flex-1 px-3 py-1.5 bg-blue-600/20 text-blue-400 rounded text-xs hover:bg-blue-600/30 transition-colors flex items-center justify-center gap-1"
                  >
                    <MessageCircle size={12} />
                    发消息
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
