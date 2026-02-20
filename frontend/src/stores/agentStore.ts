import { create } from 'zustand';
import type { Agent, Task, Plan, DiscussionMessage, WebSocketMessage } from '../types';

interface AgentState {
  // Agents
  agents: Agent[];
  selectedAgentId: string | null;
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  updateAgentPosition: (id: string, position: { x: number; y: number; z: number }) => Promise<void>;
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

  // Plans & Pipeline
  plans: Plan[];
  currentPlanId: string | null;
  setPlans: (plans: Plan[]) => void;
  addPlan: (plan: Plan) => void;
  updatePlan: (id: string, updates: Partial<Plan>) => void;
  setCurrentPlan: (id: string | null) => void;

  // Iteration Tab State
  activeIterationTab: number;  // 0 = 初始版本, 1+ = 迭代轮次
  setActiveIterationTab: (tab: number) => void;

  // Discussion
  discussionMessages: DiscussionMessage[];
  addDiscussionMessage: (msg: DiscussionMessage) => void;
  clearDiscussion: () => void;

  // Stream content
  streamContent: Record<string, string>;

  // UI State
  sidebarOpen: boolean;
  taskPanelOpen: boolean;
  chatPanelOpen: boolean;
  pipelinePanelOpen: boolean;
  projectsPanelOpen: boolean;
  thinkingLog: Array<{ agentId: string; agentName: string; thought: string; timestamp: number }>;

  toggleSidebar: () => void;
  toggleTaskPanel: () => void;
  toggleChatPanel: () => void;
  togglePipelinePanel: () => void;
  toggleProjectsPanel: () => void;
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
  updateAgentPosition: async (id: string, position: { x: number; y: number; z: number }) => {
    // Optimistic update
    set((state) => ({
      agents: state.agents.map((a) => (a.id === id ? { ...a, position } : a)),
    }));
    // Call backend API to persist position
    try {
      const response = await fetch(`/api/agents/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position }),
      });
      if (!response.ok) {
        console.error('Failed to update agent position');
      }
    } catch (error) {
      console.error('Failed to update agent position:', error);
    }
  },
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
      const { [id]: _, ...rest } = state.streamContent;
      return {
        streamContent: rest,
        tasks: state.tasks.map((t) =>
          t.id === id ? { ...t, result, status: 'completed' as const, progress: 1 } : t
        ),
      };
    }),

  // Plans
  plans: [],
  currentPlanId: null,
  setPlans: (plans) => set({ plans }),
  addPlan: (plan) => set((state) => ({ plans: [plan, ...state.plans] })),
  updatePlan: (id, updates) =>
    set((state) => ({
      plans: state.plans.map((p) => (p.id === id ? { ...p, ...updates } : p)),
    })),
  setCurrentPlan: (id) => set({ currentPlanId: id }),

  // Iteration Tab State
  activeIterationTab: 0,
  setActiveIterationTab: (tab) => set({ activeIterationTab: tab }),

  // Discussion
  discussionMessages: [],
  addDiscussionMessage: (msg) =>
    set((state) => ({
      discussionMessages: [...state.discussionMessages, msg],
    })),
  clearDiscussion: () => set({ discussionMessages: [] }),

  // Stream content
  streamContent: {},

  // UI State
  sidebarOpen: true,
  taskPanelOpen: false,
  chatPanelOpen: false,
  pipelinePanelOpen: false,
  projectsPanelOpen: false,
  thinkingLog: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleTaskPanel: () => set((state) => ({ taskPanelOpen: !state.taskPanelOpen })),
  toggleChatPanel: () => set((state) => ({ chatPanelOpen: !state.chatPanelOpen })),
  togglePipelinePanel: () => set((state) => ({ pipelinePanelOpen: !state.pipelinePanelOpen })),
  toggleProjectsPanel: () => set((state) => ({ projectsPanelOpen: !state.projectsPanelOpen })),
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
        // Stream can be for plan (discussion) or task (execution)
        const streamKey = (data.task_id || data.plan_id) as string;
        if (streamKey) {
          get().appendStreamContent(streamKey, data.content as string);
        }
        // Update task progress if task_id provided
        if (data.task_id) {
          const tasks = get().tasks;
          const existingTask = tasks.find(t => t.id === data.task_id);
          if (!existingTask) {
            // Task might be in plan tasks, not standalone tasks
          }
        }
        break;

      case 'discussion':
        const msg = data.message as DiscussionMessage;
        if (msg) {
          get().addDiscussionMessage(msg);
        }
        break;

      case 'plan_update':
        const planData = data.plan as Plan;
        if (planData) {
          const existingPlan = get().plans.find(p => p.id === planData.id);
          if (existingPlan) {
            get().updatePlan(planData.id, planData);
          } else {
            get().addPlan(planData);
          }
          // 如果有新迭代轮次，自动切换到新轮次
          const iterRound = data.iteration_round as number | undefined;
          if (iterRound && iterRound > 0) {
            get().setActiveIterationTab(iterRound);
          }
        }
        // Also handle partial plan updates (status, task status)
        if (data.plan_id && !planData) {
          const plan = get().plans.find(p => p.id === data.plan_id);
          if (plan) {
            const updates: Partial<Plan> = {};
            if (data.status) updates.status = data.status as Plan['status'];
            if (data.task_id && data.task_status) {
              updates.tasks = plan.tasks.map(t =>
                t.id === data.task_id ? { ...t, status: data.task_status as Plan['tasks'][0]['status'] } : t
              );
            }
            if (Object.keys(updates).length > 0) {
              get().updatePlan(data.plan_id as string, updates);
            }
          }
        }
        break;

      case 'iteration_discussion':
        // 迭代讨论消息
        const iterMsg = data.message as DiscussionMessage;
        const iterRound = data.iteration_round as number;
        if (iterMsg && data.plan_id && iterRound !== undefined) {
          const plan = get().plans.find(p => p.id === data.plan_id);
          if (plan && plan.iterations) {
            const updatedIterations = plan.iterations.map(iter => {
              if (iter.round_number === iterRound) {
                return {
                  ...iter,
                  discussion: [...iter.discussion, iterMsg]
                };
              }
              return iter;
            });
            get().updatePlan(data.plan_id as string, { iterations: updatedIterations });
          }
        }
        break;

      case 'iteration_task_update':
        // 迭代任务状态更新
        if (data.plan_id && data.iteration_round !== undefined && data.task_id) {
          const plan = get().plans.find(p => p.id === data.plan_id);
          if (plan && plan.iterations) {
            const updatedIterations = plan.iterations.map(iter => {
              if (iter.round_number === data.iteration_round) {
                const updatedTasks = iter.tasks.map(t =>
                  t.id === data.task_id ? { ...t, status: data.status as Plan['tasks'][0]['status'] } : t
                );
                return { ...iter, tasks: updatedTasks };
              }
              return iter;
            });
            get().updatePlan(data.plan_id as string, { iterations: updatedIterations });
          }
        }
        break;

      case 'chat':
        break;

      default:
        break;
    }
  },
}));
