import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { Suspense, useEffect, useState, useMemo } from 'react';
import { World } from './components/Scene/World';
import { Sidebar } from './components/UI/Sidebar';
import { TaskPanel } from './components/UI/TaskPanel';
import { ChatPanel } from './components/UI/ChatPanel';
import { PipelinePanel } from './components/UI/PipelinePanel';
import { PipelineHistorySidebar } from './components/UI/PipelineHistorySidebar';
import { ProjectsPanel } from './components/UI/ProjectsPanel';
import { GroupChatPanel } from './components/UI/GroupChatPanel';
import { IMPanel } from './components/UI/IMPanel';
import { AgentActivityPanel } from './components/UI/AgentActivityPanel';
import { ActivityLogPanel } from './components/UI/ActivityLogPanel';
import { KeyboardHelpModal, type ShortcutItem } from './components/UI/KeyboardHelpModal';
import ErrorBoundary from './components/common/ErrorBoundary';
import { ToastProvider } from './components/common/Toast';
import { LoadingScreen } from './components/common/LoadingScreen';
import { GlobalTaskIndicator } from './components/common/GlobalTaskIndicator';
import { StatusBar } from './components/common/StatusBar';
import { useAgentStore } from './stores/agentStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useTheme } from './hooks/useTheme';
import { useNotifications } from './hooks/useNotifications';
import { useEventNotifications } from './hooks/useEventNotifications';
import { useAutoRefresh } from './hooks/useAutoRefresh';
import { usePanelPersistence } from './hooks/usePanelPersistence';
import { GitBranch, Folder, MessageCircle, Keyboard, BarChart2, Sun, Moon, Activity, Bell, BellOff } from 'lucide-react';
import type { Agent, TaskPriority } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

