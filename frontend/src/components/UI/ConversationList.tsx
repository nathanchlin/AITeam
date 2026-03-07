import { useState, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { MessageCircle, Users, Check } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : `http://${window.location.hostname}:8000`;

interface ConversationListProps {
  selectedChatId: string | null;
  selectedChatType: 'private' | 'group';
  onSelectChat: (id: string, type: 'private' | 'group') => void;
  showCreateGroup: boolean;
  onCloseCreateGroup: () => void;
}

interface Conversation {
  id: string;
  type: 'private' | 'group';
  name: string;
  avatarColor: string;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
}

export function ConversationList({
  selectedChatId,
  selectedChatType,
  onSelectChat,
  showCreateGroup,
  onCloseCreateGroup,
}: ConversationListProps) {
  const { agents, groupChats, tasks } = useAgentStore();
  const [newChatName, setNewChatName] = useState('');
  const [newChatDescription, setNewChatDescription] = useState('');
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);

  // Build conversation list from agents (private chats) and group chats
  const conversations = useMemo(() => {
    const convos: Conversation[] = [];
    const safeAgents = agents || [];
    const safeGroupChats = groupChats || [];
    const safeTasks = tasks || [];

    // Add private chats (agents with tasks)
    safeAgents.forEach(agent => {
      const agentTasks = safeTasks.filter(t => t.agent_id === agent.id);
      const lastTask = agentTasks[0]; // Tasks are sorted by created_at desc

      if (agentTasks.length > 0) {
        convos.push({
          id: agent.id,
          type: 'private',
          name: agent.name,
          avatarColor: AGENT_COLORS[agent.type].primary,
          lastMessage: lastTask.result || lastTask.title || '...',
          lastMessageTime: lastTask.updated_at || lastTask.created_at,
          unreadCount: 0,
        });
      }
    });

    // Add group chats
    safeGroupChats.forEach(chat => {
      const lastMessage = chat.messages[chat.messages.length - 1];
      convos.push({
        id: chat.id,
        type: 'group',
        name: chat.name,
        avatarColor: getUserAvatarColor(chat.name),
        lastMessage: lastMessage?.content || '暂无消息',
        lastMessageTime: lastMessage?.timestamp || chat.updated_at,
        unreadCount: 0,
      });
    });

    // Sort by last message time
    return convos.sort((a, b) =>
      new Date(b.lastMessageTime).getTime() - new Date(a.lastMessageTime).getTime()
    );
  }, [agents, groupChats, tasks]);

  const formatTime = (timestamp: string): string => {
    const utcTimestamp = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
    const date = new Date(utcTimestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  const handleCreateChat = async () => {
    if (!newChatName.trim() || creating) return;

    setCreating(true);
    try {
      const res = await fetch(`${API_BASE}/api/group-chats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newChatName.trim(),
          description: newChatDescription.trim() || undefined,
          agent_ids: selectedAgentIds,
        }),
      });

      if (res.ok) {
        const newChat = await res.json();
        useAgentStore.getState().addGroupChat(newChat);
        setNewChatName('');
        setNewChatDescription('');
        setSelectedAgentIds([]);
        onCloseCreateGroup();
        // Select the new chat
        onSelectChat(newChat.id, 'group');
      }
    } catch (error) {
      console.error('Failed to create group chat:', error);
    } finally {
      setCreating(false);
    }
  };

  const getUserAvatarColor = (name: string): string => {
    const colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  // Show create group modal
  if (showCreateGroup) {
    return (
      <div className="p-4 space-y-4">
        <h4 className="text-white text-sm font-medium">创建群聊</h4>

        <div>
          <label className="text-gray-400 text-xs block mb-1">群聊名称</label>
          <input
            type="text"
            value={newChatName}
            onChange={(e) => setNewChatName(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
            placeholder="输入群聊名称..."
          />
        </div>

        <div>
          <label className="text-gray-400 text-xs block mb-1">描述（可选）</label>
          <input
            type="text"
            value={newChatDescription}
            onChange={(e) => setNewChatDescription(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
            placeholder="输入群聊描述..."
          />
        </div>

        <div>
          <label className="text-gray-400 text-xs block mb-2">选择成员</label>
          <div className="max-h-48 overflow-y-auto space-y-1 bg-gray-700/50 rounded p-2">
            {(agents || []).length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-2">暂无可选 Agent</p>
            ) : (
              (agents || []).map((agent) => (
                <label
                  key={agent.id}
                  className="flex items-center gap-2 cursor-pointer hover:bg-gray-600/50 p-2 rounded transition-colors"
                >
                  <div
                    className={`w-5 h-5 rounded border flex items-center justify-center ${
                      selectedAgentIds.includes(agent.id)
                        ? 'bg-blue-600 border-blue-600'
                        : 'border-gray-500'
                    }`}
                  >
                    {selectedAgentIds.includes(agent.id) && <Check size={14} className="text-white" />}
                  </div>
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs flex-shrink-0"
                    style={{ backgroundColor: AGENT_COLORS[agent.type].primary }}
                  >
                    {agent.name.charAt(0)}
                  </div>
                  <span className="text-white text-sm truncate">{agent.name}</span>
                  <span className="text-gray-400 text-xs">({getAgentDisplayType(agent)})</span>
                </label>
              ))
            )}
          </div>
          {selectedAgentIds.length > 0 && (
            <p className="text-blue-400 text-xs mt-1">已选择 {selectedAgentIds.length} 个 Agent</p>
          )}
        </div>

        <div className="flex gap-2">
          <button
            onClick={onCloseCreateGroup}
            className="flex-1 px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
          >
            取消
          </button>
          <button
            onClick={handleCreateChat}
            disabled={!newChatName.trim() || creating}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
          >
            {creating ? '创建中...' : '创建'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-700">
      {conversations.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
          <MessageCircle size={48} className="mb-3 opacity-50" />
          <p className="text-sm font-medium">暂无对话</p>
          <p className="text-xs text-gray-500 mt-1">点击通讯录开始聊天</p>
        </div>
      ) : (
        conversations.map((convo) => (
          <div
            key={`${convo.type}-${convo.id}`}
            onClick={() => onSelectChat(convo.id, convo.type)}
            className={`p-3 cursor-pointer transition-colors ${
              selectedChatId === convo.id && selectedChatType === convo.type
                ? 'bg-gray-700'
                : 'hover:bg-gray-700/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
                style={{ backgroundColor: convo.avatarColor }}
              >
                {convo.type === 'group' ? (
                  <Users size={18} />
                ) : (
                  convo.name.charAt(0).toUpperCase()
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className="text-white text-sm font-medium truncate">{convo.name}</h4>
                  <span className="text-gray-500 text-xs">{formatTime(convo.lastMessageTime)}</span>
                </div>
                <p className="text-gray-400 text-xs truncate mt-0.5">{convo.lastMessage}</p>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
