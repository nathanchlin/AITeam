import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { Suspense, useEffect, useState } from 'react';
import { World } from './components/Scene/World';
import { Sidebar } from './components/UI/Sidebar';
import { TaskPanel } from './components/UI/TaskPanel';
import { ChatPanel } from './components/UI/ChatPanel';
import { PipelinePanel } from './components/UI/PipelinePanel';
import { useAgentStore } from './stores/agentStore';
import { useWebSocket } from './hooks/useWebSocket';
import { GitBranch } from 'lucide-react';
import type { Agent } from './types';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

function App() {
  const { agents, setAgents, tasks, setTasks, pipelinePanelOpen, togglePipelinePanel } = useAgentStore();
  const { selectedAgentId, chatPanelOpen, streamContent } = useAgentStore();
  const [loading, setLoading] = useState(true);
  useWebSocket();

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agentsRes, tasksRes] = await Promise.all([
          fetch(`${API_BASE}/api/agents`),
          fetch(`${API_BASE}/api/tasks`),
        ]);

        const agentsData = await agentsRes.json();
        const tasksData = await tasksRes.json();

        setAgents(agentsData);
        setTasks(tasksData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [setAgents, setTasks]);

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
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[10, 10, 5]}
            intensity={1}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-10, -10, -5]} intensity={0.3} />

          <World agents={agents} />

          <Stars
            radius={100}
            depth={50}
            count={5000}
            factor={4}
            saturation={0}
            fade
            speed={1}
          />

          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={5}
            maxDistance={25}
            maxPolarAngle={Math.PI / 2 - 0.1}
          />
        </Suspense>
      </Canvas>

      {/* UI Overlay */}
      <Sidebar onCreateAgent={createAgent} />
      <TaskPanel tasks={tasks} onCreateTask={createTask} onStartTask={startTask} />

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

      {/* Pipeline Panel */}
      <PipelinePanel />

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

export default App;
