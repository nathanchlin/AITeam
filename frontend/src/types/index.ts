export type AgentType = 'coder' | 'analyst' | 'assistant' | 'custom';
export type AgentStatus = 'idle' | 'working' | 'waiting' | 'error';
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
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
  custom: {
    primary: '#F59E0B',
    secondary: '#FBBF24',
    light: '#FCD34D',
  },
};

export const AGENT_LABELS: Record<AgentType, string> = {
  coder: '代码开发',
  analyst: '数据分析',
  assistant: '通用助手',
  custom: '自定义',
};
