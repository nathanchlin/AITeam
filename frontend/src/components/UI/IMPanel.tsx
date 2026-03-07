import { useState, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { ConversationList } from './ConversationList';
import { ChatDetail } from './ChatDetail';
import { ContactList } from './ContactList';
import { X, MessageCircle, Users, Plus } from 'lucide-react';

type IMView = 'messages' | 'contacts';

interface IMPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function IMPanel({ onClose }: IMPanelProps) {
  const [activeView, setActiveView] = useState<IMView>('messages');
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [selectedChatType, setSelectedChatType] = useState<'private' | 'group'>('private');
  const [showCreateGroup, setShowCreateGroup] = useState(false);

  const { agents, groupChats } = useAgentStore();

  // Reset selected chat when view changes
  useEffect(() => {
    if (activeView === 'contacts') {
      setSelectedChatId(null);
    }
  }, [activeView]);

  const handleSelectChat = (id: string, type: 'private' | 'group') => {
    setSelectedChatId(id);
    setSelectedChatType(type);
  };

  const handleStartPrivateChat = (agentId: string) => {
    setSelectedChatId(agentId);
    setSelectedChatType('private');
    setActiveView('messages');
  };

  const handleCreateGroup = () => {
    setShowCreateGroup(true);
    setActiveView('messages');
  };

  const getSelectedAgent = () => {
    if (selectedChatType !== 'private' || !selectedChatId) return null;
    return agents.find(a => a.id === selectedChatId);
  };

  const getSelectedGroupChat = () => {
    if (selectedChatType !== 'group' || !selectedChatId) return null;
    return groupChats.find(c => c.id === selectedChatId);
  };

  return (
    <div
      className="absolute left-[80px] top-2 z-20 flex transition-all duration-300"
      style={{ height: 'calc(100vh - 120px)' }}
    >
      {/* Left Navigation */}
      <div className="w-[80px] bg-gray-800/95 backdrop-blur rounded-l-lg border border-r-0 border-gray-700 flex flex-col items-center py-4 gap-2">
        <button
          onClick={() => setActiveView('messages')}
          className={`w-14 h-14 rounded-lg flex flex-col items-center justify-center gap-1 transition-colors ${
            activeView === 'messages'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:bg-gray-700 hover:text-white'
          }`}
          title="消息"
        >
          <MessageCircle size={20} />
          <span className="text-xs">消息</span>
        </button>

        <button
          onClick={() => setActiveView('contacts')}
          className={`w-14 h-14 rounded-lg flex flex-col items-center justify-center gap-1 transition-colors ${
            activeView === 'contacts'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:bg-gray-700 hover:text-white'
          }`}
          title="通讯录"
        >
          <Users size={20} />
          <span className="text-xs">通讯录</span>
        </button>

        <div className="flex-1" />

        <button
          onClick={onClose}
          className="w-14 h-14 rounded-lg flex flex-col items-center justify-center gap-1 text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
          title="关闭"
        >
          <X size={20} />
          <span className="text-xs">关闭</span>
        </button>
      </div>

      {/* Content Area */}
      <div className="w-[360px] bg-gray-800/95 backdrop-blur rounded-r-lg border border-gray-700 flex flex-col overflow-hidden">
        {activeView === 'messages' && (
          <>
            {/* Conversation List */}
            <div className="w-full border-r border-gray-700">
              <div className="p-3 border-b border-gray-700 flex items-center justify-between">
                <h3 className="text-white text-sm font-bold">消息</h3>
                <button
                  onClick={handleCreateGroup}
                  className="p-1.5 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
                  title="创建群聊"
                >
                  <Plus size={16} />
                </button>
              </div>
              <div className="h-[calc(100vh-200px)] overflow-y-auto">
                <ConversationList
                  selectedChatId={selectedChatId}
                  selectedChatType={selectedChatType}
                  onSelectChat={handleSelectChat}
                  showCreateGroup={showCreateGroup}
                  onCloseCreateGroup={() => setShowCreateGroup(false)}
                />
              </div>
            </div>
          </>
        )}

        {activeView === 'contacts' && (
          <ContactList onStartPrivateChat={handleStartPrivateChat} />
        )}
      </div>

      {/* Chat Detail Panel (shown when a chat is selected) */}
      {selectedChatId && (
        <div className="ml-2">
          <ChatDetail
            chatId={selectedChatId}
            chatType={selectedChatType}
            agent={getSelectedAgent() || undefined}
            groupChat={getSelectedGroupChat() || undefined}
            onClose={() => setSelectedChatId(null)}
          />
        </div>
      )}
    </div>
  );
}
