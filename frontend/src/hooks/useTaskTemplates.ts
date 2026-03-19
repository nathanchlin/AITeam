import { useState, useEffect, useCallback } from 'react';
import type { TaskPriority } from '../types';

export interface TaskTemplate {
  id: string;
  name: string;
  title: string;
  description?: string;
  agentType?: string;
  priority: TaskPriority;
  dueDays?: number; // Days from now for due date
  createdAt: string;
  updatedAt: string;
}

interface UseTaskTemplatesReturn {
  templates: TaskTemplate[];
  addTemplate: (template: Omit<TaskTemplate, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTemplate: (id: string, updates: Partial<TaskTemplate>) => void;
  deleteTemplate: (id: string) => void;
  getTemplate: (id: string) => TaskTemplate | undefined;
  applyTemplate: (template: TaskTemplate) => {
    title: string;
    description?: string;
    priority: TaskPriority;
    dueDate?: string;
  };
}

const STORAGE_KEY = 'aiteam-task-templates';

// Default templates
const DEFAULT_TEMPLATES: TaskTemplate[] = [
  {
    id: 'default-1',
    name: 'Code Review',
    title: 'Review the code changes and provide feedback',
    priority: 'p1',
    dueDays: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'default-2',
    name: 'Write Tests',
    title: 'Write unit tests for the specified functionality',
    priority: 'p1',
    dueDays: 2,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'default-3',
    name: 'Bug Fix',
    title: 'Fix the reported bug',
    priority: 'p0',
    dueDays: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'default-4',
    name: 'Documentation',
    title: 'Write documentation for the feature',
    priority: 'p2',
    dueDays: 3,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export function useTaskTemplates(): UseTaskTemplatesReturn {
  const [templates, setTemplates] = useState<TaskTemplate[]>([]);

  // Load templates from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setTemplates(parsed);
      } catch {
        // If parsing fails, use defaults
        setTemplates(DEFAULT_TEMPLATES);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_TEMPLATES));
      }
    } else {
      // First time: initialize with defaults
      setTemplates(DEFAULT_TEMPLATES);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_TEMPLATES));
    }
  }, []);

  // Save templates to localStorage
  const saveTemplates = useCallback((newTemplates: TaskTemplate[]) => {
    setTemplates(newTemplates);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newTemplates));
  }, []);

  // Add a new template
  const addTemplate = useCallback((template: Omit<TaskTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newTemplate: TaskTemplate = {
      ...template,
      id: `template-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    saveTemplates([...templates, newTemplate]);
  }, [templates, saveTemplates]);

  // Update an existing template
  const updateTemplate = useCallback((id: string, updates: Partial<TaskTemplate>) => {
    const newTemplates = templates.map(t =>
      t.id === id
        ? { ...t, ...updates, updatedAt: new Date().toISOString() }
        : t
    );
    saveTemplates(newTemplates);
  }, [templates, saveTemplates]);

  // Delete a template
  const deleteTemplate = useCallback((id: string) => {
    const newTemplates = templates.filter(t => t.id !== id);
    saveTemplates(newTemplates);
  }, [templates, saveTemplates]);

  // Get a template by ID
  const getTemplate = useCallback((id: string) => {
    return templates.find(t => t.id === id);
  }, [templates]);

  // Apply template to create task data
  const applyTemplate = useCallback((template: TaskTemplate) => {
    const result: {
      title: string;
      description?: string;
      priority: TaskPriority;
      dueDate?: string;
    } = {
      title: template.title,
      priority: template.priority,
    };

    if (template.description) {
      result.description = template.description;
    }

    if (template.dueDays) {
      const dueDate = new Date();
      dueDate.setDate(dueDate.getDate() + template.dueDays);
      result.dueDate = dueDate.toISOString().split('T')[0];
    }

    return result;
  }, []);

  return {
    templates,
    addTemplate,
    updateTemplate,
    deleteTemplate,
    getTemplate,
    applyTemplate,
  };
}
