import { useEffect, useCallback } from 'react';
import { useAgentStore } from '../stores/agentStore';

const STORAGE_KEY = 'aiteam_panel_state';

interface PanelState {
  sidebarOpen: boolean;
  taskPanelOpen: boolean;
  pipelinePanelOpen: boolean;
  pipelineHistoryOpen: boolean;
  imPanelOpen: boolean;
  projectsPanelOpen: boolean;
}

/**
 * Hook to persist panel open/close state to localStorage.
 * Restores previous state on mount, saves on toggle.
 */
export function usePanelPersistence() {
  const {
    sidebarOpen,
    taskPanelOpen,
    pipelinePanelOpen,
    pipelineHistoryOpen,
    imPanelOpen,
    projectsPanelOpen,
  } = useAgentStore();

  // Load saved state on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const state: Partial<PanelState> = JSON.parse(saved);
        // Only restore boolean values
        if (typeof state.sidebarOpen === 'boolean') {
          useAgentStore.setState({ sidebarOpen: state.sidebarOpen });
        }
        if (typeof state.taskPanelOpen === 'boolean') {
          useAgentStore.setState({ taskPanelOpen: state.taskPanelOpen });
        }
        if (typeof state.pipelinePanelOpen === 'boolean') {
          useAgentStore.setState({ pipelinePanelOpen: state.pipelinePanelOpen });
        }
        if (typeof state.pipelineHistoryOpen === 'boolean') {
          useAgentStore.setState({ pipelineHistoryOpen: state.pipelineHistoryOpen });
        }
        if (typeof state.imPanelOpen === 'boolean') {
          useAgentStore.setState({ imPanelOpen: state.imPanelOpen });
        }
        if (typeof state.projectsPanelOpen === 'boolean') {
          useAgentStore.setState({ projectsPanelOpen: state.projectsPanelOpen });
        }
        console.log('[PanelPersistence] Restored panel state from localStorage');
      }
    } catch (e) {
      console.warn('[PanelPersistence] Failed to load panel state:', e);
    }
  }, []);

  // Save state on change (debounced)
  const saveState = useCallback(() => {
    try {
      const state: PanelState = {
        sidebarOpen,
        taskPanelOpen,
        pipelinePanelOpen,
        pipelineHistoryOpen,
        imPanelOpen,
        projectsPanelOpen,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn('[PanelPersistence] Failed to save panel state:', e);
    }
  }, [sidebarOpen, taskPanelOpen, pipelinePanelOpen, pipelineHistoryOpen, imPanelOpen, projectsPanelOpen]);

  useEffect(() => {
    // Debounce saves
    const timer = setTimeout(saveState, 500);
    return () => clearTimeout(timer);
  }, [saveState]);

  return { saveState };
}
