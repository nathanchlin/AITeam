import { useState, useRef, useEffect, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { GroupChat, GroupChatMessage, MessageReaction } from '../../types';
import { X, Send, Plus, Paperclip, MessageCircle, Users, Clock, FileText, UserPlus, AtSign, Reply, CornerDownRight, Search, Edit2, Trash2, Check, XCircle, Star, Bookmark, CheckCheck, Pin, Forward, Upload, Copy } from 'lucide-react';
import { useAutoResize } from '../../hooks/useAutoResize';
import { MessageSearch } from './MessageSearch';
import { ReactionPicker, ReactionDisplay } from './ReactionPicker';
import { highlightCode, parseCodeBlocks } from '../../utils/syntaxHighlight';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

interface GroupChatPanelProps {
  groupChats: GroupChat[];
  currentGroupChatId: string | null;
}

export function GroupChatPanel({ groupChats: groupChatsProp, currentGroupChatId }: GroupChatPanelProps) {
  const {
    agents,
    setCurrentGroupChat,
    toggleGroupChatPanel,
    addGroupChatMessage,
    setGroupChats,
  } = useAgentStore();

  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newChatName, setNewChatName] = useState('');
  const [newChatDescription, setNewChatDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useAutoResize({ value: message, minHeight: 40, maxHeight: 200 });

  // Agent multi-select for creating group chat
  const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([]);

  // Add member modal state
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [addMemberAgentIds, setAddMemberAgentIds] = useState<string[]>([]);

  // @ mention state
  const [showMentionPicker, setShowMentionPicker] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [mentionStartPos, setMentionStartPos] = useState(-1);
  const [mentionedAgentIds, setMentionedAgentIds] = useState<string[]>([]);
  const [replyingTo, setReplyingTo] = useState<{ id: string; content: string; sender_name: string } | null>(null);
  const [showSearch, setShowSearch] = useState(false);
  const [highlightedMessageId, setHighlightedMessageId] = useState<string | null>(null);
  const [messageReactions, setMessageReactions] = useState<Record<string, MessageReaction[]>>({});
  const [editingMessage, setEditingMessage] = useState<{ id: string; content: string } | null>(null);
  const [recalledMessages, setRecalledMessages] = useState<Set<string>>(new Set());
  const [editedMessages, setEditedMessages] = useState<Record<string, string>>({});
  const [bookmarkedMessages, setBookmarkedMessages] = useState<Set<string>>(new Set());
  const [showBookmarks, setShowBookmarks] = useState(false);
  const [bookmarkSearchQuery, setBookmarkSearchQuery] = useState('');
  const [readMessages, setReadMessages] = useState<Set<string>>(new Set());
  const [pinnedMessages, setPinnedMessages] = useState<Set<string>>(new Set());
  // Forward state
  const [showForwardModal, setShowForwardModal] = useState(false);
  const [forwardingMessage, setForwardingMessage] = useState<GroupChatMessage | null>(null);
  const [forwardTargetIds, setForwardTargetIds] = useState<string[]>([]);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const mentionPickerRef = useRef<HTMLDivElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  // Drag and drop state
  const [isDraggingOver, setIsDraggingOver] = useState(false);

  // Current user name for reactions
  const currentUserName = 'You';

  // Time limits
  const EDIT_TIME_LIMIT = 5 * 60 * 1000; // 5 minutes
  const RECALL_TIME_LIMIT = 2 * 60 * 1000; // 2 minutes

  // Check if message can be edited
  const canEditMessage = (msg: GroupChatMessage): boolean => {
    if (msg.sender_type !== 'user') return false;
    const msgTime = new Date(msg.timestamp).getTime();
    const now = Date.now();
    return (now - msgTime) < EDIT_TIME_LIMIT;
  };

  // Check if message can be recalled
  const canRecallMessage = (msg: GroupChatMessage): boolean => {
    if (msg.sender_type !== 'user') return false;
    const msgTime = new Date(msg.timestamp).getTime();
    const now = Date.now();
    return (now - msgTime) < RECALL_TIME_LIMIT;
  };

  // Handle edit message
  const handleStartEdit = (msg: GroupChatMessage) => {
    setEditingMessage({ id: msg.id, content: editedMessages[msg.id] || msg.content });
  };

  const handleCancelEdit = () => {
    setEditingMessage(null);
  };

  const handleSaveEdit = () => {
    if (editingMessage) {
      setEditedMessages(prev => ({
        ...prev,
        [editingMessage.id]: editingMessage.content,
      }));
      setEditingMessage(null);
    }
  };

  // Handle recall message
  const handleRecallMessage = (messageId: string) => {
    if (confirm('确定要撤回这条消息吗？')) {
      setRecalledMessages(prev => new Set(prev).add(messageId));
    }
  };

  // Get display content for a message
  const getDisplayContent = (msg: GroupChatMessage): string => {
    return editedMessages[msg.id] || msg.content;
  };

  // Check if message is recalled
  const isMessageRecalled = (messageId: string): boolean => {
    return recalledMessages.has(messageId);
  };

  // Check if message is edited
  const isMessageEdited = (messageId: string): boolean => {
    return messageId in editedMessages;
  };

  // Get reactions for a message
  const getReactions = (msg: GroupChatMessage): MessageReaction[] => {
    return messageReactions[msg.id] || msg.reactions || [];
  };

  // Handle add reaction
  const handleAddReaction = (messageId: string, emoji: string) => {
    setMessageReactions(prev => {
      const current = prev[messageId] || [];
      const existing = current.find(r => r.emoji === emoji);

      if (existing) {
        if (!existing.users.includes(currentUserName)) {
          return {
            ...prev,
            [messageId]: current.map(r =>
              r.emoji === emoji ? { ...r, users: [...r.users, currentUserName] } : r
            ),
          };
        }
        return prev;
      } else {
        return {
          ...prev,
          [messageId]: [...current, { emoji, users: [currentUserName] }],
        };
      }
    });
  };

  // Handle remove reaction
  const handleRemoveReaction = (messageId: string, emoji: string) => {
    setMessageReactions(prev => {
      const current = prev[messageId] || [];
      return {
        ...prev,
        [messageId]: current
          .map(r =>
            r.emoji === emoji ? { ...r, users: r.users.filter(u => u !== currentUserName) } : r
          )
          .filter(r => r.users.length > 0),
      };
    });
  };

  // Toggle reaction (for ReactionDisplay)
  const handleToggleReaction = (messageId: string, emoji: string) => {
    const reactions = getReactions({ id: messageId } as GroupChatMessage);
    const existing = reactions.find(r => r.emoji === emoji);
    if (existing && existing.users.includes(currentUserName)) {
      handleRemoveReaction(messageId, emoji);
    } else {
      handleAddReaction(messageId, emoji);
    }
  };

  // Handle bookmark toggle
  const handleToggleBookmark = (messageId: string) => {
    setBookmarkedMessages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  // Check if message is bookmarked
  const isMessageBookmarked = (messageId: string): boolean => {
    return bookmarkedMessages.has(messageId);
  };

  // Handle pin message toggle
  const handleTogglePin = (messageId: string) => {
    if (pinnedMessages.has(messageId)) {
      setPinnedMessages(prev => {
        const newSet = new Set(prev);
        newSet.delete(messageId);
        return newSet;
      });
    } else {
      // Limit to 5 pinned messages
      if (pinnedMessages.size >= 5) {
        alert('最多只能置顶 5 条消息');
        return;
      }
      setPinnedMessages(prev => new Set(prev).add(messageId));
    }
  };

  // Check if message is pinned
  const isMessagePinned = (messageId: string): boolean => {
    return pinnedMessages.has(messageId);
  };

  // Forward message handlers
  const handleOpenForward = (msg: GroupChatMessage) => {
    setForwardingMessage(msg);
    setForwardTargetIds([]);
    setShowForwardModal(true);
  };

  const handleToggleForwardTarget = (targetId: string) => {
    setForwardTargetIds(prev =>
      prev.includes(targetId)
        ? prev.filter(id => id !== targetId)
        : [...prev, targetId]
    );
  };

  const handleConfirmForward = () => {
    if (!forwardingMessage || forwardTargetIds.length === 0) return;

    // Forward to selected chats
    forwardTargetIds.forEach(chatId => {
      const forwardedContent = `[转发自 ${forwardingMessage.sender_name}]\n${forwardingMessage.content}`;
      const newMessage: GroupChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        chat_id: chatId,
        sender_id: 'user',
        sender_name: 'You',
        sender_type: 'user',
        content: forwardedContent,
        message_type: 'text',
        attachments: [],
        timestamp: new Date().toISOString(),
      };
      addGroupChatMessage(newMessage);
    });

    setShowForwardModal(false);
    setForwardingMessage(null);
    setForwardTargetIds([]);
  };

  const handleCloseForwardModal = () => {
    setShowForwardModal(false);
    setForwardingMessage(null);
    setForwardTargetIds([]);
  };

  // Get pinned messages for current chat
  const getPinnedMessages = () => {
    if (!currentChat) return [];
    return currentChat.messages.filter(msg => pinnedMessages.has(msg.id));
  };

  // Mark all messages as read
  const markAllAsRead = () => {
    if (!currentChat) return;
    const allMessageIds = currentChat.messages.map(m => m.id);
    setReadMessages(new Set(allMessageIds));
  };

  // Get unread count
  const getUnreadCount = () => {
    if (!currentChat) return 0;
    return currentChat.messages.filter(m => !readMessages.has(m.id)).length;
  };

  // Check if message is read
  const isMessageRead = (messageId: string): boolean => {
    return readMessages.has(messageId);
  };

  // Ensure groupChats is always an array
  const groupChats = Array.isArray(groupChatsProp) ? groupChatsProp : [];
  const currentChat = groupChats.find((c) => c.id === currentGroupChatId);

  const getBookmarkedMessages = () => {
    if (!currentChat) return [];
    return currentChat.messages.filter(msg => bookmarkedMessages.has(msg.id));
  };

  // Filter bookmarked messages by search query
  const filteredBookmarks = useMemo(() => {
    const bookmarks = getBookmarkedMessages();
    if (!bookmarkSearchQuery.trim()) return bookmarks;
    const query = bookmarkSearchQuery.toLowerCase();
    return bookmarks.filter(msg =>
      msg.content.toLowerCase().includes(query) ||
      msg.sender_name.toLowerCase().includes(query)
    );
  }, [bookmarkedMessages, currentChat?.messages, bookmarkSearchQuery]);

  // Auto-scroll when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentChat?.messages.length]);

  // Mark all messages as read when opening the chat
  useEffect(() => {
    if (currentChat && currentChat.messages.length > 0) {
      // Mark all existing messages as read when opening the chat
      markAllAsRead();
    }
  }, [currentChat?.id]); // Only when chat changes

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

  // Filter agents for mention picker
  const mentionableAgents = useMemo(() => {
    return currentChat?.members
      .map(member => agents.find(a => a.id === member.id))
      .filter((a): a is NonNullable<typeof a> => !!a)
      .filter(a =>
        a.name.toLowerCase().includes(mentionQuery.toLowerCase())
      ) || [];
  }, [currentChat?.members, agents, mentionQuery]);

  // Handle input change with @ detection
  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPos = e.target.selectionStart || 0;

    // Find @ symbol before cursor
    const textBeforeCursor = value.substring(0, cursorPos);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtIndex !== -1) {
      // Check if there's a space between @ and cursor (which would cancel the mention)
      const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1);
      if (!textAfterAt.includes(' ') && !textAfterAt.includes('\n')) {
        setMentionStartPos(lastAtIndex);
        setMentionQuery(textAfterAt);
        setShowMentionPicker(true);
      } else {
        setShowMentionPicker(false);
      }
    } else {
      setShowMentionPicker(false);
    }

    setMessage(value);
  };

  // Insert mention into message
  const insertMention = (agentId: string, agentName: string) => {
    if (mentionStartPos === -1) return;

    const beforeMention = message.substring(0, mentionStartPos);
    const afterCursor = message.substring(textareaRef.current?.selectionStart || 0);

    const newMessage = `${beforeMention}@${agentName} ${afterCursor}`;
    setMessage(newMessage);
    setMentionedAgentIds(prev => [...prev, agentId]);
    setShowMentionPicker(false);
    setMentionQuery('');
    setMentionStartPos(-1);

    // Focus back to textarea
    setTimeout(() => {
      textareaRef.current?.focus();
      const newCursorPos = beforeMention.length + agentName.length + 2;
      textareaRef.current?.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  // Parse message content to highlight mentions and code blocks
  const renderMessageContent = (content: string) => {
    // First parse code blocks
    const parsedParts = parseCodeBlocks(content);
    const result: React.ReactNode[] = [];
    let key = 0;

    parsedParts.forEach((part, partIndex) => {
      if (part.type === 'code') {
        // Render code block with syntax highlighting
        result.push(
          <div key={`code-${partIndex}`} className="my-2 relative group">
            <div className="flex items-center justify-between bg-gray-900 px-3 py-1 rounded-t-lg border-b border-gray-700">
              <span className="text-xs text-gray-400 font-mono">{part.language || 'code'}</span>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(part.content);
                }}
                className="text-gray-400 hover:text-white p-1 rounded transition-colors"
                title="复制代码"
              >
                <Copy size={12} />
              </button>
            </div>
            <pre className="bg-gray-900/80 p-3 rounded-b-lg overflow-x-auto text-sm font-mono">
              <code>{highlightCode(part.content, part.language || 'plaintext')}</code>
            </pre>
          </div>
        );
      } else if (part.type === 'inline-code') {
        // Render inline code
        result.push(
          <code
            key={`inline-${partIndex}`}
            className="bg-gray-700 text-pink-400 px-1.5 py-0.5 rounded text-sm font-mono"
          >
            {part.content}
          </code>
        );
      } else {
        // Render text with mention highlighting
        const textContent = part.content;
        const textParts: React.ReactNode[] = [];
        let lastIndex = 0;
        const mentionRegex = /@(\S+)/g;
        let match;

        while ((match = mentionRegex.exec(textContent)) !== null) {
          // Add text before mention
          if (match.index > lastIndex) {
            textParts.push(textContent.substring(lastIndex, match.index));
          }

          // Check if mentioned agent exists
          const mentionedName = match[1];
          const mentionedAgent = agents.find(a =>
            a.name === mentionedName ||
            a.name.toLowerCase() === mentionedName.toLowerCase()
          );

          if (mentionedAgent) {
            textParts.push(
              <span
                key={key++}
                className="bg-blue-500/30 text-blue-300 px-1 rounded cursor-pointer hover:bg-blue-500/50"
                title={mentionedAgent.type}
              >
                @{mentionedName}
              </span>
            );
          } else {
            textParts.push(
              <span key={key++} className="text-gray-400">
                @{mentionedName}
              </span>
            );
          }

          lastIndex = match.index + match[0].length;
        }

        // Add remaining text
        if (lastIndex < textContent.length) {
          textParts.push(textContent.substring(lastIndex));
        }

        result.push(...textParts);
      }
    });

    return result.length > 0 ? result : content;
  };

  const handleSendMessage = async () => {
    if ((!message.trim() && !selectedFile) || !currentChat || sending) return;

    setSending(true);
    try {
      let res;

      if (selectedFile) {
        // Use upload endpoint for file attachments
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('content', message.trim());
        formData.append('sender_id', 'user');
        formData.append('sender_name', '用户');
        formData.append('sender_type', 'user');
        if (replyingTo) {
        formData.append('reply_to', JSON.stringify(replyingTo));
        }

        res = await fetch(`${API_BASE}/api/group-chats/${currentChat.id}/upload`, {
          method: 'POST',
          body: formData,
        });
      } else {
        // Use messages endpoint for text-only messages
        const body: any = {
          content: message.trim(),
          sender_id: 'user',
          sender_name: '用户',
          sender_type: 'user',
          mentions: mentionedAgentIds.length > 0 ? mentionedAgentIds : undefined,
        };
        if (replyingTo) {
          body.reply_to_id = replyingTo.id;
        }

        res = await fetch(`${API_BASE}/api/group-chats/${currentChat.id}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
      }

      if (res.ok) {
        const newMessage = await res.json();
        addGroupChatMessage(newMessage);
        setMessage('');
        setSelectedFile(null);
        setMentionedAgentIds([]);
        setReplyingTo(null);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  // Handle reply to message
  const handleReply = (msg: { id: string; content: string; sender_name: string }) => {
    setReplyingTo(msg);
  };

  // Cancel reply
  const cancelReply = () => {
    setReplyingTo(null);
  };

  // Scroll to message
  const scrollToMessage = (messageId: string) => {
    const messageEl = messagesContainerRef.current?.querySelector(`[data-message-id="${messageId}"]`);
    if (messageEl) {
      messageEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setHighlightedMessageId(messageId);
      setTimeout(() => {
        setHighlightedMessageId(null);
      }, 2000);
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
        setNewChatName('');
        setNewChatDescription('');
        setSelectedAgentIds([]);
        setShowCreateModal(false);
        // Refresh group chats list
        await refreshGroupChats();
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

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.types.includes('Files')) {
      setIsDraggingOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set false if leaving the drop zone entirely
    if (dropZoneRef.current && !dropZoneRef.current.contains(e.relatedTarget as Node)) {
      setIsDraggingOver(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('文件大小不能超过 10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleAddMember = async () => {
    if (!currentChat || addMemberAgentIds.length === 0) return;

    try {
      for (const agentId of addMemberAgentIds) {
        // Skip if already a member
        if (currentChat.members.some(m => m.id === agentId)) continue;

        await fetch(`${API_BASE}/api/group-chats/${currentChat.id}/members`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id: agentId }),
        });
      }

      setAddMemberAgentIds([]);
      setShowAddMemberModal(false);
      await refreshGroupChats();
    } catch (error) {
      console.error('Failed to add member:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatTime = (timestamp: string): string => {
    // Add 'Z' suffix if not present to indicate UTC time
    const utcTimestamp = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
    const date = new Date(utcTimestamp);
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

  const getAgentColor = (type: string): string => {
    const typeColors: Record<string, string> = {
      Coder: '#3B82F6',
      Analyst: '#10B981',
      Assistant: '#8B5CF6',
      Tester: '#F59E0B',
    };
    return typeColors[type] || '#6B7280';
  };

  const refreshGroupChats = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/group-chats`);
      if (res.ok) {
        const chats = await res.json();
        setGroupChats(Array.isArray(chats) ? chats : []);
      }
    } catch (error) {
      console.error('Failed to refresh group chats:', error);
    }
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
                      {(chat.name || '?').charAt(0).toUpperCase()}
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
            <div className="bg-gray-800 rounded-lg p-6 w-[400px] shadow-2xl max-h-[80vh] overflow-y-auto">
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
                    rows={2}
                  />
                </div>
                <div>
                  <label className="text-gray-400 text-xs block mb-2">选择成员</label>
                  <div className="max-h-40 overflow-y-auto space-y-1 bg-gray-700/50 rounded p-2">
                    {agents.length === 0 ? (
                      <p className="text-gray-400 text-sm text-center py-2">暂无可选 Agent</p>
                    ) : (
                      agents.map((agent) => (
                        <label
                          key={agent.id}
                          className="flex items-center gap-2 cursor-pointer hover:bg-gray-600/50 p-2 rounded transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={selectedAgentIds.includes(agent.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedAgentIds([...selectedAgentIds, agent.id]);
                              } else {
                                setSelectedAgentIds(selectedAgentIds.filter(id => id !== agent.id));
                              }
                            }}
                            className="rounded bg-gray-600 border-gray-500 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-800"
                          />
                          <div
                            className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs flex-shrink-0"
                            style={{ backgroundColor: getAgentColor(agent.type) }}
                          >
                            {(agent.name || '?').charAt(0)}
                          </div>
                          <span className="text-white text-sm truncate">{agent.name}</span>
                          <span className="text-gray-400 text-xs">({agent.type})</span>
                        </label>
                      ))
                    )}
                  </div>
                  {selectedAgentIds.length > 0 && (
                    <p className="text-blue-400 text-xs mt-1">已选择 {selectedAgentIds.length} 个 Agent</p>
                  )}
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      setSelectedAgentIds([]);
                    }}
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
              {(currentChat.name || '?').charAt(0).toUpperCase()}
            </div>
            <div>
              <h3 className="text-white text-sm font-bold">{currentChat.name}</h3>
              <p className="text-gray-400 text-xs flex items-center gap-2">
                <Users size={10} />
                {currentChat.members.length} 成员
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowAddMemberModal(true)}
            className="p-2 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
            title="邀请成员"
          >
            <UserPlus size={16} />
          </button>
          <button
            onClick={() => setShowSearch(!showSearch)}
            disabled={!currentChat.messages || currentChat.messages.length === 0}
            className={`p-2 rounded transition-colors ${
              showSearch ? 'bg-purple-600 text-white' : 'hover:bg-gray-700 text-gray-400'
            } disabled:opacity-30 disabled:cursor-not-allowed`}
            title="搜索消息"
          >
            <Search size={16} />
          </button>
          <button
            onClick={markAllAsRead}
            disabled={getUnreadCount() === 0}
            className={`p-2 rounded transition-colors relative ${
              getUnreadCount() > 0 ? 'bg-green-600/30 text-green-400 hover:bg-green-600/50' : 'hover:bg-gray-700 text-gray-400'
            } disabled:opacity-30 disabled:cursor-not-allowed`}
            title="全部标记已读"
          >
            <CheckCheck size={16} />
            {getUnreadCount() > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 text-white text-[10px] rounded-full flex items-center justify-center">
                {getUnreadCount()}
              </span>
            )}
          </button>
          <button
            onClick={() => setShowBookmarks(!showBookmarks)}
            disabled={bookmarkedMessages.size === 0}
            className={`p-2 rounded transition-colors relative ${
              showBookmarks ? 'bg-yellow-600 text-white' : 'hover:bg-gray-700 text-gray-400'
            } disabled:opacity-30 disabled:cursor-not-allowed`}
            title="收藏消息"
          >
            <Bookmark size={16} />
            {bookmarkedMessages.size > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-500 text-white text-[10px] rounded-full flex items-center justify-center">
                {bookmarkedMessages.size}
              </span>
            )}
          </button>
          <button
            onClick={markAllAsRead}
            disabled={getUnreadCount() === 0}
            className="p-2 rounded transition-colors text-gray-400 hover:bg-gray-700"
            title="全部标记已读"
          >
            <CheckCheck size={16} />
            {getUnreadCount() > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">
                {getUnreadCount()}
              </span>
            )}
          </button>
        </div>

        {/* Member Status Row */}
        <div className="mt-2 flex flex-wrap gap-1.5">
          {currentChat.members.slice(0, 8).map((member) => {
            const agent = agents.find(a => a.id === member.id);
            const status = agent?.status || 'idle';
            const statusDotColor = status === 'working' ? '#22C55E' :
                                   status === 'error' ? '#EF4444' :
                                   status === 'waiting' ? '#EAB308' : '#9CA3AF';
            const statusText = status === 'working' ? '工作中' :
                              status === 'error' ? '错误' :
                              status === 'waiting' ? '等待中' : '在线';

            return (
              <div
                key={member.id}
                className="flex items-center gap-1 px-2 py-0.5 bg-gray-700/50 rounded-full"
                title={`${member.name}: ${statusText}`}
              >
                <div
                  className="w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px] font-bold"
                  style={{ backgroundColor: member.avatar_color || '#6B7280' }}
                >
                  {(member.name || '?').charAt(0).toUpperCase()}
                </div>
                <span
                  className={`w-2 h-2 rounded-full ${status === 'working' ? 'animate-pulse' : ''}`}
                  style={{ backgroundColor: statusDotColor }}
                />
              </div>
            );
          })}
          {currentChat.members.length > 8 && (
            <span className="text-xs text-gray-500 self-center">
              +{currentChat.members.length - 8}
            </span>
          )}
        </div>
      </div>

      {/* Pinned Messages Area */}
      {getPinnedMessages().length > 0 && (
        <div className="mb-3 p-2 bg-blue-900/20 border border-blue-500/30 rounded-lg">
          <div className="flex items-center gap-2 px-3 py-2 text-blue-400 text-sm">
            <Pin size={14} />
            <span>{getPinnedMessages().length} 条置顶消息</span>
          </div>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {getPinnedMessages().map(msg => (
              <div key={msg.id} className="bg-gray-800/80 rounded px-3 py-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-300">{msg.sender_name}</span>
                  <span className="text-xs text-gray-500">{formatTime(msg.timestamp)}</span>
                  <button
                    onClick={() => handleTogglePin(msg.id)}
                    className="text-gray-400 hover:text-red-400 ml-auto"
                  >
                    <X size={12} />
                  </button>
                </div>
                <p className="text-gray-400 text-sm truncate">{msg.content.substring(0, 100)}...</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50 relative">
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
              <div
                key={msg.id}
                data-message-id={msg.id}
                className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''} group relative transition-all duration-300 ${
                  highlightedMessageId === msg.id ? 'ring-2 ring-purple-500 rounded-lg p-2 -m-2 bg-purple-500/10' : ''
                }`}
              >
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
                    } relative group`}
                  >
                    {/* Action buttons on hover */}
                    {msg.message_type !== 'system' && !isMessageRecalled(msg.id) && (
                      <div className="absolute -left-1 top-1 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleReply({ id: msg.id, content: getDisplayContent(msg), sender_name: msg.sender_name })}
                          className="p-1 rounded bg-gray-600 text-gray-300 hover:bg-gray-500 transition-colors"
                          title="引用回复"
                        >
                          <Reply size={12} />
                        </button>
                        <button
                          onClick={() => handleToggleBookmark(msg.id)}
                          className={`p-1 rounded transition-colors ${
                            isMessageBookmarked(msg.id)
                              ? 'bg-yellow-500/30 text-yellow-400'
                              : 'bg-gray-600 text-gray-300 hover:bg-yellow-500/30 hover:text-yellow-400'
                          }`}
                          title={isMessageBookmarked(msg.id) ? '取消收藏' : '收藏消息'}
                        >
                          <Star size={12} fill={isMessageBookmarked(msg.id) ? 'currentColor' : 'none'} />
                        </button>
                        {msg.sender_type === 'user' && canEditMessage(msg) && (
                          <button
                            onClick={() => handleStartEdit(msg)}
                            className="p-1 rounded bg-gray-600 text-gray-300 hover:bg-blue-500 transition-colors"
                            title="编辑消息"
                          >
                            <Edit2 size={12} />
                          </button>
                        )}
                        {msg.sender_type === 'user' && canRecallMessage(msg) && (
                          <button
                            onClick={() => handleRecallMessage(msg.id)}
                            className="p-1 rounded bg-gray-600 text-gray-300 hover:bg-red-500 transition-colors"
                            title="撤回消息"
                          >
                            <Trash2 size={12} />
                          </button>
                        )}
                      </div>
                    )}
                    {/* Reaction button on hover */}
                    {msg.message_type !== 'system' && !isMessageRecalled(msg.id) && (
                      <div className="absolute -right-1 top-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <ReactionPicker
                          reactions={getReactions(msg)}
                          currentUserName={currentUserName}
                          onAddReaction={(emoji) => handleAddReaction(msg.id, emoji)}
                          onRemoveReaction={(emoji) => handleRemoveReaction(msg.id, emoji)}
                          showTrigger={true}
                        />
                      </div>
                    )}
                    {msg.message_type === 'system' ? (
                      <p className="text-gray-400 text-sm italic">{msg.content}</p>
                    ) : isMessageRecalled(msg.id) ? (
                      <p className="text-gray-500 text-sm italic">消息已撤回</p>
                    ) : editingMessage?.id === msg.id ? (
                      <div className="space-y-2">
                        <textarea
                          value={editingMessage.content}
                          onChange={(e) => setEditingMessage({ ...editingMessage, content: e.target.value })}
                          className="w-full px-2 py-1 bg-gray-800 text-white text-sm border border-gray-500 focus:border-blue-500 focus:outline-none rounded resize-none"
                          rows={3}
                          autoFocus
                        />
                        <div className="flex gap-1 justify-end">
                          <button
                            onClick={handleCancelEdit}
                            className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded hover:bg-gray-500 transition-colors flex items-center gap-1"
                          >
                            <XCircle size={12} /> 取消
                          </button>
                          <button
                            onClick={handleSaveEdit}
                            className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors flex items-center gap-1"
                          >
                            <Check size={12} /> 保存
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {/* Reply preview */}
                        {(msg as any).reply_to && (
                          <button
                            onClick={() => scrollToMessage((msg as any).reply_to.id)}
                            className="flex items-center gap-2 bg-black/30 rounded px-2 py-1 mb-1 text-left w-full hover:bg-black/40 transition-colors"
                          >
                            <CornerDownRight size={10} className="text-gray-400" />
                            <div className="flex-1 min-w-0">
                              <span className="text-xs text-gray-400 font-medium">
                                {(msg as any).reply_to.sender_name}
                              </span>
                              <span className="text-xs text-gray-500 truncate">
                                {(msg as any).reply_to.content.substring(0, 50)}...
                              </span>
                            </div>
                          </button>
                        )}
                        <p className="text-sm whitespace-pre-wrap">{renderMessageContent(getDisplayContent(msg))}</p>
                        {isMessageEdited(msg.id) && (
                          <span className="text-[10px] text-gray-500 mt-0.5 block">已编辑</span>
                        )}
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
                  <div className="flex items-center gap-2 mt-1">
                    {isMessageBookmarked(msg.id) && (
                      <Star size={10} className="text-yellow-500" fill="currentColor" />
                    )}
                    {!isMessageRead(msg.id) && msg.message_type !== 'system' && (
                      <span className="w-2 h-2 rounded-full bg-blue-500" title="未读" />
                    )}
                    <span className="text-xs text-gray-500">{formatTime(msg.timestamp)}</span>
                    {/* Reaction Display */}
                    {msg.message_type !== 'system' && getReactions(msg).length > 0 && (
                      <ReactionDisplay
                        reactions={getReactions(msg)}
                        currentUserName={currentUserName}
                        onToggleReaction={(emoji) => handleToggleReaction(msg.id, emoji)}
                      />
                    )}
                    {/* Pin Button */}
                    {msg.message_type !== 'system' && !isMessageRecalled(msg.id) && (
                      <button
                        onClick={() => handleTogglePin(msg.id)}
                        className={`p-1 rounded transition-colors ${
                          isMessagePinned(msg.id) ? 'text-blue-400 hover:bg-blue-500/20' : 'text-gray-400 hover:text-blue-400 hover:bg-gray-600'
                        }`}
                        title={isMessagePinned(msg.id) ? '取消置顶' : '置顶消息'}
                      >
                        <Pin size={12} fill={isMessagePinned(msg.id) ? 'currentColor' : undefined} />
                      </button>
                    )}
                    {/* Forward Button */}
                    {msg.message_type !== 'system' && !isMessageRecalled(msg.id) && (
                      <button
                        onClick={() => handleOpenForward(msg)}
                        className="p-1 rounded text-gray-400 hover:text-green-400 hover:bg-gray-600 transition-colors"
                        title="转发消息"
                      >
                        <Forward size={12} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        ref={dropZoneRef}
        className="p-3 border-t border-gray-700 bg-gray-800 relative"
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {/* Drag and Drop Overlay */}
        {isDraggingOver && (
          <div className="absolute inset-0 bg-blue-600/20 backdrop-blur-sm z-10 flex items-center justify-center border-2 border-dashed border-blue-400 rounded-lg m-2">
            <div className="text-center">
              <Upload size={32} className="text-blue-400 mx-auto mb-2 animate-bounce" />
              <p className="text-blue-300 font-medium">拖放文件到这里上传</p>
              <p className="text-blue-400/70 text-xs mt-1">最大 10MB</p>
            </div>
          </div>
        )}
        {/* Reply Preview */}
        {replyingTo && (
          <div className="mb-2 flex items-center gap-2 bg-purple-900/30 border border-purple-500/50 rounded px-3 py-2">
            <CornerDownRight size={14} className="text-purple-400" />
            <div className="flex-1 min-w-0">
              <span className="text-xs text-purple-300 font-medium">{replyingTo.sender_name}</span>
              <span className="text-xs text-gray-400 truncate block">{replyingTo.content.substring(0, 80)}...</span>
            </div>
            <button
              onClick={cancelReply}
              className="text-gray-400 hover:text-white"
            >
              <X size={14} />
            </button>
          </div>
        )}
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
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleMessageChange}
              onKeyDown={handleKeyDown}
              placeholder="输入消息... (Enter 发送, @ 提及成员)"
              className="w-full px-3 py-2 bg-gray-700 rounded-lg text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none overflow-y-auto"
              style={{ minHeight: '40px', maxHeight: '200px' }}
              disabled={sending}
            />
            {/* Mention Picker */}
            {showMentionPicker && mentionableAgents.length > 0 && (
              <div
                ref={mentionPickerRef}
                className="absolute bottom-full left-0 mb-1 w-48 bg-gray-800 border border-gray-600 rounded-lg shadow-xl overflow-hidden z-10"
              >
                <div className="px-2 py-1 border-b border-gray-700 flex items-center gap-1 text-xs text-gray-400">
                  <AtSign size={12} />
                  <span>提及成员</span>
                </div>
                <div className="max-h-40 overflow-y-auto">
                  {mentionableAgents.map(agent => (
                    <button
                      key={agent.id}
                      onClick={() => insertMention(agent.id, agent.name)}
                      className="w-full text-left px-2 py-1.5 hover:bg-gray-700 transition-colors flex items-center gap-2"
                    >
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs"
                        style={{ backgroundColor: getAgentColor(agent.type) }}
                      >
                        {agent.name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-white truncate">{agent.name}</div>
                        <div className="text-xs text-gray-400">{agent.type}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          <button
            onClick={handleSendMessage}
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
          <div className="bg-gray-800 rounded-lg p-6 w-[400px] shadow-2xl max-h-[80vh] overflow-y-auto">
            <h3 className="text-white text-lg font-bold mb-4">邀请成员</h3>
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-xs block mb-2">选择要邀请的 Agent</label>
                <div className="max-h-60 overflow-y-auto space-y-1 bg-gray-700/50 rounded p-2">
                  {agents.filter(a => !currentChat?.members.some(m => m.id === a.id)).length === 0 ? (
                    <p className="text-gray-400 text-sm text-center py-4">所有 Agent 都已在群聊中</p>
                  ) : (
                    agents
                      .filter(a => !currentChat?.members.some(m => m.id === a.id))
                      .map((agent) => (
                        <label
                          key={agent.id}
                          className="flex items-center gap-2 cursor-pointer hover:bg-gray-600/50 p-2 rounded transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={addMemberAgentIds.includes(agent.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setAddMemberAgentIds([...addMemberAgentIds, agent.id]);
                              } else {
                                setAddMemberAgentIds(addMemberAgentIds.filter(id => id !== agent.id));
                              }
                            }}
                            className="rounded bg-gray-600 border-gray-500 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-800"
                          />
                          <div
                            className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs flex-shrink-0"
                            style={{ backgroundColor: getAgentColor(agent.type) }}
                          >
                            {(agent.name || '?').charAt(0)}
                          </div>
                          <span className="text-white text-sm truncate">{agent.name}</span>
                          <span className="text-gray-400 text-xs">({agent.type})</span>
                        </label>
                      ))
                  )}
                </div>
                {addMemberAgentIds.length > 0 && (
                  <p className="text-blue-400 text-xs mt-1">已选择 {addMemberAgentIds.length} 个 Agent</p>
                )}
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

      {/* Message Search */}
      <MessageSearch
        isOpen={showSearch}
        onClose={() => setShowSearch(false)}
        messages={currentChat.messages.map(msg => ({
          id: msg.id,
          content: msg.content,
          sender_name: msg.sender_name,
          sender_type: msg.sender_type,
          timestamp: msg.timestamp,
        }))}
        onJumpToMessage={scrollToMessage}
        placeholder="搜索群聊消息..."
      />

      {/* Bookmarks Panel */}
      {showBookmarks && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-30">
          <div className="bg-gray-800 rounded-lg w-[500px] max-h-[80vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bookmark size={18} className="text-yellow-500" />
                <h3 className="text-white text-lg font-bold">收藏的消息</h3>
                <span className="text-gray-400 text-sm">({filteredBookmarks.length})</span>
              </div>
              <button
                onClick={() => {
                  setShowBookmarks(false);
                  setBookmarkSearchQuery('');
                }}
                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Search */}
            <div className="p-3 border-b border-gray-700">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={bookmarkSearchQuery}
                  onChange={(e) => setBookmarkSearchQuery(e.target.value)}
                  placeholder="搜索收藏..."
                  className="w-full pl-9 pr-3 py-2 bg-gray-700 text-white text-sm rounded-lg border border-gray-600 focus:border-yellow-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Bookmarks List */}
            <div className="flex-1 overflow-y-auto">
              {filteredBookmarks.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-gray-400">
                  <Bookmark size={32} className="mb-2 opacity-50" />
                  <p className="text-sm">
                    {bookmarkSearchQuery ? '没有匹配的收藏' : '暂无收藏的消息'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {bookmarkSearchQuery ? '尝试其他关键词' : '悬停消息点击星标即可收藏'}
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-700/50">
                  {filteredBookmarks.map((msg) => {
                    const member = currentChat.members.find((m) => m.id === msg.sender_id);
                    return (
                      <div
                        key={msg.id}
                        className="p-3 hover:bg-gray-700/50 cursor-pointer transition-colors"
                        onClick={() => {
                          scrollToMessage(msg.id);
                          setShowBookmarks(false);
                          setBookmarkSearchQuery('');
                        }}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                            style={{
                              backgroundColor: msg.sender_type === 'user'
                                ? getUserAvatarColor(msg.sender_name)
                                : member?.avatar_color || '#6B7280',
                            }}
                          >
                            {msg.sender_name.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-white text-sm font-medium">{msg.sender_name}</span>
                              <span className="text-gray-500 text-xs">{formatTime(msg.timestamp)}</span>
                            </div>
                            <p className="text-gray-300 text-sm line-clamp-3">{msg.content}</p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleBookmark(msg.id);
                            }}
                            className="p-1.5 hover:bg-gray-600 rounded text-yellow-500 hover:text-yellow-400 transition-colors"
                            title="取消收藏"
                          >
                            <Star size={14} fill="currentColor" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Forward Modal */}
      {showForwardModal && forwardingMessage && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-30">
          <div className="bg-gray-800 rounded-lg w-[400px] max-h-[80vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Forward size={18} className="text-green-400" />
                <h3 className="text-white text-lg font-bold">转发消息</h3>
              </div>
              <button
                onClick={handleCloseForwardModal}
                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Message Preview */}
            <div className="p-3 border-b border-gray-700 bg-gray-700/30">
              <div className="text-xs text-gray-400 mb-1">
                转发自 <span className="text-white font-medium">{forwardingMessage.sender_name}</span>
              </div>
              <p className="text-gray-300 text-sm line-clamp-3">{forwardingMessage.content}</p>
            </div>

            {/* Target Selection */}
            <div className="p-3 border-b border-gray-700">
              <div className="text-xs text-gray-400 mb-2">选择转发目标：</div>
              <div className="flex-1 overflow-y-auto max-h-[40vh]">
                {groupChats.length === 0 ? (
                  <div className="text-center text-gray-500 text-sm py-4">暂无群聊可转发</div>
                ) : (
                  <div className="space-y-1">
                    {groupChats.filter(chat => chat.id !== currentGroupChatId).map((chat) => (
                      <button
                        key={chat.id}
                        onClick={() => handleToggleForwardTarget(chat.id)}
                        className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                          forwardTargetIds.includes(chat.id)
                            ? 'bg-green-600/30 border border-green-500/50'
                            : 'hover:bg-gray-700'
                        }`}
                      >
                        <div className={`w-4 h-4 rounded border flex items-center justify-center ${
                          forwardTargetIds.includes(chat.id)
                            ? 'bg-green-500 border-green-500'
                            : 'border-gray-500'
                        }`}>
                          {forwardTargetIds.includes(chat.id) && (
                            <Check size={12} className="text-white" />
                          )}
                        </div>
                        <Users size={14} className="text-gray-400" />
                        <span className="text-white text-sm">{chat.name}</span>
                        <span className="text-gray-500 text-xs ml-auto">
                          {chat.members.length} 成员
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="p-3 flex gap-2 justify-end">
              <button
                onClick={handleCloseForwardModal}
                className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleConfirmForward}
                disabled={forwardTargetIds.length === 0}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              >
                <Send size={14} />
                转发 {forwardTargetIds.length > 0 && `(${forwardTargetIds.length})`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
