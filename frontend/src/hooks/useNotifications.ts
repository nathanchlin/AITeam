import { useState, useEffect, useCallback } from 'react';

export interface NotificationOptions {
  title: string;
  body: string;
  icon?: string;
  tag?: string;
  onClick?: () => void;
}

export function useNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [enabled, setEnabled] = useState(() => {
    const saved = localStorage.getItem('notificationsEnabled');
    return saved ? saved === 'true' : false;
  });

  // Check permission on mount
  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
    }
  }, []);

  // Persist enabled state
  useEffect(() => {
    localStorage.setItem('notificationsEnabled', String(enabled));
  }, [enabled]);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      console.warn('This browser does not support desktop notification');
      return false;
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result === 'granted';
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      return false;
    }
  }, []);

  // Send a notification
  const sendNotification = useCallback((options: NotificationOptions) => {
    if (!enabled || permission !== 'granted') {
      return null;
    }

    try {
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon || '/favicon.ico',
        tag: options.tag,
        requireInteraction: false,
      });

      if (options.onClick) {
        notification.onclick = () => {
          options.onClick?.();
          notification.close();
          // Focus the window
          window.focus();
        };
      }

      // Auto close after 5 seconds
      setTimeout(() => notification.close(), 5000);

      return notification;
    } catch (error) {
      console.error('Failed to send notification:', error);
      return null;
    }
  }, [enabled, permission]);

  // Toggle notifications
  const toggleNotifications = useCallback(async () => {
    if (!enabled && permission !== 'granted') {
      const granted = await requestPermission();
      if (granted) {
        setEnabled(true);
      }
    } else {
      setEnabled(!enabled);
    }
  }, [enabled, permission, requestPermission]);

  // Notify task completion
  const notifyTaskComplete = useCallback((agentName: string, taskTitle: string, onClick?: () => void) => {
    return sendNotification({
      title: `Task Completed by ${agentName}`,
      body: taskTitle.length > 100 ? taskTitle.slice(0, 100) + '...' : taskTitle,
      tag: 'task-complete',
      onClick,
    });
  }, [sendNotification]);

  // Notify agent error
  const notifyAgentError = useCallback((agentName: string, errorMessage: string, onClick?: () => void) => {
    return sendNotification({
      title: `Error from ${agentName}`,
      body: errorMessage,
      tag: 'agent-error',
      onClick,
    });
  }, [sendNotification]);

  // Notify pipeline complete
  const notifyPipelineComplete = useCallback((planTitle: string, onClick?: () => void) => {
    return sendNotification({
      title: 'Pipeline Completed',
      body: planTitle,
      tag: 'pipeline-complete',
      onClick,
    });
  }, [sendNotification]);

  return {
    permission,
    enabled,
    toggleNotifications,
    requestPermission,
    sendNotification,
    notifyTaskComplete,
    notifyAgentError,
    notifyPipelineComplete,
    isSupported: 'Notification' in window,
  };
}
