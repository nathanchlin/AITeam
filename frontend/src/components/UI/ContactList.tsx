import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { MessageCircle, User } from 'lucide-react';

interface ContactListProps {
  onStartPrivateChat: (agentId: string) => void;
}

export function ContactList({ onStartPrivateChat }: ContactListProps) {
  const { agents } = useAgentStore();

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
        <h3 className="text-white text-sm font-bold">通讯录</h3>
        <p className="text-gray-400 text-xs mt-1">{agents.length} 个 Agent</p>
      </div>

      <div className="flex-1 overflow-y-auto">
        {agents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <User size={48} className="mb-3 opacity-50" />
            <p className="text-sm font-medium">暂无 Agent</p>
            <p className="text-xs text-gray-500 mt-1">请在 Sidebar 中创建</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="p-3 hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg relative"
                    style={{ backgroundColor: AGENT_COLORS[agent.type].primary }}
                  >
                    <span className="text-white text-base font-bold">
                      {agent.name.charAt(0).toUpperCase()}
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
