import { useState, useEffect, useMemo, useCallback } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { useTheme } from '../../hooks/useTheme';
import { useNotifications } from '../../hooks/useNotifications';
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';
import { useSoundNotifications } from '../../hooks/useSoundNotifications';
import { useOnlineStatus, formatOfflineDuration } from '../../hooks/useOnlineStatus';
import { DevToolsPanel } from '../UI/DevToolsPanel';
import { useToast, type ToastHistoryItem } from './Toast';
import { Wifi, WifiOff, Users, CheckCircle, Clock, Loader2, Zap, Sun, Moon, Bell, BellOff, Activity, ChevronUp, RefreshCw, Gauge, Database, Volume2, VolumeX, History, X, AlertTriangle } from 'lucide-react';

export function StatusBar() {
  const { agents, tasks, wsConnected, toggleTaskPanel } = useAgentStore();
  const { theme, toggleTheme } = useTheme();
  const { enabled: notificationsEnabled, toggleNotifications } = useNotifications();
  const { enabled: soundEnabled, toggleEnabled: toggleSound, setVolume: setSoundVolume, getVolume: getSoundVolume, playSound } = useSoundNotifications();
  const [soundVolume, setSoundVolumeState] = useState(getSoundVolume());
  const { isOffline, getOfflineDuration } = useOnlineStatus({ showConsoleLog: true });
  const { history: toastHistory, clearHistory } = useToast();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [showDevTools, setShowDevTools] = useState(false);
  const [showToastHistory, setShowToastHistory] = useState(false);
  const [offlineTimer, setOfflineTimer] = useState(0);

  // Simulate system performance (mock data)
  const [systemPerf, setSystemPerf] = useState({ cpu: 23, memory: 45 });

  // Network latency measurement
  const [latency, setLatency] = useState<number | null>(null);

  // Performance monitoring (dev mode only)
  const isDev = import.meta.env.DEV;
  const handlePerfWarning = useCallback((metric: string, value: number) => {
    if (isDev) {
      console.warn(`[Perf] ${metric} warning:`, value);
    }
  }, [isDev]);
  const { stats: perfStats, updateLatency: updatePerfLatency } = usePerformanceMonitor({
    sampleInterval: 2000,
    onWarning: handlePerfWarning,
  });

  const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

  // Measure network latency every 5 seconds
  useEffect(() => {
    const measureLatency = async () => {
      if (!wsConnected) {
        setLatency(null);
        updatePerfLatency(null);
        return;
      }
      try {
        const start = performance.now();
        await fetch(`${API_BASE}/api/health`, { method: 'HEAD' });
        const end = performance.now();
        const measured = Math.round(end - start);
        setLatency(measured);
        updatePerfLatency(measured);
      } catch {
        setLatency(null);
        updatePerfLatency(null);
      }
    };

    measureLatency();
    const timer = setInterval(measureLatency, 5000);
    return () => clearInterval(timer);
  }, [wsConnected, API_BASE, updatePerfLatency]);

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      // Simulate fluctuating system performance
      setSystemPerf(prev => ({
        cpu: Math.min(100, Math.max(5, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.min(100, Math.max(20, prev.memory + (Math.random() - 0.5) * 5)),
      }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Calculate statistics
  const stats = useMemo(() => {
    const activeAgents = agents.filter(a => a.status === 'working').length;
    const errorAgents = agents.filter(a => a.status === 'error').length;
    const runningTasks = tasks.filter(t => t.status === 'running').length;
    const pendingTasks = tasks.filter(t => t.status === 'pending').length;
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const totalTasks = tasks.length;
    const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    return {
      agentCount: agents.length,
      activeAgents,
      errorAgents,
      runningTasks,
      pendingTasks,
      completedTasks,
      totalTasks,
      progress,
    };
  }, [agents, tasks]);

  // Version info
  const version = 'v1.5.0';

  // Session duration timer
  const [sessionStart] = useState(Date.now());
  const [sessionDuration, setSessionDuration] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSessionDuration(Math.floor((Date.now() - sessionStart) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [sessionStart]);

  // Offline duration timer
  useEffect(() => {
    if (!isOffline) {
      setOfflineTimer(0);
      return;
    }
    const timer = setInterval(() => {
      const duration = getOfflineDuration();
      if (duration !== null) setOfflineTimer(duration);
    }, 1000);
    return () => clearInterval(timer);
  }, [isOffline, getOfflineDuration]);

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 h-6 bg-gray-900/95 border-t border-gray-700 flex items-center px-3 text-xs z-30">
      {/* Left section - Connection & Agents */}
      <div className="flex items-center gap-4">
        {/* Browser Offline Warning */}
        {isOffline && (
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-red-900/50 rounded text-red-300 animate-pulse">
            <WifiOff size={12} />
            <span>Offline</span>
            {offlineTimer > 0 && (
              <span className="text-red-400 text-[10px]">({formatOfflineDuration(offlineTimer)})</span>
            )}
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-1.5">
          {wsConnected ? (
            <>
              <Wifi size={12} className="text-green-400" />
              <span className="text-green-400">Connected</span>
              {/* Signal strength indicator */}
              {latency !== null && (
                <div className="flex items-center gap-0.5 ml-1">
                  <div className={`w-0.5 h-1 rounded-sm ${latency < 300 ? 'bg-green-400' : 'bg-gray-600'}`} />
                  <div className={`w-0.5 h-2 rounded-sm ${latency < 200 ? 'bg-green-400' : 'bg-gray-600'}`} />
                  <div className={`w-0.5 h-2.5 rounded-sm ${latency < 100 ? 'bg-green-400' : latency < 200 ? 'bg-yellow-400' : 'bg-gray-600'}`} />
                  <div className={`w-0.5 h-3 rounded-sm ${latency < 50 ? 'bg-green-400' : latency < 100 ? 'bg-yellow-400' : 'bg-gray-600'}`} />
                </div>
              )}
              {latency !== null && (
                <span className={`ml-0.5 ${
                  latency < 100 ? 'text-green-400' :
                  latency < 300 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {latency}ms
                </span>
              )}
            </>
          ) : (
            <>
              <WifiOff size={12} className="text-red-400 animate-pulse" />
              <span className="text-red-400">Disconnected</span>
              <button
                onClick={() => window.location.reload()}
                className="ml-1.5 p-0.5 hover:bg-gray-700 rounded transition-colors text-red-400 hover:text-white"
                title="Reconnect (reload page)"
              >
                <RefreshCw size={10} />
              </button>
            </>
          )}
        </div>

        {/* Separator */}
        <div className="w-px h-3 bg-gray-700" />

        {/* Agent Stats */}
        <div className="flex items-center gap-1.5 text-gray-400">
          <Users size={12} />
          <span>{stats.agentCount} Agents</span>
          {stats.activeAgents > 0 && (
            <span className="text-green-400 ml-1">
              ({stats.activeAgents} active)
            </span>
          )}
          {stats.errorAgents > 0 && (
            <span className="text-red-400 ml-1">
              ({stats.errorAgents} error)
            </span>
          )}
        </div>

        {/* Separator */}
        <div className="w-px h-3 bg-gray-700" />

        {/* System Performance */}
        <div className="flex items-center gap-2 text-gray-400">
          <Activity size={12} />
          <div className="flex items-center gap-1">
            <span className={systemPerf.cpu > 80 ? 'text-red-400' : systemPerf.cpu > 50 ? 'text-yellow-400' : 'text-green-400'}>
              CPU {Math.round(systemPerf.cpu)}%
            </span>
            <span className="text-gray-600">|</span>
            <span className={systemPerf.memory > 80 ? 'text-red-400' : systemPerf.memory > 60 ? 'text-yellow-400' : 'text-blue-400'}>
              RAM {Math.round(systemPerf.memory)}%
            </span>
          </div>
        </div>

        {/* Dev Mode Performance Stats */}
        {isDev && (
          <div className="flex items-center gap-2 text-gray-400">
            <Gauge size={12} className="text-purple-400" />
            <span className={`text-[10px] ${perfStats.fps < 30 ? 'text-red-400' : perfStats.fps < 50 ? 'text-yellow-400' : 'text-green-400'}`}>
              {perfStats.fps} FPS
            </span>
            {perfStats.memoryMB > 0 && (
              <span className={`text-[10px] ${perfStats.memoryMB > 500 ? 'text-red-400' : perfStats.memoryMB > 300 ? 'text-yellow-400' : 'text-gray-400'}`}>
                {perfStats.memoryMB}MB
              </span>
            )}
          </div>
        )}
      </div>

      {/* Center section - Task Stats (clickable to open TaskPanel) */}
      <div
        className="flex-1 flex items-center justify-center gap-4 cursor-pointer hover:opacity-80 transition-opacity"
        onClick={toggleTaskPanel}
        title="Click to toggle Task Panel"
      >
        {/* Overall Progress */}
        {stats.totalTasks > 0 && (
          <div className="flex items-center gap-1.5">
            <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-green-400 transition-all duration-500"
                style={{ width: `${stats.progress}%` }}
              />
            </div>
            <span className="text-gray-300">{stats.progress}%</span>
          </div>
        )}

        {/* Running Tasks */}
        {stats.runningTasks > 0 && (
          <div className="flex items-center gap-1 text-green-400">
            <Loader2 size={12} className="animate-spin" />
            <span>{stats.runningTasks} Running</span>
          </div>
        )}

        {/* Pending Tasks */}
        {stats.pendingTasks > 0 && (
          <div className="flex items-center gap-1 text-yellow-400">
            <Clock size={12} />
            <span>{stats.pendingTasks} Pending</span>
          </div>
        )}

        {/* Completed Tasks */}
        {stats.completedTasks > 0 && (
          <div className="flex items-center gap-1 text-blue-400">
            <CheckCircle size={12} />
            <span>{stats.completedTasks} Completed</span>
          </div>
        )}

        {/* No tasks indicator */}
        {stats.runningTasks === 0 && stats.pendingTasks === 0 && stats.completedTasks === 0 && (
          <div className="flex items-center gap-1 text-gray-500">
            <Zap size={12} />
            <span>No tasks</span>
          </div>
        )}
      </div>

      {/* Right section - Quick Actions, Time & Version */}
      <div className="flex items-center gap-2">
        {/* Quick Actions Toggle */}
        <div className="relative">
          <button
            onClick={(e) => { e.stopPropagation(); setShowQuickActions(!showQuickActions); }}
            className={`flex items-center gap-1 px-1.5 py-0.5 rounded transition-colors ${
              showQuickActions ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            <ChevronUp size={12} className={`transition-transform ${showQuickActions ? 'rotate-180' : ''}`} />
          </button>

          {/* Quick Actions Popup */}
          {showQuickActions && (
            <div className="absolute bottom-5 right-0 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-1 flex gap-1 z-50">
              <button
                onClick={(e) => { e.stopPropagation(); toggleTheme(); }}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors text-gray-300 hover:text-white"
                title={theme === 'dark' ? 'Switch to light' : 'Switch to dark'}
              >
                {theme === 'dark' ? <Sun size={12} /> : <Moon size={12} />}
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); toggleNotifications(); }}
                className={`p-1.5 rounded transition-colors ${
                  notificationsEnabled ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                title={notificationsEnabled ? 'Disable notifications' : 'Enable notifications'}
              >
                {notificationsEnabled ? <Bell size={12} /> : <BellOff size={12} />}
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); toggleSound(); }}
                className={`p-1.5 rounded transition-colors ${
                  soundEnabled ? 'bg-green-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                title={soundEnabled ? 'Disable sound notifications' : 'Enable sound notifications'}
              >
                {soundEnabled ? <Volume2 size={12} /> : <VolumeX size={12} />}
              </button>
              {/* Volume Slider */}
              {soundEnabled && (
                <div className="flex items-center gap-1 px-1">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={Math.round(soundVolume * 100)}
                    onChange={(e) => {
                      const newVolume = parseInt(e.target.value) / 100;
                      setSoundVolume(newVolume);
                      setSoundVolumeState(newVolume);
                    }}
                    onMouseUp={() => playSound('notification')}
                    className="w-12 h-1 bg-gray-600 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-2 [&::-webkit-slider-thumb]:h-2 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-green-400"
                    title={`Volume: ${Math.round(soundVolume * 100)}%`}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <span className="text-[9px] text-gray-400 w-6">{Math.round(soundVolume * 100)}%</span>
                </div>
              )}
              {toastHistory.length > 0 && (
                <button
                  onClick={(e) => { e.stopPropagation(); setShowToastHistory(true); setShowQuickActions(false); }}
                  className="p-1.5 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white relative"
                  title="Notification history"
                >
                  <History size={12} />
                  {toastHistory.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full text-[8px] text-white flex items-center justify-center">
                      {toastHistory.length > 9 ? '9+' : toastHistory.length}
                    </span>
                  )}
                </button>
              )}
              {isDev && (
                <button
                  onClick={(e) => { e.stopPropagation(); setShowDevTools(true); setShowQuickActions(false); }}
                  className="p-1.5 hover:bg-gray-700 rounded transition-colors text-purple-400 hover:text-white"
                  title="Dev Tools (localStorage Manager)"
                >
                  <Database size={12} />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Separator */}
        <div className="w-px h-3 bg-gray-700" />

        {/* Session Duration */}
        <span className="text-gray-600 text-[10px] flex items-center gap-0.5" title="Session duration">
          <Clock size={8} />
          {formatDuration(sessionDuration)}
        </span>

        {/* Time */}
        <span className="text-gray-500">{currentTime.toLocaleTimeString()}</span>

        {/* Version */}
        <span className="text-gray-600 text-[10px]">{version}</span>
      </div>

      {/* Dev Tools Panel (dev mode only) */}
      {showDevTools && <DevToolsPanel onClose={() => setShowDevTools(false)} />}

      {/* Toast History Panel */}
      {showToastHistory && (
        <div className="fixed bottom-8 right-4 w-80 max-h-96 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 flex flex-col">
          <div className="flex items-center justify-between p-3 border-b border-gray-700">
            <h3 className="text-white font-medium text-sm">Notification History</h3>
            <div className="flex items-center gap-2">
              {toastHistory.length > 0 && (
                <button
                  onClick={() => clearHistory()}
                  className="text-xs text-gray-400 hover:text-red-400 transition-colors"
                >
                  Clear
                </button>
              )}
              <button
                onClick={() => setShowToastHistory(false)}
                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
              >
                <X size={14} />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {toastHistory.length === 0 ? (
              <p className="text-gray-500 text-xs text-center py-4">No notifications yet</p>
            ) : (
              [...toastHistory].reverse().map((item) => (
                <ToastHistoryItem key={item.id} item={item} />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ToastHistoryItem({ item }: { item: ToastHistoryItem }) {
  const icons = {
    success: <CheckCircle size={14} className="text-green-400" />,
    error: <X size={14} className="text-red-400" />,
    warning: <AlertTriangle size={14} className="text-yellow-400" />,
    info: <Activity size={14} className="text-blue-400" />,
  };

  const bgColors = {
    success: 'bg-green-900/30',
    error: 'bg-red-900/30',
    warning: 'bg-yellow-900/30',
    info: 'bg-blue-900/30',
  };

  return (
    <div className={`flex items-start gap-2 p-2 rounded ${bgColors[item.type]}`}>
      {icons[item.type]}
      <div className="flex-1 min-w-0">
        <p className="text-gray-200 text-xs truncate">{item.message}</p>
        <p className="text-gray-500 text-[10px]">
          {new Date(item.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
