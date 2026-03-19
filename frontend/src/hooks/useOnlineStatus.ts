import { useState, useEffect, useCallback } from 'react';

interface UseOnlineStatusOptions {
  onOnline?: () => void;
  onOffline?: () => void;
  showConsoleLog?: boolean;
}

/**
 * Hook to track online/offline status.
 * Useful for warning users when they lose connection.
 */
export function useOnlineStatus(options: UseOnlineStatusOptions = {}) {
  const { onOnline, onOffline, showConsoleLog = true } = options;
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastOnlineTime, setLastOnlineTime] = useState<Date | null>(
    navigator.onLine ? new Date() : null
  );
  const [lastOfflineTime, setLastOfflineTime] = useState<Date | null>(
    navigator.onLine ? null : new Date()
  );

  const handleOnline = useCallback(() => {
    if (showConsoleLog) {
      console.log('[Network] Back online');
    }
    setIsOnline(true);
    setLastOnlineTime(new Date());
    onOnline?.();
  }, [showConsoleLog, onOnline]);

  const handleOffline = useCallback(() => {
    if (showConsoleLog) {
      console.warn('[Network] Gone offline');
    }
    setIsOnline(false);
    setLastOfflineTime(new Date());
    onOffline?.();
  }, [showConsoleLog, onOffline]);

  useEffect(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [handleOnline, handleOffline]);

  // Calculate offline duration
  const getOfflineDuration = useCallback((): number | null => {
    if (isOnline || !lastOfflineTime) return null;
    return Math.floor((Date.now() - lastOfflineTime.getTime()) / 1000);
  }, [isOnline, lastOfflineTime]);

  return {
    isOnline,
    isOffline: !isOnline,
    lastOnlineTime,
    lastOfflineTime,
    getOfflineDuration,
  };
}

/**
 * Format offline duration for display
 */
export function formatOfflineDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`;
  if (seconds < 3600) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}分${secs}秒`;
  }
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hours}小时${mins}分`;
}
