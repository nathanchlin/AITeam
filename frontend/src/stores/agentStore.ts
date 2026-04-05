import { create } from 'zustand';
import type { Agent, Task, Plan, DiscussionMessage, WebSocketMessage, AgentStats, AchievementNotification, GroupChat, GroupChatMessage } from '../types';

// Stream buffer for batching updates (reduces UI re-renders)
const streamBuffer: Record<string, string> = {};
let streamFlushTimer: ReturnType<typeof setInterval> | null = null;

const startStreamFlushTimer = (flush: () => void) => {
  if (!streamFlushTimer) {
    streamFlushTimer = setInterval(flush, 300); // Flush every 300ms
  }
};

// Queue status interface
export interface QueueStatus {
  running_count: number;
  max_concurrent: number;
  queue_length: number;
  running_pipelines: Array<{
    plan_id: string;
    request: string;
    target_output: string;
    started_at: string | null;
  }>;
  queued_pipelines: Array<{
    plan_id: string;
    request: string;
    target_output: string;
    position: number;
    queued_at: string;
  }>;
}

interface AgentState {
  // Agents
  agents: Agent[];
  selectedAgentId: string | null;
  isDraggingAgent: boolean;
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  updateAgentPosition: (id: string, position: { x: number; y: number; z: number }) => Promise<void>;
  removeAgent: (id: string) => void;
  selectAgent: (id: string | null) => void;
  setIsDraggingAgent: (isDragging: boolean) => void;

  // Agent Stats & Achievements
  agentStats: Record<string, AgentStats>;
  achievementNotifications: AchievementNotification[];
  setAgentStats: (stats: Record<string, AgentStats>) => void;
  updateAgentStats: (agentId: string, stats: Partial<AgentStats>) => void;
  addAchievementNotification: (notification: AchievementNotification) => void;
  removeAchievementNotification: (index: number) => void;
  clearAchievementNotifications: () => void;
  fetchAgentStats: (agentId?: string) => Promise<void>;

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

  // Group Chat
  groupChats: GroupChat[];
  currentGroupChatId: string | null;
  setGroupChats: (chats: GroupChat[]) => void;
  addGroupChat: (chat: GroupChat) => void;
  updateGroupChat: (id: string, updates: Partial<GroupChat>) => void;
  setCurrentGroupChat: (id: string | null) => void;
  addGroupChatMessage: (message: GroupChatMessage) => void;

  // Stream content
  streamContent: Record<string, string>;

  // Queue Status
  queueStatus: QueueStatus | null;
  setQueueStatus: (status: QueueStatus) => void;

  // UI State
  sidebarOpen: boolean;
  pipelineHistoryOpen: boolean;
  taskPanelOpen: boolean;
  chatPanelOpen: boolean;
  pipelinePanelOpen: boolean;
  projectsPanelOpen: boolean;
  groupChatPanelOpen: boolean;
  imPanelOpen: boolean;
  vibeCodingPanelOpen: boolean;
  vibeCodingPlanId: string | null;
  thinkingLog: Array<{ agentId: string; agentName: string; thought: string; timestamp: number }>;

  toggleSidebar: () => void;
  togglePipelineHistory: () => void;
  toggleTaskPanel: () => void;
  toggleChatPanel: () => void;
  togglePipelinePanel: () => void;
  toggleProjectsPanel: () => void;
  toggleGroupChatPanel: () => void;
  toggleIMPanel: () => void;
  toggleVibeCodingPanel: () => void;
  setVibeCodingPlanId: (id: string | null) => void;
  addThinkingLog: (agentId: string, agentName: string, thought: string) => void;
  clearThinkingLog: () => void;
  appendStreamContent: (taskId: string, content: string) => void;
  flushStreamBuffer: () => void;
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
  isDraggingAgent: false,
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  updateAgent: (id, updates) =>
    set((state) => ({
      agents: state.agents.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    })),
  setIsDraggingAgent: (isDragging) => set({ isDraggingAgent: isDragging }),

  // Agent Stats & Achievements
  agentStats: {},
  achievementNotifications: [],
  setAgentStats: (stats) => set({ agentStats: stats }),
  updateAgentStats: (agentId, stats) =>
    set((state) => ({
      agentStats: {
        ...state.agentStats,
        [agentId]: { ...state.agentStats[agentId], ...stats },
      },
    })),
  addAchievementNotification: (notification) =>
    set((state) => ({
      achievementNotifications: [...state.achievementNotifications, notification],
    })),
  removeAchievementNotification: (index) =>
    set((state) => ({
      achievementNotifications: state.achievementNotifications.filter((_, i) => i !== index),
    })),
  clearAchievementNotifications: () => set({ achievementNotifications: [] }),
  fetchAgentStats: async (agentId?: string) => {
    try {
      const targetId = agentId || get().selectedAgentId;
      if (!targetId) return;

      const response = await fetch(`/api/agents/${targetId}/stats`);
      if (response.ok) {
        const stats = await response.json();
        get().updateAgentStats(targetId, stats);
      }
    } catch (error) {
      console.error('Failed to fetch agent stats:', error);
    }
  },
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
  setCurrentPlan: (id) => set({ 
    currentPlanId: id,
    activeIterationTab: 0  // 切换项目时重置到初始版本
  }),

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

