import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { GroupChat, GroupChatMessage, FileAttachment } from '../../types';
import { X, Send, Plus, Paperclip, MessageCircle, Users, Clock, FileText, Download } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : `http://${window.location.hostname}:8000}`;

interface GroupChatPanelProps {
  groupChats: GroupChat[];
  currentGroupChatId: string | null;
}

export function GroupChatPanel({ groupChats, currentGroupChatId }: GroupChatPanelProps) {
  const {
    setCurrentGroupChat,
    toggleGroupChatPanel,
    addGroupChatMessage,
  } = useAgentStore();

  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newChatName, setNewChatName] = useState('');
  const [newChatDescription, setNewChatDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const currentChat = groupChats.find((c) => c.id === currentGroupChatId);

  // Auto-scroll when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentChat?.messages.length]);

  const handleSendMessage = async () => {
    if (!message.trim() || !currentChat || sending) return;

    setSending(true);
    try {
      const formData = new FormData();
      formData.append('chat_id', currentChat.id);
      formData.append('content', message.trim());
      if (selectedFile) {
        formData.append('file', selectedFile);
      }

      const res = await fetch(`${API_BASE}/api/group-chat/messages`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const newMessage = await res.json();
        addGroupChatMessage(newMessage);
        setMessage('');
        setSelectedFile(null);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCreateChat = async () => {
    if (!newChatName.trim()) return;

    try {
      const res = await fetch(`${API_BASE}/api/group-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newChatName.trim(),
          description: newChatDescription.trim() || undefined,
        }),
      });

      if (res.ok) {
        const newChat = await res.json();
        setNewChatName('');
        setNewChatDescription('');
        setShowCreateModal(false);
        setCurrentGroupChat(newChat.id);
      }
    } catch (error) {
      console.error('Failed to create group chat:', error);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  const getUserAvatarColor = (name: string): string => {
    const colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  if (!currentChat) {
    return (
      <div className="absolute bottom-4 left-4 w-[800px] h-[600px] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="p-3 border-b border-gray-700 bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageCircle size={18} className="text-blue-400" />
              <h3 className="text-white text-sm font-bold">群聊</h3>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowCreateModal(true)}
                className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
                title="创建群聊"
              >
                <Plus size={16} />
              </button>
              <button
                onClick={toggleGroupChatPanel}
                className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          {groupChats.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageCircle size={48} className="mb-3 opacity-50" />
              <p className="text-sm font-medium">暂无群聊</p>
              <p className="text-xs text-gray-500 mt-1">点击上方 + 号创建新群聊</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-700">
              {groupChats.map((chat) => (
                <div
                  key={chat.id}
                  onClick={() => setCurrentGroupChat(chat.id)}
                  className="p-4 hover:bg-gray-700/50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                      style={{ backgroundColor: getUserAvatarColor(chat.name) }}
                    >
                      {chat.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-white font-medium truncate">{chat.name}</h4>
                        <span className="text-gray-500 text-xs flex items-center gap-1">
                          <Users size={12} />
                          {chat.members.length}
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm truncate">
                        {chat.description || '暂无描述'}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-gray-500 text-xs flex items-center gap-1">
                          <Clock size={10} />
                          {formatTime(chat.updated_at)}
                        </span>
                        {chat.messages.length > 0 && (
                          <span className="text-gray-500 text-xs">
                            {chat.messages.length} 条消息
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create Chat Modal */}
        {showCreateModal && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-30">
            <div className="bg-gray-800 rounded-lg p-6 w-[400px] shadow-2xl">
              <h3 className="text-white text-lg font-bold mb-4">创建群聊</h3>
              <div className="space-y-4">
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
                  <textarea
                    value={newChatDescription}
                    onChange={(e) => setNewChatDescription(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                    placeholder="输入群聊描述..."
                    rows={3}
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
                  >
                    取消
                  </button>
                  <button
                    onClick={handleCreateChat}
                    disabled={!newChatName.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                  >
                    创建
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="absolute bottom-4 left-4 w-[800px] h-[600px] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col z-20 overflow-hidden shadow-2xl border border-gray-700">
      {/* Header */}
      <div className="p-3 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentGroupChat(null)}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
          >
            <X size={16} />
          </button>
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
              style={{ backgroundColor: getUserAvatarColor(currentChat.name) }}
            >
              {currentChat.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h3 className="text-white text-sm font-bold">{currentChat.name}</h3>
              <p className="text-gray-400 text-xs flex items-center gap-2">
                <Users size={10} />
                {currentChat.members.length} 成员
              </p>
            </div>
          </div>
          <div className="w-8" />
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50">
        {currentChat.messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <MessageCircle size={48} className="mb-3 opacity-50" />
            <p className="text-sm font-medium">开始群聊</p>
            <p className="text-xs text-gray-500 mt-1">发送第一条消息</p>
          </div>
        ) : (
          currentChat.messages.map((msg) => {
            const isUser = msg.sender_type === 'user';
            const member = currentChat.members.find((m) => m.id === msg.sender_id);

            return (
              <div key={msg.id} className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs flex-shrink-0"
                  style={{
                    backgroundColor: isUser
                      ? getUserAvatarColor(msg.sender_name)
                      : member?.avatar_color || '#6B7280',
                  }}
                >
                  {msg.sender_name.charAt(0).toUpperCase()}
                </div>
                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[70%]`}>
                  <span className="text-xs text-gray-400 mb-1">{msg.sender_name}</span>
                  <div
                    className={`rounded-lg px-3 py-2 ${
                      isUser
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-gray-700 text-gray-200 rounded-bl-none'
                    }`}
                  >
                    {msg.message_type === 'system' ? (
                      <p className="text-gray-400 text-sm italic">{msg.content}</p>
                    ) : (
                      <>
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        {msg.attachments.length > 0 && (
                          <div className="mt-2 space-y-2">
                            {msg.attachments.map((attachment) => (
                              <div
                                key={attachment.id}
                                className="flex items-center gap-2 bg-black/20 rounded px-2 py-1"
                              >
                                <FileText size={14} />
                                <span className="text-xs truncate">{attachment.original_name}</span>
                                <span className="text-xs opacity-60">
                                  ({formatFileSize(attachment.file_size)})
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 mt-1">{formatTime(msg.timestamp)}</span>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-gray-700 bg-gray-800">
        {selectedFile && (
          <div className="mb-2 flex items-center gap-2 bg-gray-700 rounded px-3 py-2">
            <FileText size={14} className="text-blue-400" />
            <span className="text-sm text-gray-300 truncate flex-1">{selectedFile.name}</span>
            <span className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</span>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-gray-400 hover:text-white"
            >
              <X size={14} />
            </button>
          </div>
        )}
        <div className="flex gap-2">
          <div className="flex items-center gap-1">
            <label className="p-2 hover:bg-gray-700 rounded cursor-pointer transition-colors text-gray-400 hover:text-white">
              <input
                type="file"
                className="hidden"
                onChange={handleFileSelect}
              />
              <Paperclip size={18} />
            </label>
          </div>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Enter 发送)"
            className="flex-1 px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            rows={2}
            disabled={sending}
          />
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() && !selectedFile || sending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
