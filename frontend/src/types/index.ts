export type AgentType = 'coder' | 'analyst' | 'assistant' | 'tester' | 'custom';
export type AgentStatus = 'idle' | 'working' | 'waiting' | 'error';
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';
export type PlanStatus = 'draft' | 'discussing' | 'approved' | 'pending_approval' | 'executing' | 'completed';

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  display_type?: string | null;
  description?: string;
  custom_prompt?: string;
  status: AgentStatus;
  position: Position;
  current_task_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  agent_id?: string;
  parent_task_id?: string;
  status: TaskStatus;
  progress: number;
  result?: string;
  thinking_process: ThinkingStep[];
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface ThinkingStep {
  step: number;
  thought: string;
  action?: string;
  timestamp: string;
}

// Discussion system
export interface DiscussionMessage {
  id: string;
  plan_id: string;
  agent_id: string;
  agent_name: string;
  agent_type: string;
  content: string;
  message_type: 'comment' | 'proposal' | 'question' | 'answer' | 'agreement';
  reply_to?: string;
  timestamp: string;
}

// Plan system
export interface PlanTask {
  id: string;
  title: string;
  description?: string;
  assigned_agent_id?: string;
  assigned_agent_type?: string;
  dependencies: string[];
  status: TaskStatus;
  order: number;
}

export interface IterationTask {
  id: string;
  iteration_round: number;
  title: string;
  description?: string;
  assigned_agent_id?: string;
  assigned_agent_type?: string;
  dependencies: string[];
  status: TaskStatus;
  order: number;
}

export interface IterationRound {
  round_number: number;
  iteration_request: string;
  status: PlanStatus;
  tasks: IterationTask[];
  discussion: DiscussionMessage[];
  created_at: string;
  completed_at?: string;
  archive_path?: string | null;  // 存档路径
}

export interface Plan {
  id: string;
  title: string;
  description?: string;
  original_request: string;
  target_output?: string;
  status: PlanStatus;
  tasks: PlanTask[];
  discussion: DiscussionMessage[];
  is_approved: boolean;
  created_by_agent_id?: string;
  selected_agent_ids: string[];
  iterations: IterationRound[];
  current_iteration_round: number;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface ChatMessage {
  id: string;
  agent_id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

export interface WebSocketMessage {
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export const AGENT_COLORS: Record<AgentType, { primary: string; secondary: string; light: string }> = {
  coder: {
    primary: '#3B82F6',
    secondary: '#60A5FA',
    light: '#93C5FD',
  },
  analyst: {
    primary: '#10B981',
    secondary: '#34D399',
    light: '#6EE7B7',
  },
  assistant: {
    primary: '#8B5CF6',
    secondary: '#A78BFA',
    light: '#C4B5FD',
  },
  tester: {
    primary: '#F97316',
    secondary: '#FB923C',
    light: '#FDBA74',
  },
  custom: {
    primary: '#F59E0B',
    secondary: '#FBBF24',
    light: '#FCD34D',
  },
};

export const AGENT_LABELS: Record<AgentType, string> = {
  coder: '代码开发',
  analyst: '数据分析',
  assistant: '协调者',
  tester: '测试工程师',
  custom: '自定义',
};

// Helper function to get display type (prefer custom display_type over default label)
export function getAgentDisplayType(agent: { type: AgentType; display_type?: string | null }): string {
  if (agent.display_type) {
    return agent.display_type;
  }
  return AGENT_LABELS[agent.type] || agent.type;
}

// Archive Management Types
export interface ArchiveInfo {
  round_number: number;
  label: string;
  archive_name: string;
  archive_path: string;
  size: number;
  modified_at: string;
  custom_name?: string | null;
  description?: string | null;
  checksum?: string | null;
}

export interface ArchiveDiffResult {
  from_round: number;
  to_round: number;
  from_size: number;
  to_size: number;
  additions: number;
  deletions: number;
  diff_lines: string[];
}

export interface ArchiveValidationResult {
  round_number: number;
  valid: boolean;
  checksum_match: boolean;
  file_exists: boolean;
  errors: string[];
  warnings: string[];
}

// Agent Statistics and Achievement System
export interface AgentStats {
  agent_id: string;
  level: number;
  xp: number;
  xp_to_next_level: number;
  tasks_completed: number;
  tasks_successful: number;
  quality_streak: number;
  pipeline_count: number;
  motivation: number;
  satisfaction: number;
  achievements: string[];
  emotion_state?: {
    key: string;
    emoji: string;
    label: string;
  };
  // Score tracking
  score: number;
  discussion_count: number;
  total_tokens_used: number;
  prompt_tokens_used: number;
  completion_tokens_used: number;
  discussion_score: number;
  task_score: number;
  token_bonus_score: number;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
}

export interface AchievementNotification {
  agent_id: string;
  agent_name: string;
  achievement: Achievement;
}
