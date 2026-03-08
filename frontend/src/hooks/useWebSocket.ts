import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '../stores/agentStore';

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
  const { setWsConnected, handleWebSocketMessage, currentPlanId, updatePlan } = useAgentStore();

  // Sync current plan state from server (called on WebSocket reconnect)
  const syncCurrentPlan = useCallback(async () => {
    if (!currentPlanId) return;

    try {
      const res = await fetch(`${API_BASE}/api/pipeline/plans/${currentPlanId}`);
      if (res.ok) {
        const plan = await res.json();
        console.log('[WS] Synced plan state:', plan.status);
        updatePlan(currentPlanId, plan);
      }
    } catch (e) {
      console.error('[WS] Failed to sync plan state:', e);
    }
  }, [currentPlanId, updatePlan]);

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
      // Sync current plan state on reconnect
      syncCurrentPlan();
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);

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
  }, [setWsConnected, handleWebSocketMessage, syncCurrentPlan]);

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
