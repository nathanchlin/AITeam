import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { Agent, GroupChat } from '../../types';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { X, Send, Loader2, Users, FileText, UserPlus, Paperclip, MessageCircle } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : `http://${window.location.hostname}:8000`;

interface ChatDetailProps {
  chatId: string;
  chatType: 'private' | 'group';
  agent?: Agent;
  groupChat?: GroupChat;
  onClose: () => void;
}

export function ChatDetail({ chatType, agent, groupChat, onClose }: ChatDetailProps) {
  const {
    tasks,
    streamContent,
    updateTask,
    addTask,
    agents,
    addGroupChatMessage,
    setGroupChats,
  } = useAgentStore();

  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [addMemberAgentIds, setAddMemberAgentIds] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingRef = useRef<number | null>(null);

  // For private chat
  const agentTasks = agent ? tasks.filter((t) => t.agent_id === agent.id) : [];
  const runningTask = agentTasks.find((t) => t.status === 'running');
  const completedTasks = agentTasks.filter((t) => t.status === 'completed' && t.result);
  const currentStreamContent = runningTask ? (streamContent[runningTask.id] || '') : '';

  // For group chat
  const groupChatMessages = groupChat?.messages || [];
  const groupChatMembers = groupChat?.members || [];

  // Auto-scroll when new content arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentStreamContent, completedTasks.length, groupChatMessages.length]);

  // Poll for task updates when there's a running task
  useEffect(() => {
    if (runningTask) {
      const pollTask = async () => {
        try {
          const res = await fetch(`${API_BASE}/api/tasks/${runningTask.id}`);
          const task = await res.json();
          if (task.status === 'completed' && task.result) {
            updateTask(task.id, {
              status: 'completed',
              result: task.result,
              progress: 1,
            });
          }
        } catch (e) {
          console.error('Poll error:', e);
        }
      };

      pollingRef.current = window.setInterval(pollTask, 2000);
      return () => {
        if (pollingRef.current) clearInterval(pollingRef.current);
      };
    }
  }, [runningTask?.id, updateTask]);

  // Private chat handlers
  const handlePrivateSend = async () => {
    if (!message.trim() || sending || !agent || agent.status === 'working') return;

    setSending(true);
    try {
      const taskRes = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: message.trim(),
          agent_id: agent.id,
        }),
      });
      const task = await taskRes.json();
      addTask(task);

      await fetch(`${API_BASE}/api/tasks/${task.id}/start`, {
        method: 'POST',
      });

      updateTask(task.id, { status: 'running' });
      setMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  // Group chat handlers
  const handleGroupSend = async () => {
    if ((!message.trim() && !selectedFile) || !groupChat || sending) return;

    setSending(true);
    try {
      let res;

      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('content', message.trim());
        formData.append('sender_id', 'user');
        formData.append('sender_name', '用户');
        formData.append('sender_type', 'user');

        res = await fetch(`${API_BASE}/api/group-chats/${groupChat.id}/upload`, {
          method: 'POST',
          body: formData,
        });
      } else {
        res = await fetch(`${API_BASE}/api/group-chats/${groupChat.id}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: message.trim(),
            sender_id: 'user',
            sender_name: '用户',
            sender_type: 'user',
          }),
        });
      }

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
      if (chatType === 'private') {
        handlePrivateSend();
      } else {
        handleGroupSend();
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleAddMember = async () => {
    if (!groupChat || addMemberAgentIds.length === 0) return;

    try {
      for (const agentId of addMemberAgentIds) {
        if (groupChatMembers.some(m => m.id === agentId)) continue;

        await fetch(`${API_BASE}/api/group-chats/${groupChat.id}/members`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id: agentId }),
        });
      }

      setAddMemberAgentIds([]);
      setShowAddMemberModal(false);

      // Refresh group chats
      const res = await fetch(`${API_BASE}/api/group-chats`);
      if (res.ok) {
        const chats = await res.json();
        setGroupChats(Array.isArray(chats) ? chats : []);
      }
    } catch (error) {
      console.error('Failed to add member:', error);
    }
  };

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

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getUserAvatarColor = (name: string): string => {
    const colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  // Sort completed tasks by creation time (newest first)
  const sortedTasks = [...completedTasks].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  // Render private chat
  if (chatType === 'private' && agent) {
    return (
      <div className="w-[400px] h-[calc(100vh-120px)] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="p-3 border-b border-gray-700 flex items-center justify-between bg-gray-800">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center shadow-lg"
              style={{ backgroundColor: AGENT_COLORS[agent.type].primary }}
            >
              <span className="text-white text-sm font-bold">
                {agent.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h3 className="text-white text-sm font-bold">{agent.name}</h3>
              <p className="text-gray-400 text-xs flex items-center gap-2">
                <span>{getAgentDisplayType(agent)}</span>
                <span className={`w-2 h-2 rounded-full ${
                  agent.status === 'working' ? 'bg-green-500 animate-pulse' :
                  agent.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                }`} />
                <span>{agent.status === 'working' ? '思考中...' : '在线'}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
          >
            <X size={16} />
          </button>
        </div>

        {/* Chat Content */}
        <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-900/50">
          {sortedTasks.map((task) => (
            <div key={task.id} className="space-y-2">
              <div className="bg-gray-700/70 rounded-lg p-3 text-sm text-gray-300">
                {task.title}
              </div>
              {task.result && (
                <div className="bg-gradient-to-r from-blue-600/30 to-purple-600/30 rounded-lg p-3 text-sm text-white whitespace-pre-wrap border-l-2 border-blue-500">
                  {task.result}
                </div>
              )}
            </div>
          ))}

          {runningTask && (
            <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300">
              {runningTask.title}
            </div>
          )}

          {currentStreamContent && (
            <div className="bg-gradient-to-r from-blue-600/30 to-purple-600/30 rounded-lg p-3 text-sm text-white whitespace-pre-wrap border-l-2 border-green-500 animate-pulse">
              {currentStreamContent}
            </div>
          )}

          {sortedTasks.length === 0 && !currentStreamContent && !runningTask && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <div className="text-5xl mb-3">💬</div>
              <p className="text-sm font-medium">开始和 {agent.name} 对话吧</p>
              <p className="text-xs text-gray-500 mt-1">输入问题或任务，Agent 会实时响应</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="p-3 border-t border-gray-700 bg-gray-800">
          <div className="flex gap-2">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={agent.status === 'working' ? 'Agent 正在思考...' : '输入消息... (Enter 发送)'}
              className="flex-1 px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
              rows={2}
              disabled={sending || agent.status === 'working'}
            />
            <button
              onClick={handlePrivateSend}
              disabled={!message.trim() || sending || agent.status === 'working'}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
            >
              {sending || agent.status === 'working' ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render group chat
  if (chatType === 'group' && groupChat) {
    return (
      <div className="w-[400px] h-[calc(100vh-120px)] bg-gray-800/95 backdrop-blur rounded-lg flex flex-col overflow-hidden shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="p-3 border-b border-gray-700 bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                style={{ backgroundColor: getUserAvatarColor(groupChat.name) }}
              >
                <Users size={18} />
              </div>
              <div>
                <h3 className="text-white text-sm font-bold">{groupChat.name}</h3>
                <p className="text-gray-400 text-xs flex items-center gap-2">
                  <Users size={10} />
                  {groupChatMembers.length} 成员
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setShowAddMemberModal(true)}
                className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
                title="邀请成员"
              >
                <UserPlus size={16} />
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50">
          {groupChatMessages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageCircle size={48} className="mb-3 opacity-50" />
              <p className="text-sm font-medium">开始群聊</p>
              <p className="text-xs text-gray-500 mt-1">发送第一条消息</p>
            </div>
          ) : (
            groupChatMessages.map((msg) => {
              const isUser = msg.sender_type === 'user';
              const member = groupChatMembers.find((m) => m.id === msg.sender_id);

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
              onClick={handleGroupSend}
              disabled={!message.trim() && !selectedFile || sending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
            >
              <Send size={18} />
            </button>
          </div>
        </div>

        {/* Add Member Modal */}
        {showAddMemberModal && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-30">
            <div className="bg-gray-800 rounded-lg p-6 w-[350px] shadow-2xl max-h-[80vh] overflow-y-auto">
              <h3 className="text-white text-lg font-bold mb-4">邀请成员</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-gray-400 text-xs block mb-2">选择要邀请的 Agent</label>
                  <div className="max-h-48 overflow-y-auto space-y-1 bg-gray-700/50 rounded p-2">
                    {agents.filter(a => !groupChatMembers.some(m => m.id === a.id)).length === 0 ? (
                      <p className="text-gray-400 text-sm text-center py-4">所有 Agent 都已在群聊中</p>
                    ) : (
                      agents
                        .filter(a => !groupChatMembers.some(m => m.id === a.id))
                        .map((a) => (
                          <label
                            key={a.id}
                            className="flex items-center gap-2 cursor-pointer hover:bg-gray-600/50 p-2 rounded transition-colors"
                          >
                            <input
                              type="checkbox"
                              checked={addMemberAgentIds.includes(a.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setAddMemberAgentIds([...addMemberAgentIds, a.id]);
                                } else {
                                  setAddMemberAgentIds(addMemberAgentIds.filter(id => id !== a.id));
                                }
                              }}
                              className="rounded bg-gray-600 border-gray-500 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-800"
                            />
                            <div
                              className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs flex-shrink-0"
                              style={{ backgroundColor: AGENT_COLORS[a.type].primary }}
                            >
                              {a.name.charAt(0)}
                            </div>
                            <span className="text-white text-sm truncate">{a.name}</span>
                          </label>
                        ))
                    )}
                  </div>
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => {
                      setShowAddMemberModal(false);
                      setAddMemberAgentIds([]);
                    }}
                    className="px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
                  >
                    取消
                  </button>
                  <button
                    onClick={handleAddMember}
                    disabled={addMemberAgentIds.length === 0}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                  >
                    邀请
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
}
