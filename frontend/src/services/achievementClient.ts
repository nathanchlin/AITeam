import type { AgentStats, Achievement } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function getAgentStats(agentId: string): Promise<AgentStats> {
  const response = await fetch(`${API_BASE}/api/agents/${agentId}/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch agent stats');
  }
  return response.json();
}

export async function getAllAgentStats(): Promise<Record<string, AgentStats>> {
  const response = await fetch(`${API_BASE}/api/agents/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch all agent stats');
  }
  return response.json();
}

export async function getAchievements(): Promise<Achievement[]> {
  const response = await fetch(`${API_BASE}/api/achievements`);
  if (!response.ok) {
    throw new Error('Failed to fetch achievements');
  }
  return response.json();
}

export async function getAgentAchievements(agentId: string): Promise<Achievement[]> {
  const response = await fetch(`${API_BASE}/api/agents/${agentId}/achievements`);
  if (!response.ok) {
    throw new Error('Failed to fetch agent achievements');
  }
  return response.json();
}
