import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '../stores/agentStore';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Hook to automatically refresh data when the window regains focus
 * or periodically in the background.
 */
export function useAutoRefresh(options: {
  enabled?: boolean;
  intervalMs?: number; // Background refresh interval (0 = disabled)
  onFocusRefresh?: boolean; // Refresh when window gains focus
}) {
  const { enabled = true, intervalMs = 0, onFocusRefresh = true } = options;
  const lastRefreshRef = useRef<number>(Date.now());
  const { setAgents, setTasks, setPlans } = useAgentStore();

  const refreshData = useCallback(async () => {
    if (!enabled) return;

    // Throttle: don't refresh more than once per 2 seconds
    const now = Date.now();
    if (now - lastRefreshRef.current < 2000) return;
    lastRefreshRef.current = now;

    try {
      const [agentsRes, tasksRes, plansRes] = await Promise.all([
        fetch(`${API_BASE}/api/agents`),
        fetch(`${API_BASE}/api/tasks`),
        fetch(`${API_BASE}/api/pipeline/plans`),
      ]);

      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (tasksRes.ok) setTasks(await tasksRes.json());
      if (plansRes.ok) setPlans(await plansRes.json());

      console.log('[AutoRefresh] Data refreshed');
    } catch (e) {
      console.warn('[AutoRefresh] Failed to refresh:', e);
    }
  }, [enabled, setAgents, setTasks, setPlans]);

  // Refresh when window gains focus
  useEffect(() => {
    if (!enabled || !onFocusRefresh) return;

    const handleFocus = () => {
      console.log('[AutoRefresh] Window focused, refreshing data...');
      refreshData();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [enabled, onFocusRefresh, refreshData]);

  // Periodic background refresh
  useEffect(() => {
    if (!enabled || intervalMs <= 0) return;

    const timer = setInterval(() => {
      refreshData();
    }, intervalMs);

    return () => clearInterval(timer);
  }, [enabled, intervalMs, refreshData]);

  return { refreshData };
}
