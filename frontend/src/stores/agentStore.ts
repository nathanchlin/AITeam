import { create } from 'zustand';
import type { Agent, Task, WebSocketMessage } from '../types';

interface AgentState {
  // Agents
  agents: Agent[];
  selectedAgentId: string | null;
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  removeAgent: (id: string) => void;
  selectAgent: (id: string | null) => void;

  // Tasks
  tasks: Task[];
  selectedTaskId: string | null;
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;
  selectTask: (id: string | null) => void;
  setTaskResult: (id: string, result: string) => void;

  // UI State
  sidebarOpen: boolean;
  taskPanelOpen: boolean;
  chatPanelOpen: boolean;
  thinkingLog: Array<{ agentId: string; agentName: string; thought: string; timestamp: number }>;
  streamContent: Record<string, string>;

  toggleSidebar: () => void;
  toggleTaskPanel: () => void;
  toggleChatPanel: () => void;
  addThinkingLog: (agentId: string, agentName: string, thought: string) => void;
  clearThinkingLog: () => void;
  appendStreamContent: (taskId: string, content: string) => void;
  clearStreamContent: (taskId: string) => void;

  // WebSocket
  wsConnected: boolean;
  setWsConnected: (connected: boolean) => void;
  handleWebSocketMessage: (message: WebSocketMessage) => void;
}

export const useAgentStore = create<AgentState>((set, get) => ({
  // Agents
  agents: [],
  selectedAgentId: null,
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  updateAgent: (id, updates) =>
    set((state) => ({
      agents: state.agents.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    })),
  removeAgent: (id) =>
    set((state) => ({
      agents: state.agents.filter((a) => a.id !== id),
      selectedAgentId: state.selectedAgentId === id ? null : state.selectedAgentId,
    })),
  selectAgent: (id) => set({ selectedAgentId: id, chatPanelOpen: id !== null }),

  // Tasks
  tasks: [],
  selectedTaskId: null,
  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((state) => ({ tasks: [task, ...state.tasks] })),
  updateTask: (id, updates) =>
    set((state) => ({
      tasks: state.tasks.map((t) => (t.id === id ? { ...t, ...updates } : t)),
    })),
  removeTask: (id) =>
    set((state) => ({
      tasks: state.tasks.filter((t) => t.id !== id),
      selectedTaskId: state.selectedTaskId === id ? null : state.selectedTaskId,
    })),
  selectTask: (id) => set({ selectedTaskId: id }),
  setTaskResult: (id, result) =>
    set((state) => {
      // Clear stream content and set result
      const { [id]: _, ...rest } = state.streamContent;
      return {
        streamContent: rest,
        tasks: state.tasks.map((t) =>
          t.id === id ? { ...t, result, status: 'completed' as const, progress: 1 } : t
        ),
      };
    }),

  // UI State
  sidebarOpen: true,
  taskPanelOpen: false,
  chatPanelOpen: false,
  thinkingLog: [],
  streamContent: {},

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleTaskPanel: () => set((state) => ({ taskPanelOpen: !state.taskPanelOpen })),
  toggleChatPanel: () => set((state) => ({ chatPanelOpen: !state.chatPanelOpen })),
  addThinkingLog: (agentId, agentName, thought) =>
    set((state) => ({
      thinkingLog: [
        ...state.thinkingLog.slice(-50),
        { agentId, agentName, thought, timestamp: Date.now() },
      ],
    })),
  clearThinkingLog: () => set({ thinkingLog: [] }),
  appendStreamContent: (taskId, content) =>
    set((state) => ({
      streamContent: {
        ...state.streamContent,
        [taskId]: (state.streamContent[taskId] || '') + content,
      },
    })),
  clearStreamContent: (taskId) =>
    set((state) => {
      const { [taskId]: _, ...rest } = state.streamContent;
      return { streamContent: rest };
    }),

  // WebSocket
  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),
  handleWebSocketMessage: (message) => {
    const { type, data } = message;
    console.log('[WS] Received:', type, data);

    switch (type) {
      case 'agent_update':
        get().updateAgent(data.agent_id as string, {
          status: data.status as Agent['status'],
          current_task_id: data.current_task_id as string | undefined,
        });
        break;

      case 'task_update':
        const status = data.status as Task['status'];
        get().updateTask(data.task_id as string, {
          status,
          progress: data.progress as number,
          result: data.result as string | undefined,
        });
        // When task completes, clear stream content
        if (status === 'completed' && data.result) {
          get().clearStreamContent(data.task_id as string);
        }
        break;

      case 'thinking':
        get().addThinkingLog(
          data.agent_id as string,
          data.agent_name as string,
          data.thought as string
        );
        break;

      case 'stream':
        get().appendStreamContent(data.task_id as string, data.content as string);
        get().updateTask(data.task_id as string, {
          progress: data.progress as number,
        });
        break;

      case 'chat':
        break;

      default:
        break;
    }
  },
}));