function AppContent() {
  const { agents, setAgents, tasks, setTasks, pipelinePanelOpen, togglePipelinePanel, projectsPanelOpen, toggleProjectsPanel, setPlans, setCurrentPlan, groupChats, setGroupChats, groupChatPanelOpen, imPanelOpen, toggleIMPanel, selectAgent, sidebarOpen, toggleSidebar, taskPanelOpen, toggleTaskPanel } = useAgentStore();
  const { selectedAgentId, chatPanelOpen, streamContent, isDraggingAgent } = useAgentStore();
  const [loading, setLoading] = useState(true);
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);
  const [showAgentActivity, setShowAgentActivity] = useState(false);
  const [showActivityLog, setShowActivityLog] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { enabled: notificationsEnabled, toggleNotifications, isSupported: notificationsSupported } = useNotifications();
  useWebSocket();
  useEventNotifications(); // Auto-show toast notifications for events
  useAutoRefresh({ enabled: true, onFocusRefresh: true, intervalMs: 60000 }); // Refresh on focus + every 60s
  usePanelPersistence(); // Persist panel open/close state

  // Define keyboard shortcuts
  const shortcuts = useMemo(() => [
    { key: '?', description: 'Show keyboard help', action: () => setShowKeyboardHelp(prev => !prev) },
    { key: 'Escape', description: 'Close all panels', action: () => {
      selectAgent(null);
      if (chatPanelOpen) useAgentStore.getState().toggleChatPanel?.();
      if (pipelinePanelOpen) togglePipelinePanel();
      if (projectsPanelOpen) toggleProjectsPanel();
      if (imPanelOpen) toggleIMPanel();
      setShowKeyboardHelp(false);
    }},
    { key: 'p', description: 'Toggle pipeline panel', action: togglePipelinePanel },
    { key: 'g', description: 'Toggle IM panel', action: toggleIMPanel },
    { key: 's', description: 'Toggle sidebar', action: toggleSidebar },
    { key: 't', description: 'Toggle task panel', action: toggleTaskPanel },
    { key: '/', description: 'Focus search (future)', action: () => {} },
    // Number key shortcuts for quick panel access
    { key: '1', description: 'Toggle sidebar (alt)', action: toggleSidebar },
    { key: '2', description: 'Toggle task panel (alt)', action: toggleTaskPanel },
    { key: '3', description: 'Toggle pipeline panel (alt)', action: togglePipelinePanel },
    { key: '4', description: 'Toggle IM panel (alt)', action: toggleIMPanel },
    { key: '5', description: 'Toggle projects panel (alt)', action: toggleProjectsPanel },
  ], [selectAgent, chatPanelOpen, pipelinePanelOpen, togglePipelinePanel, projectsPanelOpen, toggleProjectsPanel, imPanelOpen, toggleIMPanel, sidebarOpen, toggleSidebar, taskPanelOpen, toggleTaskPanel]);

  useKeyboardShortcuts(shortcuts, !loading);

  // Shortcut items for help modal
  const helpShortcuts: ShortcutItem[] = useMemo(() => [
    { key: '?', description: 'Show/hide keyboard help' },
    { key: 'Esc', description: 'Close all panels' },
    { key: 'P', description: 'Toggle pipeline panel' },
    { key: 'G', description: 'Toggle IM panel' },
    { key: 'S', description: 'Toggle sidebar' },
    { key: 'T', description: 'Toggle task panel' },
    { key: '1-5', description: 'Quick toggle panels (Sidebar/Task/Pipeline/IM/Projects)' },
  ], []);

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agentsRes, tasksRes, plansRes, groupChatsRes] = await Promise.all([
          fetch(`${API_BASE}/api/agents`),
          fetch(`${API_BASE}/api/tasks`),
          fetch(`${API_BASE}/api/pipeline/plans`),
          fetch(`${API_BASE}/api/group-chats`),
        ]);

        const agentsData = await agentsRes.json();
        const tasksData = await tasksRes.json();
        const plansData = await plansRes.json();
        const groupChatsData = await groupChatsRes.json();

        setAgents(agentsData);
        setTasks(tasksData);
        setPlans(plansData);
        setGroupChats(Array.isArray(groupChatsData) ? groupChatsData : []);

        // Set the most recent plan as current if exists
        if (plansData.length > 0) {
          setCurrentPlan(plansData[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [setAgents, setTasks, setPlans, setCurrentPlan, setGroupChats]);

  const createAgent = async (name: string, type: Agent['type']) => {
    // Calculate non-overlapping position using spiral layout
    const agentCount = agents.length;
    const angle = agentCount * 0.8; // Golden angle for better distribution
    const radius = 2 + agentCount * 0.5; // Gradually increase radius
    const position = {
      x: Math.cos(angle) * radius,
      y: 0,
      z: Math.sin(angle) * radius,
    };

    try {
      const res = await fetch(`${API_BASE}/api/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          type,
          position,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        console.error('Failed to create agent:', errorData);
        return;
      }
      const agent = await res.json();
      // Only add if response contains a valid agent with id and name
      if (agent && agent.id && agent.name) {
        useAgentStore.getState().addAgent(agent);
      }
    } catch (error) {
      console.error('Failed to create agent:', error);
    }
  };

  const createTask = async (title: string, agentId?: string, priority: TaskPriority = 'p2', dueDate?: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, agent_id: agentId, priority, due_date: dueDate }),
      });
      const task = await res.json();
      useAgentStore.getState().addTask(task);
      return task;
    } catch (error) {
      console.error('Failed to create task:', error);
      return null;
    }
  };

  const startTask = async (taskId: string) => {
    try {
      await fetch(`${API_BASE}/api/tasks/${taskId}/start`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to start task:', error);
    }
  };

  const deleteTasks = async (taskIds: string[]) => {
    try {
      await Promise.all(taskIds.map(id =>
        fetch(`${API_BASE}/api/tasks/${id}`, { method: 'DELETE' })
      ));
      useAgentStore.getState().setTasks(tasks.filter(t => !taskIds.includes(t.id)));
    } catch (error) {
      console.error('Failed to delete tasks:', error);
    }
  };

  const completeTasks = async (taskIds: string[]) => {
    try {
      await Promise.all(taskIds.map(id =>
        fetch(`${API_BASE}/api/tasks/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'completed' }),
        })
      ));
      useAgentStore.getState().setTasks(tasks.map(t =>
        taskIds.includes(t.id) ? { ...t, status: 'completed' } : t
      ));
    } catch (error) {
      console.error('Failed to complete tasks:', error);
    }
  };

  const updateTaskPriority = async (taskId: string, priority: TaskPriority) => {
    try {
      await fetch(`${API_BASE}/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priority }),
      });
      useAgentStore.getState().setTasks(tasks.map(t =>
        t.id === taskId ? { ...t, priority } : t
      ));
    } catch (error) {
      console.error('Failed to update task priority:', error);
    }
  };

  const duplicateTask = async (taskId: string) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;
      const res = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `${task.title} (Copy)`,
          description: task.description,
          agent_id: task.agent_id,
          priority: task.priority,
          due_date: task.due_date,
        }),
      });
      const newTask = await res.json();
      useAgentStore.getState().addTask(newTask);
    } catch (error) {
      console.error('Failed to duplicate task:', error);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  // Get the selected agent and its tasks
  const selectedAgent = agents.find((a) => a.id === selectedAgentId);
  const agentTasks = selectedAgentId ? tasks.filter((t) => t.agent_id === selectedAgentId) : [];

  // Get stream content for the current running task of the selected agent
  const currentRunningTask = agentTasks.find((t) => t.status === 'running');
  const currentStreamContent = currentRunningTask ? (streamContent[currentRunningTask.id] || '') : '';

  return (
    <div className="w-full h-full relative bg-gray-900">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [10, 10, 10], fov: 50 }}
        shadows
        className="w-full h-full"
      >
        <Suspense fallback={null}>
          {/* Office-style warm lighting */}
          <ambientLight intensity={0.5} color="#FFF8E7" />
          <directionalLight
            position={[10, 15, 5]}
            intensity={0.8}
            color="#FFF8E7"
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
            shadow-camera-far={50}
            shadow-camera-left={-20}
            shadow-camera-right={20}
            shadow-camera-top={20}
            shadow-camera-bottom={-20}
          />
          {/* Secondary light for fill */}
          <directionalLight
            position={[-5, 10, -5]}
            intensity={0.4}
            color="#E8E0D5"
          />
          {/* Accent light */}
          <pointLight position={[0, 5, 0]} intensity={0.3} color="#FFF8E7" distance={20} />

          <World agents={agents} />

          <OrbitControls
            enablePan={!isDraggingAgent}
            enableZoom={!isDraggingAgent}
            enableRotate={!isDraggingAgent}
            minDistance={5}
            maxDistance={25}
            maxPolarAngle={Math.PI / 2 - 0.1}
            enableDamping
            dampingFactor={0.05}
            zoomSpeed={0.5}
            rotateSpeed={0.5}
          />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <Sidebar onCreateAgent={createAgent} />
      <PipelineHistorySidebar />
      <TaskPanel
        tasks={tasks}
        onCreateTask={createTask}
        onStartTask={startTask}
        onDeleteTasks={deleteTasks}
        onCompleteTasks={completeTasks}
        onUpdateTaskPriority={updateTaskPriority}
        onDuplicateTask={duplicateTask}
        onBatchUpdatePriority={async (ids, priority) => { await Promise.all(ids.map(id => updateTaskPriority(id, priority))); }}
      />

      {/* Achievement Notifications - Temporarily hidden due to UI issues */}
      {/* <AchievementNotification /> */}

      {/* Global Task Indicator */}
      <GlobalTaskIndicator />

      {/* Pipeline Button */}
      <button
        onClick={togglePipelinePanel}
        className={`absolute top-2 left-1/2 transform -translate-x-1/2 z-20 px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          pipelinePanelOpen
            ? 'bg-purple-600 text-white'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
      >
        <GitBranch size={18} />
        <span className="text-sm font-medium">协作流水线</span>
        <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] bg-gray-700/50 rounded border border-gray-600 text-gray-400 ml-1">P</kbd>
      </button>

      {/* IM Button */}
      <button
        onClick={toggleIMPanel}
        className={`absolute top-2 left-[calc(50%+80px)] z-20 px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          imPanelOpen
            ? 'bg-green-600 text-white'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
      >
        <MessageCircle size={18} />
        <span className="text-sm font-medium">IM</span>
        <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] bg-gray-700/50 rounded border border-gray-600 text-gray-400 ml-1">G</kbd>
      </button>

      {/* Projects Button */}
      <button
        onClick={toggleProjectsPanel}
        className={`absolute top-2 right-[100px] z-20 px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          projectsPanelOpen
            ? 'bg-yellow-600 text-white'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
      >
        <Folder size={18} />
        <span className="text-sm font-medium">项目</span>
        <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] bg-gray-700/50 rounded border border-gray-600 text-gray-400 ml-1">5</kbd>
      </button>

      {/* Theme Toggle Button */}
      <button
        onClick={toggleTheme}
        className="absolute top-2 right-2 z-20 p-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
        title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      {/* Notification Toggle Button */}
      {notificationsSupported && (
        <button
          onClick={toggleNotifications}
          className={`absolute top-2 right-14 z-20 p-2 rounded-lg transition-colors ${
            notificationsEnabled
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
          }`}
          title={notificationsEnabled ? 'Notifications enabled (click to disable)' : 'Enable notifications'}
        >
          {notificationsEnabled ? <Bell size={18} /> : <BellOff size={18} />}
        </button>
      )}

      {/* Pipeline Panel */}
      <PipelinePanel />

      {/* Projects Panel */}
      <ProjectsPanel />

      {/* IM Panel */}
      {imPanelOpen && (
        <IMPanel isOpen={imPanelOpen} onClose={() => toggleIMPanel()} />
      )}

      {/* Group Chat Panel */}
      {groupChatPanelOpen && (
        <GroupChatPanel
          groupChats={groupChats}
          currentGroupChatId={useAgentStore.getState().currentGroupChatId}
        />
      )}

      {selectedAgent && chatPanelOpen && (
        <ChatPanel
          agent={selectedAgent}
          streamContent={currentStreamContent}
          tasks={agentTasks}
        />
      )}

      {/* Keyboard shortcut indicator - moved up to avoid StatusBar */}
      <button
        onClick={() => setShowKeyboardHelp(true)}
        className="absolute bottom-10 right-4 z-10 px-3 py-1.5 bg-gray-800/80 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white text-xs flex items-center gap-1.5 transition-colors"
      >
        <Keyboard size={12} />
        <span>Press <kbd className="px-1 bg-gray-700 rounded">?</kbd> for shortcuts</span>
      </button>

      {/* Agent Activity Button */}
      {selectedAgentId && (
        <button
          onClick={() => setShowAgentActivity(!showAgentActivity)}
          className={`absolute bottom-16 right-4 z-10 px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 transition-colors ${
            showAgentActivity
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white'
          }`}
        >
          <BarChart2 size={12} />
          <span>Agent Stats</span>
        </button>
      )}

      {/* Agent Activity Panel */}
      {showAgentActivity && (
        <AgentActivityPanel onClose={() => setShowAgentActivity(false)} />
      )}

      {/* Activity Log Button */}
      <button
        onClick={() => setShowActivityLog(!showActivityLog)}
        className={`absolute top-2 right-[220px] z-20 p-2 rounded-lg transition-colors ${
          showActivityLog
            ? 'bg-blue-600 text-white'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
        title="Activity Log"
      >
        <Activity size={18} />
      </button>

      {/* Activity Log Panel */}
      {showActivityLog && (
        <ActivityLogPanel onClose={() => setShowActivityLog(false)} />
      )}

      {/* Keyboard Help Modal */}
      <KeyboardHelpModal
        isOpen={showKeyboardHelp}
        onClose={() => setShowKeyboardHelp(false)}
        shortcuts={helpShortcuts}
      />

      {/* Status Bar */}
      <StatusBar />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
