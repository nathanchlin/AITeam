import { useState, useEffect, useRef, useCallback } from 'react';

interface PerformanceStats {
  fps: number;
  memoryMB: number;
  renderCount: number;
  wsMessageRate: number; // messages per second
  latency: number | null;
}

interface PerformanceMonitorOptions {
  sampleInterval?: number; // ms, default 1000
  onWarning?: (metric: string, value: number) => void;
}

// Global message counter for WebSocket tracking
let wsMessageCount = 0;
let lastWsCountTime = Date.now();

export function trackWsMessage() {
  wsMessageCount++;
}

/**
 * Performance monitoring hook for debugging and diagnostics.
 * Tracks FPS, memory usage, render count, and WebSocket message rate.
 */
export function usePerformanceMonitor(options: PerformanceMonitorOptions = {}) {
  const { sampleInterval = 1000, onWarning } = options;

  const [stats, setStats] = useState<PerformanceStats>({
    fps: 60,
    memoryMB: 0,
    renderCount: 0,
    wsMessageRate: 0,
    latency: null,
  });

  const renderCountRef = useRef(0);
  const frameCountRef = useRef(0);
  const lastFrameTimeRef = useRef(performance.now());
  const rafIdRef = useRef<number | null>(null);

  // Increment render count (call in component body)
  const incrementRender = useCallback(() => {
    renderCountRef.current++;
  }, []);

  // Measure FPS using requestAnimationFrame
  useEffect(() => {
    const measureFrame = () => {
      frameCountRef.current++;
      rafIdRef.current = requestAnimationFrame(measureFrame);
    };
    rafIdRef.current = requestAnimationFrame(measureFrame);

    return () => {
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
      }
    };
  }, []);

  // Sample stats at interval
  useEffect(() => {
    const timer = setInterval(() => {
      const now = performance.now();

      // Calculate FPS
      const elapsed = now - lastFrameTimeRef.current;
      const fps = Math.round((frameCountRef.current / elapsed) * 1000);
      frameCountRef.current = 0;
      lastFrameTimeRef.current = now;

      // Get memory (if available - Chrome only)
      const memory = (performance as unknown as { memory?: { usedJSHeapSize: number } }).memory;
      const memoryMB = memory ? Math.round(memory.usedJSHeapSize / (1024 * 1024)) : 0;

      // Calculate WebSocket message rate
      const wsElapsed = (Date.now() - lastWsCountTime) / 1000;
      const wsRate = wsElapsed > 0 ? Math.round(wsMessageCount / wsElapsed) : 0;
      wsMessageCount = 0;
      lastWsCountTime = Date.now();

      const newStats: PerformanceStats = {
        fps,
        memoryMB,
        renderCount: renderCountRef.current,
        wsMessageRate: wsRate,
        latency: null, // Will be set by external latency measurement
      };

      // Trigger warnings for abnormal values
      if (fps < 30 && onWarning) {
        onWarning('fps', fps);
      }
      if (memoryMB > 500 && onWarning) {
        onWarning('memory', memoryMB);
      }

      setStats(newStats);
    }, sampleInterval);

    return () => clearInterval(timer);
  }, [sampleInterval, onWarning]);

  // Update latency from external source
  const updateLatency = useCallback((latency: number | null) => {
    setStats(prev => ({ ...prev, latency }));
  }, []);

  return {
    stats,
    incrementRender,
    updateLatency,
    trackWsMessage,
  };
}

/**
 * Simple component render tracker.
 * Wrap components with this to count renders.
 */
export function useRenderCount(componentName: string) {
  const countRef = useRef(0);
  countRef.current++;

  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log(`[${componentName}] Render #${countRef.current}`);
    }
  });
}
