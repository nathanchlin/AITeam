import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { Suspense, useEffect, useState } from 'react';
import { World } from './components/Scene/World';
import { Sidebar } from './components/UI/Sidebar';
import { TaskPanel } from './components/UI/TaskPanel';
import { ChatPanel } from './components/UI/ChatPanel';
import { PipelinePanel } from './components/UI/PipelinePanel';
import { ProjectsPanel } from './components/UI/ProjectsPanel';
import { AchievementNotification } from './components/UI/AchievementNotification';
import { GroupChatPanel } from './components/UI/GroupChatPanel';
import ErrorBoundary from './components/common/ErrorBoundary';
import { useAgentStore } from './stores/agentStore';
import { useWebSocket } from './hooks/useWebSocket';
import { GitBranch, Folder, MessageCircle } from 'lucide-react';
import type { Agent } from './types';

const API_BASE = import.meta.env.PROD ? '' : `http://${window.location.hostname}:8000`;

function AppContent() {
  const { agents, setAgents, tasks, setTasks, pipelinePanelOpen, togglePipelinePanel, projectsPanelOpen, toggleProjectsPanel, setPlans, setCurrentPlan, groupChats, setGroupChats, groupChatPanelOpen, toggleGroupChatPanel } = useAgentStore();
  const { selectedAgentId, chatPanelOpen, streamContent, isDraggingAgent } = useAgentStore();
  const [loading, setLoading] = useState(true);
  useWebSocket();

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
    try {
      const res = await fetch(`${API_BASE}/api/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          type,
          position: {
            x: (Math.random() - 0.5) * 8,
            y: 0,
            z: (Math.random() - 0.5) * 8,
          },
        }),
      });
      const agent = await res.json();
      useAgentStore.getState().addAgent(agent);
    } catch (error) {
      console.error('Failed to create agent:', error);
    }
  };

  const createTask = async (title: string, agentId?: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, agent_id: agentId }),
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

  if (loading) {
    return (
      <div className="flex items-center justify-center w-full h-full bg-gray-900">
        <div className="text-white text-xl animate-pulse">Loading AITeam...</div>
      </div>
    );
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
          />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <Sidebar onCreateAgent={createAgent} />
      <TaskPanel tasks={tasks} onCreateTask={createTask} onStartTask={startTask} />

      {/* Achievement Notifications - Temporarily hidden due to UI issues */}
      {/* <AchievementNotification /> */}

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
      </button>

      {/* Projects Button */}
      <button
        onClick={toggleProjectsPanel}
        className={`absolute top-2 right-4 z-20 px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          projectsPanelOpen
            ? 'bg-yellow-600 text-white'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
      >
        <Folder size={18} />
        <span className="text-sm font-medium">项目</span>
      </button>

      {/* Group Chat Button */}
      <button
        onClick={toggleGroupChatPanel}
        className={`absolute top-2 left-[140px] z-20 px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          groupChatPanelOpen
            ? 'bg-green-600 text-white'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
        }`}
      >
        <MessageCircle size={18} />
        <span className="text-sm font-medium">群聊</span>
      </button>

      {/* Pipeline Panel */}
      <PipelinePanel />

      {/* Projects Panel */}
      <ProjectsPanel />

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

      {/* Connection status */}
      <ConnectionStatus />
    </div>
  );
}

function ConnectionStatus() {
  const { wsConnected } = useAgentStore();

  return (
    <div className="absolute bottom-4 left-4 z-10">
      <div
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
          wsConnected
            ? 'bg-green-500/20 text-green-400'
            : 'bg-red-500/20 text-red-400'
        }`}
      >
        <div
          className={`w-2 h-2 rounded-full ${
            wsConnected ? 'bg-green-500' : 'bg-red-500 animate-pulse'
          }`}
        />
        {wsConnected ? 'Connected' : 'Connecting...'}
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}

export default App;
