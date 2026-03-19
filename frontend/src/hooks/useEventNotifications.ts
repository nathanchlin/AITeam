import { useEffect, useRef } from 'react';
import { useAgentStore } from '../stores/agentStore';
import { useToast } from '../components/common/Toast';
import { useSoundNotifications } from './useSoundNotifications';

/**
 * Hook to automatically show toast notifications for important events
 * - Task completions
 * - Agent errors
 * - Pipeline completions
 */
export function useEventNotifications() {
  const { agents, tasks, plans } = useAgentStore();
  const toast = useToast();
  const { playSound } = useSoundNotifications();

  // Track previous states to detect changes
  const prevTaskStatuses = useRef<Map<string, string>>(new Map());
  const prevAgentStatuses = useRef<Map<string, string>>(new Map());
  const prevPlanStatuses = useRef<Map<string, string>>(new Map());

  // Notification settings from localStorage
  const getSettings = () => {
    try {
      const saved = localStorage.getItem('aiteam_event_notifications');
      return saved ? JSON.parse(saved) : {
        taskComplete: true,
        agentError: true,
        pipelineComplete: true,
      };
    } catch {
      return { taskComplete: true, agentError: true, pipelineComplete: true };
    }
  };

  const settings = getSettings();

  useEffect(() => {
    // Check for task completions
    tasks.forEach(task => {
      const prevStatus = prevTaskStatuses.current.get(task.id);
      if (prevStatus && prevStatus !== 'completed' && task.status === 'completed') {
        if (settings.taskComplete) {
          const agent = agents.find(a => a.id === task.agent_id);
          toast.success(`${agent?.name || 'Agent'} 完成任务: ${task.title.slice(0, 50)}${task.title.length > 50 ? '...' : ''}`);
          playSound('success');
        }
      }
      // Check for task failures
      if (prevStatus && prevStatus !== 'failed' && task.status === 'failed') {
        playSound('error');
      }
      prevTaskStatuses.current.set(task.id, task.status);
    });

    // Clean up completed tasks from tracking
    const currentTaskIds = new Set(tasks.map(t => t.id));
    prevTaskStatuses.current.forEach((_, id) => {
      if (!currentTaskIds.has(id)) {
        prevTaskStatuses.current.delete(id);
      }
    });
  }, [tasks, agents, toast, settings.taskComplete, playSound]);

  useEffect(() => {
    // Check for agent errors
    agents.forEach(agent => {
      const prevStatus = prevAgentStatuses.current.get(agent.id);
      if (prevStatus && prevStatus !== 'error' && agent.status === 'error') {
        if (settings.agentError) {
          toast.error(`${agent.name} 遇到错误`);
          playSound('error');
        }
      }
      prevAgentStatuses.current.set(agent.id, agent.status);
    });

    // Clean up
    const currentAgentIds = new Set(agents.map(a => a.id));
    prevAgentStatuses.current.forEach((_, id) => {
      if (!currentAgentIds.has(id)) {
        prevAgentStatuses.current.delete(id);
      }
    });
  }, [agents, toast, settings.agentError, playSound]);

  useEffect(() => {
    // Check for pipeline completions
    plans.forEach(plan => {
      const prevStatus = prevPlanStatuses.current.get(plan.id);
      if (prevStatus && prevStatus !== 'completed' && plan.status === 'completed') {
        if (settings.pipelineComplete) {
          toast.success(`Pipeline 完成: ${plan.title || '未命名'}`);
          playSound('success');
        }
      }
      prevPlanStatuses.current.set(plan.id, plan.status);
    });

    // Clean up
    const currentPlanIds = new Set(plans.map(p => p.id));
    prevPlanStatuses.current.forEach((_, id) => {
      if (!currentPlanIds.has(id)) {
        prevPlanStatuses.current.delete(id);
      }
    });
  }, [plans, toast, settings.pipelineComplete, playSound]);
}
