import { useState, useRef, useEffect, useMemo } from 'react';
import { X, Send, Edit2, Trash2, Check, AtSign, MessageCircle, History, Clock } from 'lucide-react';
import type { Task, Agent, TaskHistoryEntry } from '../../types';
import { useAutoResize } from '../../hooks/useAutoResize';

interface TaskCommentPanelProps {
  task: Task | null;
  agents: Agent[];
  onClose: () => void;
  onAddComment: (taskId: string, content: string, mentions?: string[]) => void;
  onEditComment: (taskId: string, commentId: string, content: string) => void;
  onDeleteComment: (taskId: string, commentId: string) => void;
}

export function TaskCommentPanel({
  task,
  agents,
  onClose,
  onAddComment,
  onEditComment,
  onDeleteComment,
}: TaskCommentPanelProps) {
  const [comment, setComment] = useState('');
  const [editingComment, setEditingComment] = useState<{ id: string; content: string } | null>(null);
  const [showMentionPicker, setShowMentionPicker] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [mentionStartPos, setMentionStartPos] = useState(-1);
  const [mentionedAgentIds, setMentionedAgentIds] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'comments' | 'history'>('comments');
  const textareaRef = useAutoResize({ value: comment, minHeight: 40, maxHeight: 120 });
  const mentionPickerRef = useRef<HTMLDivElement>(null);
  const commentsEndRef = useRef<HTMLDivElement>(null);

  // Close mention picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (mentionPickerRef.current && !mentionPickerRef.current.contains(e.target as Node)) {
        setShowMentionPicker(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-scroll to bottom when new comments arrive
  useEffect(() => {
    // Only scroll within the container, not the whole page
    if (commentsEndRef.current) {
      commentsEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [task?.comments?.length]);

  // Filter agents for mention picker
  const mentionableAgents = useMemo(() => {
    if (!mentionQuery) return agents;
    return agents.filter(a =>
      a.name.toLowerCase().includes(mentionQuery.toLowerCase())
    );
  }, [agents, mentionQuery]);

  // Handle input change
  const handleCommentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPos = e.target.selectionStart || 0;
    setComment(value);

    // Check for @ mention trigger
    const lastAtIndex = value.lastIndexOf('@', cursorPos);
    if (lastAtIndex !== -1 && lastAtIndex < cursorPos) {
      const textAfterAt = value.substring(lastAtIndex + 1, cursorPos);
      if (!textAfterAt.includes(' ')) {
        setMentionQuery(textAfterAt);
        setMentionStartPos(lastAtIndex);
        setShowMentionPicker(true);
      } else {
        setShowMentionPicker(false);
      }
    } else {
      setShowMentionPicker(false);
    }
  };

  // Insert mention
  const insertMention = (agentId: string, agentName: string) => {
    if (mentionStartPos === -1) return;
    const before = comment.substring(0, mentionStartPos);
    const after = comment.substring(textareaRef.current?.selectionStart || 0);
    const newComment = `${before}@${agentName} ${after}`;
    setComment(newComment);
    setMentionedAgentIds(prev => [...prev, agentId]);
    setShowMentionPicker(false);
    setMentionStartPos(-1);
    textareaRef.current?.focus();
  };

  // Handle submit
  const handleSubmit = () => {
    if (!task || !comment.trim()) return;
    onAddComment(task.id, comment.trim(), mentionedAgentIds.length > 0 ? mentionedAgentIds : undefined);
    setComment('');
    setMentionedAgentIds([]);
  };

  // Handle key down
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Format time
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  // Get author color
  const getAuthorColor = (authorType: string, authorName: string): string => {
    if (authorType === 'user') {
      const colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];
      const index = authorName.charCodeAt(0) % colors.length;
      return colors[index];
    }
    return '#8B5CF6'; // Agent purple
  };

  if (!task) return null;

  const comments = task.comments || [];

  // Generate history entries from task data
  const historyEntries: TaskHistoryEntry[] = useMemo(() => {
    const entries: TaskHistoryEntry[] = [];

    // Created event
    if (task.created_at) {
      entries.push({
        id: `h-created`,
        task_id: task.id,
        event_type: 'created',
        timestamp: task.created_at,
        actor: 'system'
      });
    }

    // Started event
    if (task.started_at) {
      entries.push({
        id: `h-started`,
        task_id: task.id,
        event_type: 'started',
        timestamp: task.started_at,
        actor: 'system'
      });
    }

    // Completed/Failed event
    if (task.completed_at) {
      entries.push({
        id: `h-${task.status}`,
        task_id: task.id,
        event_type: task.status === 'failed' ? 'failed' : 'completed',
        timestamp: task.completed_at,
        actor: 'system'
      });
    }

    // Archived event
    if (task.archived && task.archived_at) {
      entries.push({
        id: `h-archived`,
        task_id: task.id,
        event_type: 'archived',
        timestamp: task.archived_at,
        actor: 'user'
      });
    }

    // Sort by timestamp descending
    return entries.sort((a, b) =>
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [task]);

  // Event type display config
  const eventConfig: Record<TaskHistoryEntry['event_type'], { label: string; color: string; icon: React.ReactNode }> = {
    created: { label: 'Task Created', color: 'text-blue-400', icon: <span className="text-blue-400">📝</span> },
    started: { label: 'Started', color: 'text-yellow-400', icon: <span className="text-yellow-400">▶️</span> },
    completed: { label: 'Completed', color: 'text-green-400', icon: <span className="text-green-400">✅</span> },
    failed: { label: 'Failed', color: 'text-red-400', icon: <span className="text-red-400">❌</span> },
    archived: { label: 'Archived', color: 'text-purple-400', icon: <span className="text-purple-400">📦</span> },
    restored: { label: 'Restored', color: 'text-cyan-400', icon: <span className="text-cyan-400">↩️</span> },
    priority_changed: { label: 'Priority Changed', color: 'text-orange-400', icon: <span className="text-orange-400">🚩</span> },
    assigned: { label: 'Assigned', color: 'text-indigo-400', icon: <span className="text-indigo-400">👤</span> },
    unassigned: { label: 'Unassigned', color: 'text-gray-400', icon: <span className="text-gray-400">👤</span> },
  };

  return (
    <div className="absolute right-0 top-0 h-full w-[320px] bg-gray-800/95 backdrop-blur border-l border-gray-700 flex flex-col z-20">
      {/* Header */}
      <div className="p-3 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-white text-sm font-bold">Task Details</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
          >
            <X size={16} />
          </button>
        </div>
        {/* Tab Switcher */}
        <div className="flex bg-gray-700 rounded-lg p-0.5">
          <button
            onClick={() => setActiveTab('comments')}
            className={`flex-1 flex items-center justify-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
              activeTab === 'comments' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <MessageCircle size={12} />
            Comments ({comments.length})
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 flex items-center justify-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
              activeTab === 'history' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <History size={12} />
            History ({historyEntries.length})
          </button>
        </div>
      </div>

      {/* Task Title */}
      <div className="p-3 border-b border-gray-700 bg-gray-700/30">
        <p className="text-white text-sm font-medium truncate">{task.title}</p>
        <p className="text-gray-400 text-xs mt-0.5">ID: {task.id.slice(0, 8)}</p>
      </div>

      {/* Content Area */}
      {activeTab === 'history' ? (
        /* History List */
        <div className="flex-1 overflow-y-auto p-3">
          {historyEntries.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <History size={32} className="mb-2 opacity-50" />
              <p className="text-sm">No history yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {historyEntries.map((entry) => {
                const config = eventConfig[entry.event_type];
                return (
                  <div
                    key={entry.id}
                    className="flex items-start gap-2 p-2 bg-gray-700/50 rounded-lg"
                  >
                    <span className="text-lg">{config.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${config.color}`}>{config.label}</p>
                      <div className="flex items-center gap-1 text-gray-400 text-[10px] mt-0.5">
                        <Clock size={8} />
                        <span>{formatTime(entry.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        /* Comments List */
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {comments.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageCircle size={32} className="mb-2 opacity-50" />
              <p className="text-sm">暂无评论</p>
              <p className="text-xs text-gray-500 mt-1">添加第一条评论</p>
            </div>
          ) : (
            comments.map((c) => (
              <div key={c.id} className="group">
                {editingComment?.id === c.id ? (
                  <div className="bg-gray-700 rounded-lg p-2 space-y-2">
                    <textarea
                      value={editingComment.content}
                      onChange={(e) => setEditingComment({ ...editingComment, content: e.target.value })}
                      className="w-full px-2 py-1 bg-gray-800 text-white text-sm border border-gray-500 focus:border-blue-500 focus:outline-none rounded resize-none"
                      rows={3}
                      autoFocus
                    />
                    <div className="flex gap-1 justify-end">
                      <button
                        onClick={() => setEditingComment(null)}
                        className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded hover:bg-gray-500 transition-colors"
                      >
                        取消
                      </button>
                      <button
                        onClick={() => {
                          onEditComment(task.id, c.id, editingComment.content);
                          setEditingComment(null);
                        }}
                        className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors flex items-center gap-1"
                    >
                      <Check size={12} /> 保存
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex gap-2">
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                    style={{ backgroundColor: getAuthorColor(c.author_type, c.author_name) }}
                  >
                    {c.author_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-white text-xs font-medium">{c.author_name}</span>
                      <span className="text-gray-500 text-[10px]">{formatTime(c.timestamp)}</span>
                      {c.is_edited && (
                        <span className="text-gray-500 text-[10px]">(已编辑)</span>
                      )}
                      {/* Edit/Delete buttons */}
                      {c.author_type === 'user' && (
                        <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                          <button
                            onClick={() => setEditingComment({ id: c.id, content: c.content })}
                            className="p-0.5 hover:bg-gray-600 rounded text-gray-400 hover:text-white"
                            title="编辑"
                          >
                            <Edit2 size={10} />
                          </button>
                          <button
                            onClick={() => {
                              if (confirm('确定要删除这条评论吗？')) {
                                onDeleteComment(task.id, c.id);
                              }
                            }}
                            className="p-0.5 hover:bg-red-500/30 rounded text-gray-400 hover:text-red-400"
                            title="删除"
                          >
                            <Trash2 size={10} />
                          </button>
                        </div>
                      )}
                    </div>
                    <p className="text-gray-300 text-xs mt-0.5 whitespace-pre-wrap break-words">
                      {c.content}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
          <div ref={commentsEndRef} />
        </div>
      )}

      {/* Comment Input */}
      <div className="p-3 border-t border-gray-700">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={comment}
            onChange={handleCommentChange}
            onKeyDown={handleKeyDown}
            placeholder="添加评论... (@ 提及成员)"
            className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            style={{ minHeight: '40px', maxHeight: '120px' }}
          />
          {/* Mention Picker */}
          {showMentionPicker && mentionableAgents.length > 0 && (
            <div
              ref={mentionPickerRef}
              className="absolute bottom-full left-0 mb-1 w-full bg-gray-800 border border-gray-600 rounded-lg shadow-xl overflow-hidden z-10"
            >
              <div className="px-2 py-1 border-b border-gray-700 flex items-center gap-1 text-xs text-gray-400">
                <AtSign size={12} />
                <span>提及成员</span>
              </div>
              <div className="max-h-32 overflow-y-auto">
                {mentionableAgents.slice(0, 5).map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => insertMention(agent.id, agent.name)}
                    className="w-full text-left px-2 py-1.5 hover:bg-gray-700 transition-colors flex items-center gap-2"
                  >
                    <div
                      className="w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px]"
                      style={{ backgroundColor: '#8B5CF6' }}
                    >
                      {agent.name.charAt(0)}
                    </div>
                    <span className="text-sm text-white">{agent.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        <button
          onClick={handleSubmit}
          disabled={!comment.trim()}
          className="mt-2 w-full py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-1"
        >
          <Send size={14} />
          发送评论
        </button>
      </div>
    </div>
  );
}
