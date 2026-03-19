import { useState, useMemo, useEffect, useCallback } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { MessageCircle, Users, Check, Search, X, Filter, Inbox, Pin, CheckCheck } from 'lucide-react';

// Local storage key for tracking last viewed times
const LAST_VIEWED_KEY = 'aiteam_last_viewed_conversations';
const PINNED_KEY = 'aiteam_pinned_conversations';

// Helper to get/set last viewed time
const getLastViewedTimes = (): Record<string, string> => {
  try {
    const data = localStorage.getItem(LAST_VIEWED_KEY);
    return data ? JSON.parse(data) : {};
  } catch {
    return {};
  }
};

const setLastViewedTime = (conversationKey: string) => {
  try {
    const times = getLastViewedTimes();
    times[conversationKey] = new Date().toISOString();
    localStorage.setItem(LAST_VIEWED_KEY, JSON.stringify(times));
  } catch {
    // Ignore storage errors
  }
};

// Helper to get/set pinned conversations
const getPinnedConversations = (): Set<string> => {
  try {
    const data = localStorage.getItem(PINNED_KEY);
    return data ? new Set(JSON.parse(data)) : new Set();
  } catch {
    return new Set();
  }
};

const savePinnedConversations = (pinned: Set<string>) => {
  try {
    localStorage.setItem(PINNED_KEY, JSON.stringify([...pinned]));
  } catch {
    // Ignore storage errors
  }
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

interface ConversationListProps {
  selectedChatId: string | null;
  selectedChatType: 'private' | 'group';
  onSelectChat: (id: string, type: 'private' | 'group') => void;
  showCreateGroup: boolean;
  onCloseCreateGroup: () => void;
  onUnreadCountChange?: (count: number) => void;
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
  onUnreadCountChange,
}: ConversationListProps) {
  const { agents, groupChats, tasks } = useAgentStore();
  const [newChatName, setNewChatName] = useState('');
  const [newChatDescription, setNewChatDescription] = useState('');
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);

  // Search and filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<'all' | 'private' | 'group'>('all');
  const [showFilters, setShowFilters] = useState(false);

  // Track last viewed times for unread calculation
  const [lastViewedTimes, setLastViewedTimes] = useState<Record<string, string>>(() => getLastViewedTimes());

  // Track pinned conversations
  const [pinnedConversations, setPinnedConversations] = useState<Set<string>>(() => getPinnedConversations());

  // Toggle pin status
  const togglePin = useCallback((e: React.MouseEvent, convoKey: string) => {
    e.stopPropagation();
    setPinnedConversations(prev => {
      const newSet = new Set(prev);
      if (newSet.has(convoKey)) {
        newSet.delete(convoKey);
      } else {
        newSet.add(convoKey);
      }
      // Persist to localStorage
      savePinnedConversations(newSet);
      return newSet;
    });
  }, []);

  // Build conversation list from agents (private chats) and group chats
  const conversations = useMemo(() => {
    const convos: Conversation[] = [];

    // Helper function defined before useMemo
    const getUserAvatarColor = (name: string): string => {
      const colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];
      const index = name.charCodeAt(0) % colors.length;
      return colors[index];
    };

    const safeAgents = agents || [];
    const safeGroupChats = groupChats || [];
    const safeTasks = tasks || [];

    // Add private chats (agents with tasks)
    safeAgents.forEach(agent => {
      const agentTasks = safeTasks.filter(t => t.agent_id === agent.id);
      const lastTask = agentTasks[0]; // Tasks are sorted by created_at desc

      if (agentTasks.length > 0) {
        // Calculate unread count for private chat
        const lastViewed = lastViewedTimes[`private-${agent.id}`];
        const unreadCount = lastViewed
          ? agentTasks.filter(t => new Date(t.updated_at || t.created_at) > new Date(lastViewed)).length
          : agentTasks.length;

        convos.push({
          id: agent.id,
          type: 'private',
          name: agent.name,
          avatarColor: AGENT_COLORS[agent.type]?.primary || '#6B7280',
          lastMessage: lastTask.result || lastTask.title || '...',
          lastMessageTime: lastTask.updated_at || lastTask.created_at,
          unreadCount,
        });
      }
    });

    // Add group chats
    safeGroupChats.forEach(chat => {
      const lastMessage = chat.messages[chat.messages.length - 1];

      // Calculate unread count for group chat (only count messages from others, not user)
      const lastViewed = lastViewedTimes[`group-${chat.id}`];
      const unreadMessages = lastViewed
        ? chat.messages.filter(m =>
            m.sender_type !== 'user' &&
            new Date(m.timestamp) > new Date(lastViewed)
          )
        : chat.messages.filter(m => m.sender_type !== 'user');

      convos.push({
        id: chat.id,
        type: 'group',
        name: chat.name,
        avatarColor: getUserAvatarColor(chat.name),
        lastMessage: lastMessage?.content || '暂无消息',
        lastMessageTime: lastMessage?.timestamp || chat.updated_at,
        unreadCount: unreadMessages.length,
      });
    });

    // Sort by last message time
    return convos.sort((a, b) =>
      new Date(b.lastMessageTime).getTime() - new Date(a.lastMessageTime).getTime()
    );
  }, [agents, groupChats, tasks, lastViewedTimes]);

  // Calculate total unread count and notify parent
  const totalUnreadCount = useMemo(() => {
    return conversations.reduce((sum, c) => sum + c.unreadCount, 0);
  }, [conversations]);

  // Notify parent of unread count changes
  useEffect(() => {
    onUnreadCountChange?.(totalUnreadCount);
  }, [totalUnreadCount, onUnreadCountChange]);

  // Mark conversation as read when selected
  useEffect(() => {
    if (selectedChatId) {
      const key = `${selectedChatType}-${selectedChatId}`;
      setLastViewedTime(key);
      setLastViewedTimes(getLastViewedTimes());
    }
  }, [selectedChatId, selectedChatType]);

  // Wrapper for onSelectChat to mark as read
  const handleSelectChat = useCallback((id: string, type: 'private' | 'group') => {
    const key = `${type}-${id}`;
    setLastViewedTime(key);
    setLastViewedTimes(getLastViewedTimes());
    onSelectChat(id, type);
  }, [onSelectChat]);

  // Apply search and filters
  const filteredConversations = useMemo(() => {
    const filtered = conversations.filter(convo => {
      // Type filter
      if (typeFilter !== 'all' && convo.type !== typeFilter) return false;

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const nameMatch = convo.name.toLowerCase().includes(query);
        const messageMatch = convo.lastMessage.toLowerCase().includes(query);
        if (!nameMatch && !messageMatch) return false;
      }

      return true;
    });

    // Sort: pinned first, then by last message time
    return filtered.sort((a, b) => {
      const aKey = `${a.type}-${a.id}`;
      const bKey = `${b.type}-${b.id}`;
      const aPinned = pinnedConversations.has(aKey);
      const bPinned = pinnedConversations.has(bKey);

      if (aPinned && !bPinned) return -1;
      if (!aPinned && bPinned) return 1;

      return new Date(b.lastMessageTime).getTime() - new Date(a.lastMessageTime).getTime();
    });
  }, [conversations, searchQuery, typeFilter, pinnedConversations]);

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
                    style={{ backgroundColor: AGENT_COLORS[agent.type]?.primary || '#6B7280' }}
                  >
                    {(agent.name || '?').charAt(0)}
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
      {/* Search and Filter Bar */}
      <div className="p-2 space-y-2">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索对话..."
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

        {/* Type Filter */}
        {showFilters && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setTypeFilter('all')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                typeFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              全部
            </button>
            <button
              onClick={() => setTypeFilter('private')}
              className={`px-2 py-1 text-xs rounded transition-colors flex items-center gap-1 ${
                typeFilter === 'private' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <MessageCircle size={10} />
              私聊
            </button>
            <button
              onClick={() => setTypeFilter('group')}
              className={`px-2 py-1 text-xs rounded transition-colors flex items-center gap-1 ${
                typeFilter === 'group' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <Users size={10} />
              群聊
            </button>
            {(searchQuery || typeFilter !== 'all') && (
              <span className="text-xs text-gray-500 ml-auto">
                {filteredConversations.length}/{conversations.length}
              </span>
            )}
          </div>
        )}

        {/* Mark All as Read Button */}
        {totalUnreadCount > 0 && (
          <button
            onClick={() => {
              // Mark all conversations as read by setting last viewed time to now for all
              const now = new Date().toISOString();
              const newTimes: Record<string, string> = {};
              conversations.forEach(convo => {
                newTimes[`${convo.type}-${convo.id}`] = now;
              });
              localStorage.setItem(LAST_VIEWED_KEY, JSON.stringify(newTimes));
              setLastViewedTimes(newTimes);
            }}
            className="w-full flex items-center justify-center gap-1.5 px-2 py-1.5 bg-green-600/20 text-green-400 rounded text-xs hover:bg-green-600/30 transition-colors"
          >
            <CheckCheck size={12} />
            全部标为已读 ({totalUnreadCount})
          </button>
        )}
      </div>

      {filteredConversations.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
          {conversations.length === 0 ? (
            <>
              <MessageCircle size={48} className="mb-3 opacity-50" />
              <p className="text-sm font-medium">暂无对话</p>
              <p className="text-xs text-gray-500 mt-1">点击通讯录开始聊天</p>
            </>
          ) : (
            <>
              <Inbox size={32} className="mb-2 opacity-50" />
              <p className="text-sm">未找到匹配的对话</p>
              <button
                onClick={() => { setSearchQuery(''); setTypeFilter('all'); }}
                className="text-xs text-blue-400 hover:text-blue-300 mt-2"
              >
                清除筛选
              </button>
            </>
          )}
        </div>
      ) : (
        filteredConversations.map((convo) => {
          const convoKey = `${convo.type}-${convo.id}`;
          const isPinned = pinnedConversations.has(convoKey);
          return (
          <div
            key={convoKey}
            onClick={() => handleSelectChat(convo.id, convo.type)}
            className={`p-3 cursor-pointer transition-colors group ${
              selectedChatId === convo.id && selectedChatType === convo.type
                ? 'bg-gray-700'
                : 'hover:bg-gray-700/50'
            } ${isPinned ? 'bg-gray-700/30' : ''}`}
          >
            <div className="flex items-center gap-3">
              <div className="relative">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
                  style={{ backgroundColor: convo.avatarColor }}
                >
                  {convo.type === 'group' ? (
                    <Users size={18} />
                  ) : (
                    (convo.name || '?').charAt(0).toUpperCase()
                  )}
                </div>
                {/* Unread badge */}
                {convo.unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center shadow-lg">
                    {convo.unreadCount > 99 ? '99+' : convo.unreadCount}
                  </span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {isPinned && <Pin size={10} className="text-blue-400" />}
                    <h4 className={`text-sm font-medium truncate ${convo.unreadCount > 0 ? 'text-white' : 'text-gray-300'}`}>
                      {convo.name}
                    </h4>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500 text-xs">{formatTime(convo.lastMessageTime)}</span>
                    <button
                      onClick={(e) => togglePin(e, convoKey)}
                      className={`p-1 rounded transition-colors ${
                        isPinned ? 'text-blue-400' : 'text-gray-500 opacity-0 group-hover:opacity-100 hover:text-blue-400'
                      }`}
                      title={isPinned ? '取消置顶' : '置顶会话'}
                    >
                      <Pin size={12} />
                    </button>
                  </div>
                </div>
                <p className={`text-xs truncate mt-0.5 ${convo.unreadCount > 0 ? 'text-gray-300' : 'text-gray-400'}`}>
                  {convo.lastMessage}
                </p>
              </div>
            </div>
          </div>
        );})
      )}
    </div>
  );
}
