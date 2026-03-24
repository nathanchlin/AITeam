import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '../stores/agentStore';
import { useToast } from '../components/common/Toast';

// Production: use VITE_API_BASE_URL env var
// Development: use empty string to let Vite proxy handle requests
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

// WebSocket URL:
// - Production: derive from API_BASE
// - Development: use relative path '/ws', Vite will proxy to backend
const WS_URL = API_BASE
  ? `${API_BASE.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')}/ws`
  : `ws://${window.location.host}/ws`;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const wasConnectedRef = useRef(false); // Track if we were ever connected (for toast)
  const { setWsConnected, handleWebSocketMessage, updatePlan, currentPlanId } = useAgentStore();
  const toast = useToast();

  // Use refs to avoid triggering reconnect when these values change
  const currentPlanIdRef = useRef<string | null>(null);
  const toastRef = useRef(toast);

  // Keep refs in sync with store/context
  useEffect(() => {
    currentPlanIdRef.current = currentPlanId;
  }, [currentPlanId]);

  useEffect(() => {
    toastRef.current = toast;
  }, [toast]);

  // Store syncCurrentPlan in ref to ensure stable reference for connect
  const syncCurrentPlanRef = useRef<() => Promise<void>>(async () => {});

  // Update the sync function when dependencies change
  useEffect(() => {
    syncCurrentPlanRef.current = async () => {
      const planId = currentPlanIdRef.current;
      if (!planId) return;

      try {
        const res = await fetch(`${API_BASE}/api/pipeline/plans/${planId}`);
        if (res.ok) {
          const plan = await res.json();
          console.log('[WS] Synced plan state:', plan.status);
          updatePlan(planId, plan);
        }
      } catch (e) {
        console.error('[WS] Failed to sync plan state:', e);
      }
    };
  }, [updatePlan]);

  // Stable connect function with minimal dependencies
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[WS] Already connected, skipping');
      return;
    }

    console.log('[WS] Connecting to:', WS_URL);
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log('[WS] Connected successfully');
      setWsConnected(true);

      // Show reconnection toast if this is a reconnect
      if (wasConnectedRef.current) {
        toastRef.current?.success('WebSocket reconnected');
      }
      wasConnectedRef.current = true;

      // Sync current plan state on reconnect
      syncCurrentPlanRef.current();
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);

      // Show disconnection toast (only if we were previously connected)
      if (wasConnectedRef.current) {
        toastRef.current?.warning('WebSocket disconnected, reconnecting...');
      }

      // Attempt to reconnect after 3 seconds
      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    wsRef.current = ws;
  }, [setWsConnected, handleWebSocketMessage]); // Minimal stable dependencies

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { send, disconnect, reconnect: connect };
}