  // Group Chat
  groupChats: [],
  currentGroupChatId: null,
  setGroupChats: (chats) => set({ groupChats: chats }),
  addGroupChat: (chat) =>
    set((state) => ({
      groupChats: [chat, ...state.groupChats],
    })),
  updateGroupChat: (id, updates) =>
    set((state) => ({
      groupChats: state.groupChats.map((c) => (c.id === id ? { ...c, ...updates } : c)),
    })),
  setCurrentGroupChat: (id) => set({ currentGroupChatId: id }),
  addGroupChatMessage: (message) => {
    console.log('[Store] addGroupChatMessage called:', message.chat_id, message.sender_name, message.content?.substring(0, 50));
    set((state) => {
      const chatExists = state.groupChats.some((chat) => chat.id === message.chat_id);
      if (!chatExists) {
        console.warn('[Store] Chat not found for message:', message.chat_id, 'available chats:', state.groupChats.map(c => c.id));
      }
      return {
        groupChats: state.groupChats.map((chat) =>
          chat.id === message.chat_id
            ? { ...chat, messages: [...chat.messages, message], updated_at: message.timestamp }
            : chat
        ),
      };
    });
  },
  toggleGroupChatPanel: () => set((state) => ({ groupChatPanelOpen: !state.groupChatPanelOpen })),

  // Stream content
  streamContent: {},

  // Queue Status
  queueStatus: null as QueueStatus | null,
  setQueueStatus: (status: QueueStatus) => set({ queueStatus: status }),

  // UI State
  sidebarOpen: false,
  pipelineHistoryOpen: true,
  taskPanelOpen: false,
  chatPanelOpen: false,
  pipelinePanelOpen: false,
  projectsPanelOpen: false,
  groupChatPanelOpen: false,
  imPanelOpen: false,
  vibeCodingPanelOpen: false,
  vibeCodingPlanId: null,
  thinkingLog: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  togglePipelineHistory: () => set((state) => ({ pipelineHistoryOpen: !state.pipelineHistoryOpen })),
  toggleTaskPanel: () => set((state) => ({ taskPanelOpen: !state.taskPanelOpen })),
  toggleChatPanel: () => set((state) => ({ chatPanelOpen: !state.chatPanelOpen })),
  togglePipelinePanel: () => set((state) => ({ pipelinePanelOpen: !state.pipelinePanelOpen })),
  toggleProjectsPanel: () => set((state) => ({ projectsPanelOpen: !state.projectsPanelOpen })),
  toggleIMPanel: () => set((state) => ({ imPanelOpen: !state.imPanelOpen })),
  toggleVibeCodingPanel: () => set((state) => ({ vibeCodingPanelOpen: !state.vibeCodingPanelOpen })),
  setVibeCodingPlanId: (id) => set({ vibeCodingPlanId: id }),
  addThinkingLog: (agentId, agentName, thought) =>
    set((state) => ({
      thinkingLog: [
        ...state.thinkingLog.slice(-50),
        { agentId, agentName, thought, timestamp: Date.now() },
      ],
    })),
  clearThinkingLog: () => set({ thinkingLog: [] }),
  // Internal function to flush buffer to state
  flushStreamBuffer: () => {
    const keys = Object.keys(streamBuffer);
    if (keys.length === 0) return;

    const updates: Record<string, string> = {};
    keys.forEach(key => {
      if (streamBuffer[key]) {
        updates[key] = streamBuffer[key];
        delete streamBuffer[key];
      }
    });

    if (Object.keys(updates).length > 0) {
      set((state) => {
        const newStreamContent = { ...state.streamContent };
        Object.keys(updates).forEach(key => {
          newStreamContent[key] = (newStreamContent[key] || '') + updates[key];
        });
        return { streamContent: newStreamContent };
      });
    }
  },

  appendStreamContent: (taskId, content) => {
    // Buffer the content instead of immediate state update
    streamBuffer[taskId] = (streamBuffer[taskId] || '') + content;
    // Start flush timer if not running
    startStreamFlushTimer(() => get().flushStreamBuffer());
  },
  clearStreamContent: (taskId) => {
    // Also clear from buffer
    delete streamBuffer[taskId];
    set((state) => {
      const { [taskId]: _, ...rest } = state.streamContent;
      return { streamContent: rest };
    });
  },

