import { useState, useEffect, useMemo } from 'react';
import { Bell, X, CheckCircle, Clock, AlertTriangle, MessageCircle, AtSign, Check, Trash2 } from 'lucide-react';
import type { Task } from '../../types';

export interface Notification {
  id: string;
  type: 'due_soon' | 'overdue' | 'status_change' | 'mention' | 'assignment';
  title: string;
  message: string;
  taskId?: string;
  taskTitle?: string;
  timestamp: string;
  read: boolean;
}

interface NotificationPanelProps {
  tasks: Task[];
  onTaskClick?: (taskId: string) => void;
}

const STORAGE_KEY = 'notification_history';
const MAX_NOTIFICATIONS = 50;

export function NotificationPanel({ tasks, onTaskClick }: NotificationPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Save notifications to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notifications.slice(0, MAX_NOTIFICATIONS)));
  }, [notifications]);

  // Generate notifications from tasks
  const generatedNotifications = useMemo(() => {
    const newNotifications: Notification[] = [];
    const now = new Date();

    tasks.forEach(task => {
      if (task.archived || task.status === 'completed') return;

      // Due soon notification (within 24 hours)
      if (task.due_date) {
        const dueDate = new Date(task.due_date);
        const hoursUntilDue = (dueDate.getTime() - now.getTime()) / (1000 * 60 * 60);

        if (hoursUntilDue < 0) {
          // Overdue
          newNotifications.push({
            id: `overdue-${task.id}`,
            type: 'overdue',
            title: 'Task Overdue',
            message: `"${task.title}" is overdue`,
            taskId: task.id,
            taskTitle: task.title,
            timestamp: dueDate.toISOString(),
            read: false
          });
        } else if (hoursUntilDue < 1) {
          // Due within 1 hour
          newNotifications.push({
            id: `due-1h-${task.id}`,
            type: 'due_soon',
            title: 'Due Very Soon',
            message: `"${task.title}" is due within 1 hour`,
            taskId: task.id,
            taskTitle: task.title,
            timestamp: now.toISOString(),
            read: false
          });
        } else if (hoursUntilDue < 24) {
          // Due within 24 hours
          newNotifications.push({
            id: `due-24h-${task.id}`,
            type: 'due_soon',
            title: 'Due Soon',
            message: `"${task.title}" is due within 24 hours`,
            taskId: task.id,
            taskTitle: task.title,
            timestamp: now.toISOString(),
            read: false
          });
        }
      }
    });

    return newNotifications;
  }, [tasks]);

  // Merge generated notifications with stored ones
  useEffect(() => {
    setNotifications(prev => {
      const existingIds = new Set(prev.map(n => n.id));
      const newToAdd = generatedNotifications.filter(n => !existingIds.has(n.id));
      if (newToAdd.length === 0) return prev;
      return [...newToAdd, ...prev].slice(0, MAX_NOTIFICATIONS);
    });
  }, [generatedNotifications]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const clearNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const handleNotificationClick = (notification: Notification) => {
    markAsRead(notification.id);
    if (notification.taskId && onTaskClick) {
      onTaskClick(notification.taskId);
      setIsOpen(false);
    }
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'due_soon':
        return <Clock size={14} className="text-yellow-400" />;
      case 'overdue':
        return <AlertTriangle size={14} className="text-red-400" />;
      case 'status_change':
        return <CheckCircle size={14} className="text-green-400" />;
      case 'mention':
        return <AtSign size={14} className="text-blue-400" />;
      case 'assignment':
        return <MessageCircle size={14} className="text-purple-400" />;
      default:
        return <Bell size={14} className="text-gray-400" />;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
        title="Notifications"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Panel */}
          <div className="absolute right-0 top-full mt-2 w-80 bg-gray-800 rounded-lg shadow-xl border border-gray-700 z-50 max-h-[400px] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-gray-700">
              <h3 className="text-white text-sm font-medium flex items-center gap-2">
                <Bell size={14} />
                Notifications
                {unreadCount > 0 && (
                  <span className="text-xs bg-red-500 text-white px-1.5 py-0.5 rounded-full">
                    {unreadCount} new
                  </span>
                )}
              </h3>
              <div className="flex items-center gap-1">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                    title="Mark all as read"
                  >
                    <Check size={14} />
                  </button>
                )}
                {notifications.length > 0 && (
                  <button
                    onClick={clearAllNotifications}
                    className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-red-400"
                    title="Clear all"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Notification List */}
            <div className="flex-1 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                  <Bell size={32} className="mb-2 opacity-50" />
                  <p className="text-sm">No notifications</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-700">
                  {notifications.map(notification => (
                    <div
                      key={notification.id}
                      onClick={() => handleNotificationClick(notification)}
                      className={`p-3 cursor-pointer transition-colors hover:bg-gray-700/50 ${
                        !notification.read ? 'bg-blue-500/5' : ''
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        <div className="mt-0.5">
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className={`text-xs font-medium ${
                              !notification.read ? 'text-white' : 'text-gray-300'
                            }`}>
                              {notification.title}
                            </span>
                            <span className="text-[10px] text-gray-500">
                              {formatTime(notification.timestamp)}
                            </span>
                          </div>
                          <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">
                            {notification.message}
                          </p>
                          {notification.taskTitle && (
                            <div className="mt-1 flex items-center gap-1">
                              {!notification.read && (
                                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                              )}
                              <span className="text-[10px] text-gray-500 truncate">
                                Task: {notification.taskTitle}
                              </span>
                            </div>
                          )}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            clearNotification(notification.id);
                          }}
                          className="p-1 hover:bg-gray-600 rounded text-gray-500 hover:text-gray-300"
                        >
                          <X size={12} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="p-2 border-t border-gray-700 text-center">
                <span className="text-[10px] text-gray-500">
                  {notifications.length} notification{notifications.length !== 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