  // WebSocket
  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),
  handleWebSocketMessage: (message) => {
    const { type, data } = message;
    // 只打印非stream类型的消息，避免流式数据刷屏
    if (type !== 'stream') {
      console.log('[WS] Received:', type, data);
    }

    switch (type) {
      case 'agent_update':
        get().updateAgent(data.agent_id as string, {
          status: data.status as Agent['status'],
          current_task_id: data.current_task_id as string | undefined,
        });
        break;

      case 'task_update': {
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
      }

      case 'thinking':
        get().addThinkingLog(
          data.agent_id as string,
          data.agent_name as string,
          data.thought as string
        );
        break;

      case 'tool_call': {
        // Agent 调用工具
        const streamKey2 = (data.task_id || data.plan_id) as string;
        if (streamKey2) {
          get().appendStreamContent(
            streamKey2,
            `\n🔧 [工具调用] ${data.name || 'unknown'}(${JSON.stringify(data.arguments || {}).slice(0, 200)})\n`
          );
        }
        break;
      }

      case 'tool_result': {
        // 工具执行结果
        const streamKey3 = (data.task_id || data.plan_id) as string;
        if (streamKey3) {
          const resultPreview = typeof data.result === 'string'
            ? (data.result as string).slice(0, 300)
            : JSON.stringify(data.result).slice(0, 300);
          get().appendStreamContent(
            streamKey3,
            `📤 [工具结果] ${data.name || 'unknown'}: ${resultPreview}\n`
          );
        }
        break;
      }

      case 'stream': {
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
      }

      case 'discussion': {
        const msg = data.message as DiscussionMessage;
        if (msg) {
          get().addDiscussionMessage(msg);
        }
        break;
      }

      case 'plan_update': {
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
            // 处理迭代状态的部分更新
            if (data.iteration_round !== undefined && data.status) {
              const iterRoundNum = data.iteration_round as number;
              if (plan.iterations) {
                updates.iterations = plan.iterations.map(iter => {
                  if (iter.round_number === iterRoundNum) {
                    return { ...iter, status: data.status as Plan['status'] };
                  }
                  return iter;
                });
              }
            }
            if (Object.keys(updates).length > 0) {
              get().updatePlan(data.plan_id as string, updates);
            }
          }
        }
        break;
      }

      case 'plan_pending_approval': {
        // Update plan with pending_approval status
        const pendingPlanData = data.plan as Plan;
        if (pendingPlanData) {
          const existingPlan = get().plans.find(p => p.id === pendingPlanData.id);
          if (existingPlan) {
            get().updatePlan(pendingPlanData.id, pendingPlanData);
          } else {
            get().addPlan(pendingPlanData);
          }
        }
        break;
      }

      case 'iteration_pending_approval':
        // Update iteration with pending_approval status
        if (data.plan_id && data.iteration_round !== undefined) {
          const plan = get().plans.find(p => p.id === data.plan_id);
          if (plan && plan.iterations) {
            const updatedIterations = plan.iterations.map(iter => {
              if (iter.round_number === data.iteration_round) {
                return { ...iter, status: 'pending_approval' as const };
              }
              return iter;
            });
            get().updatePlan(data.plan_id as string, { iterations: updatedIterations });
          }
        }
        break;

      case 'iteration_discussion': {
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
      }

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

      case 'queue_update':
        // Queue status update from backend
        if (data.queue_status) {
          get().setQueueStatus(data.queue_status as QueueStatus);
        }
        break;

      case 'chat':
        break;

      case 'achievement_unlocked':
        // Handle achievement notification from backend
        if (data.notification) {
          const notification = data.notification as AchievementNotification;
          get().addAchievementNotification(notification);
          // Also update agent stats
          if (notification.agent_id) {
            get().fetchAgentStats(notification.agent_id);
          }
        }
        break;

      case 'score_update':
        // Handle score update from backend
        if (data.agent_id && data.total_score !== undefined) {
          get().updateAgentStats(data.agent_id as string, {
            score: data.total_score as number,
            discussion_count: data.discussion_count as number | undefined,
            discussion_score: data.discussion_score as number | undefined,
            task_score: data.task_score as number | undefined,
            token_bonus_score: data.token_bonus_score as number | undefined,
          });
        }
        break;

      case 'group_chat_message':
        // Handle new group chat message
        // Backend sends data as the message object directly
        console.log('[WS] Received group_chat_message:', data);
        if (data) {
          const message = data as unknown as GroupChatMessage;
          console.log('[WS] chat_id:', message.chat_id, 'current chats:', get().groupChats.map(c => c.id));
          get().addGroupChatMessage(message);
        }
        break;

      case 'group_chat_created':
        // Handle new group chat created
        // Backend sends data as the chat object directly
        if (data) {
          const chat = data as unknown as GroupChat;
          console.log('[WS] group_chat_created:', chat.id, chat.name);
          const existing = get().groupChats.find((c) => c.id === chat.id);
          if (!existing) {
            get().addGroupChat(chat);
          } else {
            get().updateGroupChat(chat.id, chat);
          }
        }
        break;

      case 'group_chat_member_added':
        // Handle member added to group chat
        if (data.chat_id && data.member) {
          get().updateGroupChat(data.chat_id as string, {
            members: [...(get().groupChats.find((c) => c.id === data.chat_id)?.members || []), data.member as unknown as import('../types').GroupChatMember],
          });
        }
        break;

      case 'group_chat_member_removed':
        // Handle member removed from group chat
        if (data.chat_id && data.member_id) {
          const chat = get().groupChats.find((c) => c.id === data.chat_id);
          if (chat) {
            get().updateGroupChat(data.chat_id as string, {
              members: chat.members.filter((m) => m.id !== data.member_id),
            });
          }
        }
        break;

      default:
        break;
    }
  },
}));
