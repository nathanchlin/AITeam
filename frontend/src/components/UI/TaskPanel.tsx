import { useState, useMemo, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { Task, TaskPriority, TaskStatus, TaskTag } from '../../types';
import { getAgentDisplayType, PRIORITY_COLORS, DEFAULT_TAGS } from '../../types';
import { ClipboardList, Play, Plus, X, CheckCircle, Clock, AlertCircle, Trash2, Copy, Download, ClipboardPaste, Flag, Layers, Sparkles, GripVertical, Tag, MessageCircle, Check, ChevronDown, ChevronRight, ChevronLeft, ListChecks, Link2, AlertTriangle, Bookmark, FileDown, FileJson, FileSpreadsheet, Calendar, List, Search, Archive, ArchiveRestore, Edit3, CalendarDays, User, Columns, ArrowUpDown, ArrowUp, ArrowDown, Filter, Network, Timer, Zap, TrendingDown } from 'lucide-react';
import { useTaskTemplates } from '../../hooks/useTaskTemplates';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { TaskCommentPanel } from './TaskCommentPanel';

interface TaskPanelProps {
  tasks: Task[];
  onCreateTask: (title: string, agentId?: string) => Promise<Task | null>;
  onStartTask: (taskId: string) => void;
  onDeleteTasks: (taskIds: string[]) => void;
  onCompleteTasks: (taskIds: string[]) => void;
  onUpdateTaskPriority: (taskId: string, priority: TaskPriority) => void;
  onUpdateTaskTags: (taskId: string, tags: string[]) => void;
  onDuplicateTask: (taskId: string) => void;
  onBatchUpdatePriority: (ids: string[], priority: TaskPriority) => Promise<void>;
  onAddComment: (taskId: string, content: string, mentions?: string[]) => void;
  onEditComment: (taskId: string, commentId: string, content: string) => void;
  onDeleteComment: (taskId: string, commentId: string) => void;
  onAddSubtask?: (taskId: string, title: string) => void;
  onToggleSubtask?: (taskId: string, subtaskId: string) => void;
  onDeleteSubtask?: (taskId: string, subtaskId: string) => void;
  onArchiveTask?: (taskId: string, archived: boolean) => void;
  onBatchEditTasks?: (ids: string[], updates: { description?: string; due_date?: string; agent_id?: string }) => Promise<void>;
}

export function TaskPanel({ tasks, onCreateTask, onStartTask, onDeleteTasks, onCompleteTasks, onUpdateTaskPriority: _onUpdateTaskPriority, onUpdateTaskTags, onDuplicateTask, onBatchUpdatePriority: _onBatchUpdatePriority, onAddComment, onEditComment, onDeleteComment, onAddSubtask, onToggleSubtask, onDeleteSubtask, onArchiveTask, onBatchEditTasks }: TaskPanelProps) {
  const { agents, taskPanelOpen, toggleTaskPanel, sidebarOpen, pipelineHistoryOpen, setTasks } = useAgentStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set());
  const [groupByPriority, setGroupByPriority] = useState(true);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');
  const [tagFilter, setTagFilter] = useState<string | null>(null);
  const [customTags] = useState<TaskTag[]>([...DEFAULT_TAGS]);
  const [showComments, setShowComments] = useState(false);
  const [selectedTaskForComments, setSelectedTaskForComments] = useState<Task | null>(null);
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  // Archive filter state
  const [showArchived, setShowArchived] = useState(false);
  // Subtask state
  const [expandedSubtasks, setExpandedSubtasks] = useState<Set<string>>(new Set());
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(() => {
    // Load from localStorage
    try {
      const saved = localStorage.getItem('taskPanel_collapsedGroups');
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  });
  const [addingSubtaskTo, setAddingSubtaskTo] = useState<string | null>(null);
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('');
  const { templates, applyTemplate, addTemplate, deleteTemplate } = useTaskTemplates();

  // Loading state - show skeleton on initial load
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  useEffect(() => {
    if (tasks.length > 0) {
      setIsInitialLoad(false);
    }
  }, [tasks.length]);

  // Drag and drop state
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [dragOverTaskId, setDragOverTaskId] = useState<string | null>(null);
  const [dragPosition, setDragPosition] = useState<'before' | 'after'>('after');
  const [dropSuccessId, setDropSuccessId] = useState<string | null>(null);

  // Show drop success animation
  const showDropSuccess = (taskId: string) => {
    setDropSuccessId(taskId);
    setTimeout(() => setDropSuccessId(null), 500);
  };

  // Batch operation menus
  const [showBatchPriorityMenu, setShowBatchPriorityMenu] = useState(false);
  const [showBatchTagMenu, setShowBatchTagMenu] = useState(false);

  // Template management state
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  const [savingTaskAsTemplate, setSavingTaskAsTemplate] = useState<string | null>(null);
  const [newTemplateName, setNewTemplateName] = useState('');

  // Keyboard navigation state
  const [focusedTaskIndex, setFocusedTaskIndex] = useState<number>(-1);

  // View mode state (list, calendar, kanban, or dependency)
  const [viewMode, setViewMode] = useState<'list' | 'calendar' | 'kanban' | 'dependency'>('list');
  const [calendarMonth, setCalendarMonth] = useState(new Date());
  const [selectedCalendarDate, setSelectedCalendarDate] = useState<string | null>(null);

  // Batch edit state
  const [showBatchEditModal, setShowBatchEditModal] = useState(false);
  const [batchEditDescription, setBatchEditDescription] = useState('');
  const [batchEditDueDate, setBatchEditDueDate] = useState('');
  const [batchEditAgentId, setBatchEditAgentId] = useState('');

  // Sorting state
  const [sortBy, setSortBy] = useState<'created' | 'due_date' | 'priority' | 'title'>('created');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showSortMenu, setShowSortMenu] = useState(false);

  // Quick filters state
  const [quickFilters, setQuickFilters] = useState<Set<'today' | 'week' | 'highPriority' | 'unassigned'>>(new Set());

  // Undo deletion state
  const [recentlyDeleted, setRecentlyDeleted] = useState<Array<{ task: Task; deletedAt: number; timerId: ReturnType<typeof setTimeout> }>>([]);

  // Toggle quick filter
  const toggleQuickFilter = (filter: 'today' | 'week' | 'highPriority' | 'unassigned') => {
    setQuickFilters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(filter)) {
        newSet.delete(filter);
      } else {
        newSet.add(filter);
      }
      return newSet;
    });
  };

  // Calculate position: stack horizontally after Agent Sidebar and Pipeline History
  const agentSidebarWidth = sidebarOpen ? 320 : 0;
  const pipelineHistoryWidth = pipelineHistoryOpen ? 280 : 0;
  const taskPanelLeft = agentSidebarWidth + pipelineHistoryWidth + 8;
  const taskPanelWidth = 280;
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<TaskPriority>('p2');
  const [newTaskEstimatedHours, setNewTaskEstimatedHours] = useState<string>('');
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');

  // Apply template to form
  const handleSelectTemplate = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      const data = applyTemplate(template);
      setNewTaskTitle(data.title);
      setNewTaskDescription(data.description || '');
      setNewTaskPriority(data.priority);
    }
  };

  // Subtask handlers
  const toggleSubtasksExpanded = (taskId: string) => {
    setExpandedSubtasks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  // Group collapse handler
  const toggleGroupCollapse = (groupKey: string) => {
    setCollapsedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupKey)) {
        newSet.delete(groupKey);
      } else {
        newSet.add(groupKey);
      }
      // Persist to localStorage
      localStorage.setItem('taskPanel_collapsedGroups', JSON.stringify([...newSet]));
      return newSet;
    });
  };

  const handleAddSubtask = (taskId: string) => {
    if (!newSubtaskTitle.trim() || !onAddSubtask) return;
    onAddSubtask(taskId, newSubtaskTitle.trim());
    setNewSubtaskTitle('');
    setAddingSubtaskTo(null);
  };

  const handleToggleSubtask = (taskId: string, subtaskId: string) => {
    if (onToggleSubtask) {
      onToggleSubtask(taskId, subtaskId);
    }
  };

  const handleDeleteSubtask = (taskId: string, subtaskId: string) => {
    if (onDeleteSubtask) {
      onDeleteSubtask(taskId, subtaskId);
    }
  };

  // Filter tasks by status and search first
  const filteredByStatus = useMemo(() => {
    let result = tasks;
    // Archive filter - by default hide archived, show only when showArchived is true
    if (!showArchived) {
      result = result.filter(t => !t.archived);
    } else {
      result = result.filter(t => t.archived);
    }
    if (statusFilter !== 'all') {
      result = result.filter(t => t.status === statusFilter);
    }
    if (tagFilter) {
      result = result.filter(t => t.tags?.includes(tagFilter));
    }
    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      result = result.filter(t =>
        t.title.toLowerCase().includes(query) ||
        (t.description?.toLowerCase().includes(query) ?? false)
      );
    }
    // Quick filters
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekEnd = new Date(today);
    weekEnd.setDate(weekEnd.getDate() + 7);
    if (quickFilters.has('today')) {
      result = result.filter(t => {
        if (!t.due_date) return false;
        const dueDate = new Date(t.due_date);
        return dueDate >= today && dueDate < new Date(today.getTime() + 24 * 60 * 60 * 1000);
      });
    }
    if (quickFilters.has('week')) {
      result = result.filter(t => {
        if (!t.due_date) return false;
        const dueDate = new Date(t.due_date);
        return dueDate >= today && dueDate <= weekEnd;
      });
    }
    if (quickFilters.has('highPriority')) {
      result = result.filter(t => t.priority === 'p0' || t.priority === 'p1');
    }
    if (quickFilters.has('unassigned')) {
      result = result.filter(t => !t.agent_id);
    }
    // Apply sorting
    const priorityOrder = { p0: 0, p1: 1, p2: 2, p3: 3 };
    result = [...result].sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'created':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'due_date':
          const aDue = a.due_date ? new Date(a.due_date).getTime() : Infinity;
          const bDue = b.due_date ? new Date(b.due_date).getTime() : Infinity;
          comparison = aDue - bDue;
          break;
        case 'priority':
          const aPriority = a.priority ? priorityOrder[a.priority] : 99;
          const bPriority = b.priority ? priorityOrder[b.priority] : 99;
          comparison = aPriority - bPriority;
          break;
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    return result;
  }, [tasks, statusFilter, tagFilter, searchQuery, showArchived, sortBy, sortOrder, quickFilters]);

  // Group tasks by priority
  const groupedTasks = useMemo(() => {
    if (!groupByPriority) return { all: filteredByStatus };
    const groups: Record<string, Task[]> = {
      p0: filteredByStatus.filter(t => t.priority === 'p0'),
      p1: filteredByStatus.filter(t => t.priority === 'p1'),
      p2: filteredByStatus.filter(t => t.priority === 'p2'),
      p3: filteredByStatus.filter(t => t.priority === 'p3'),
      none: filteredByStatus.filter(t => !t.priority),
    };
    return groups;
  }, [filteredByStatus, groupByPriority]);

  // Status counts
  const statusCounts = useMemo(() => ({
    all: tasks.length,
    pending: tasks.filter(t => t.status === 'pending').length,
    running: tasks.filter(t => t.status === 'running').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    failed: tasks.filter(t => t.status === 'failed').length,
  }), [tasks]);

  // Task duration helpers
  const getTaskDuration = (task: Task): number | null => {
    if (!task.started_at) return null;
    const start = new Date(task.started_at).getTime();
    const end = task.completed_at ? new Date(task.completed_at).getTime() : Date.now();
    return Math.floor((end - start) / 1000);
  };

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  };

  // Calendar helpers
  const getDaysInMonth = (date: Date): number => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date): number => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDateKey = (date: Date): string => {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  };

  const getTasksForDate = (dateKey: string): Task[] => {
    return tasks.filter(task => {
      // Check due_date
      if (task.due_date && task.due_date.startsWith(dateKey)) return true;
      // Check created_at
      if (task.created_at && task.created_at.startsWith(dateKey)) return true;
      // Check completed_at
      if (task.completed_at && task.completed_at.startsWith(dateKey)) return true;
      return false;
    });
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCalendarMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() + (direction === 'next' ? 1 : -1));
      return newMonth;
    });
  };

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const daysInMonth = getDaysInMonth(calendarMonth);
    const firstDay = getFirstDayOfMonth(calendarMonth);
    const days: Array<{ date: Date; isCurrentMonth: boolean; tasks: Task[] } | null> = [];

    // Add empty cells for days before the first day of month
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(calendarMonth.getFullYear(), calendarMonth.getMonth(), day);
      const dateKey = formatDateKey(date);
      days.push({
        date,
        isCurrentMonth: true,
        tasks: getTasksForDate(dateKey)
      });
    }

    return days;
  }, [calendarMonth, tasks]);

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', taskId);
    setDraggedTaskId(taskId);
  };

  const handleDragOver = (e: React.DragEvent, targetTaskId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    if (draggedTaskId === targetTaskId) return;

    const rect = (e.target as HTMLElement).closest('[data-task-id]')?.getBoundingClientRect();
    if (rect) {
      const midY = rect.top + rect.height / 2;
      setDragPosition(e.clientY < midY ? 'before' : 'after');
    }
    setDragOverTaskId(targetTaskId);
  };

  const handleDragLeave = () => {
    setDragOverTaskId(null);
  };

  const handleDrop = (e: React.DragEvent, targetTaskId: string) => {
    e.preventDefault();
    const sourceTaskId = e.dataTransfer.getData('text/plain');

    if (sourceTaskId === targetTaskId) {
      setDraggedTaskId(null);
      setDragOverTaskId(null);
      return;
    }

    // Reorder tasks
    const currentTasks = [...tasks];
    const sourceIndex = currentTasks.findIndex(t => t.id === sourceTaskId);
    const targetIndex = currentTasks.findIndex(t => t.id === targetTaskId);

    if (sourceIndex === -1 || targetIndex === -1) return;

    const [removed] = currentTasks.splice(sourceIndex, 1);
    const insertIndex = dragPosition === 'before' ? targetIndex : targetIndex + 1;
    currentTasks.splice(insertIndex > sourceIndex ? insertIndex - 1 : insertIndex, 0, removed);

    setTasks(currentTasks);
    setDraggedTaskId(null);
    setDragOverTaskId(null);

    // Show drop success animation
    showDropSuccess(sourceTaskId);
  };

  const handleDragEnd = () => {
    setDraggedTaskId(null);
    setDragOverTaskId(null);
  };

  // Export tasks to Markdown
  const exportToMarkdown = () => {
    let md = `# Task Export - ${new Date().toISOString().slice(0, 10)}\n\n`;
    md += `## Summary\n- Total: ${tasks.length}\n- Completed: ${tasks.filter(t => t.status === 'completed').length}\n- Running: ${tasks.filter(t => t.status === 'running').length}\n- Pending: ${tasks.filter(t => t.status === 'pending').length}\n\n---\n\n## Tasks\n\n`;
    tasks.forEach(task => {
      const statusEmoji = task.status === 'completed' ? '✅' : task.status === 'running' ? '🔄' : '⏳';
      md += `### ${statusEmoji} ${task.title}\n- **Status**: ${task.status}\n- **Priority**: ${task.priority || 'none'}\n- **Agent**: ${agents.find(a => a.id === task.agent_id)?.name || 'Unassigned'}\n`;
      if (task.description) md += `- **Description**: ${task.description}\n`;
      md += '\n';
    });
    downloadFile(md, 'tasks.md', 'text/markdown');
  };

  // Export tasks to JSON
  const exportToJSON = () => {
    const data = {
      exportDate: new Date().toISOString(),
      total: tasks.length,
      summary: {
        completed: tasks.filter(t => t.status === 'completed').length,
        running: tasks.filter(t => t.status === 'running').length,
        pending: tasks.filter(t => t.status === 'pending').length,
        failed: tasks.filter(t => t.status === 'failed').length,
      },
      tasks: tasks.map(task => ({
        id: task.id,
        title: task.title,
        description: task.description,
        status: task.status,
        priority: task.priority,
        agent_id: task.agent_id,
        agent_name: agents.find(a => a.id === task.agent_id)?.name || null,
        tags: task.tags,
        due_date: task.due_date,
        created_at: task.created_at,
        started_at: task.started_at,
        completed_at: task.completed_at,
        subtasks: task.subtasks?.map(st => ({
          id: st.id,
          title: st.title,
          completed: st.completed,
        })),
        dependencies: task.dependencies,
        comments_count: task.comments?.length,
      })),
    };
    downloadFile(JSON.stringify(data, null, 2), 'tasks.json', 'application/json');
  };

  // Export tasks to CSV
  const exportToCSV = () => {
    const headers = ['ID', 'Title', 'Description', 'Status', 'Priority', 'Agent', 'Tags', 'Due Date', 'Created At', 'Started At', 'Completed At', 'Subtasks Count', 'Dependencies Count'];
    const rows = tasks.map(task => [
      task.id,
      `"${(task.title || '').replace(/"/g, '""')}"`,
      `"${(task.description || '').replace(/"/g, '""')}"`,
      task.status,
      task.priority || '',
      agents.find(a => a.id === task.agent_id)?.name || '',
      (task.tags || []).join(';'),
      task.due_date || '',
      task.created_at || '',
      task.started_at || '',
      task.completed_at || '',
      task.subtasks?.length || 0,
      task.dependencies?.length || 0,
    ].join(','));

    const csv = [headers.join(','), ...rows].join('\n');
    downloadFile(csv, 'tasks.csv', 'text/csv');
  };

  // Helper function to download file
  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: `${mimeType};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Export menu state
  const [showExportMenu, setShowExportMenu] = useState(false);

  // Quick create from clipboard
  const handlePasteFromClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text.trim()) {
        const title = text.trim().slice(0, 100);
        await onCreateTask(title);
      }
    } catch (e) {
      console.error('Failed to read clipboard:', e);
    }
  };

  // Toggle task selection
  const toggleTaskSelection = (taskId: string) => {
    const newSelection = new Set(selectedTasks);
    if (newSelection.has(taskId)) {
      newSelection.delete(taskId);
    } else {
      newSelection.add(taskId);
    }
    setSelectedTasks(newSelection);
  };

  // Batch actions
  // Handle deletion with undo support
  const handleDeleteWithUndo = (taskIds: string[]) => {
    const tasksToDelete = tasks.filter(t => taskIds.includes(t.id));
    if (tasksToDelete.length === 0) return;

    // Store tasks for potential undo
    const newDeleted = tasksToDelete.map(task => ({
      task,
      deletedAt: Date.now(),
      timerId: setTimeout(() => {
        // After 5 seconds, permanently delete
        onDeleteTasks([task.id]);
        setRecentlyDeleted(prev => prev.filter(d => d.task.id !== task.id));
      }, 5000)
    }));

    setRecentlyDeleted(prev => [...prev, ...newDeleted]);

    // Remove from current view immediately
    const remainingTasks = tasks.filter(t => !taskIds.includes(t.id));
    setTasks(remainingTasks);
    setSelectedTasks(new Set());
  };

  // Undo deletion
  const handleUndoDelete = (taskId: string) => {
    const deleted = recentlyDeleted.find(d => d.task.id === taskId);
    if (deleted) {
      clearTimeout(deleted.timerId);
      const restoredTasks = [...tasks, deleted.task];
      setTasks(restoredTasks);
      setRecentlyDeleted(prev => prev.filter(d => d.task.id !== taskId));
    }
  };

  const handleBatchDelete = () => {
    if (selectedTasks.size > 0) {
      handleDeleteWithUndo(Array.from(selectedTasks));
    }
  };

  const handleBatchComplete = () => {
    if (selectedTasks.size > 0) {
      onCompleteTasks(Array.from(selectedTasks));
      setSelectedTasks(new Set());
    }
  };

  // Batch priority change
  const handleBatchPriorityChange = async (priority: TaskPriority) => {
    if (selectedTasks.size > 0 && _onBatchUpdatePriority) {
      await _onBatchUpdatePriority(Array.from(selectedTasks), priority);
      setSelectedTasks(new Set());
    }
  };

  // Batch tag assignment
  const handleBatchTagChange = (tagId: string) => {
    if (selectedTasks.size > 0) {
      selectedTasks.forEach(taskId => {
        const task = tasks.find(t => t.id === taskId);
        if (task) {
          const currentTags = task.tags || [];
          if (!currentTags.includes(tagId)) {
            onUpdateTaskTags(taskId, [...currentTags, tagId]);
          }
        }
      });
    }
  };

  // Select all / Deselect all
  const handleSelectAll = () => {
    setSelectedTasks(new Set(filteredByStatus.map(t => t.id)));
  };

  const handleDeselectAll = () => {
    setSelectedTasks(new Set());
  };

  // Save task as template
  const handleSaveAsTemplate = (task: Task) => {
    setSavingTaskAsTemplate(task.id);
    setNewTemplateName(task.title);
  };

  const confirmSaveAsTemplate = (task: Task) => {
    addTemplate({
      name: newTemplateName || task.title,
      title: task.title,
      description: task.description,
      priority: task.priority,
      dueDays: task.due_date ? Math.ceil((new Date(task.due_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)) : undefined,
    });
    setSavingTaskAsTemplate(null);
    setNewTemplateName('');
  };

  const handleDeleteTemplate = (templateId: string) => {
    if (confirm('确定要删除这个模板吗？')) {
      deleteTemplate(templateId);
    }
  };

  // Keyboard shortcuts for task panel
  useKeyboardShortcuts([
    // Navigation: Arrow Up/Down to focus tasks
    { key: 'ArrowUp', description: 'Focus previous task', action: () => {
      if (filteredByStatus.length > 0) {
        setFocusedTaskIndex(prev => Math.max(0, prev <= 0 ? filteredByStatus.length - 1 : prev - 1));
      }
    }},
    { key: 'ArrowDown', description: 'Focus next task', action: () => {
      if (filteredByStatus.length > 0) {
        setFocusedTaskIndex(prev => prev >= filteredByStatus.length - 1 ? 0 : prev + 1);
      }
    }},
    // Actions on focused task
    { key: 'Enter', description: 'Start focused task', action: () => {
      if (focusedTaskIndex >= 0 && focusedTaskIndex < filteredByStatus.length) {
        const task = filteredByStatus[focusedTaskIndex];
        if (task.status === 'pending' && task.agent_id) {
          onStartTask(task.id);
        }
      }
    }},
    { key: 'd', description: 'Delete focused task', action: () => {
      if (focusedTaskIndex >= 0 && focusedTaskIndex < filteredByStatus.length) {
        const task = filteredByStatus[focusedTaskIndex];
        onDeleteTasks([task.id]);
        setFocusedTaskIndex(prev => Math.min(prev, filteredByStatus.length - 2));
      }
    }},
    { key: 'c', description: 'Duplicate focused task', action: () => {
      if (focusedTaskIndex >= 0 && focusedTaskIndex < filteredByStatus.length) {
        const task = filteredByStatus[focusedTaskIndex];
        onDuplicateTask(task.id);
      }
    }},
    { key: 'e', description: 'Toggle subtasks for focused task', action: () => {
      if (focusedTaskIndex >= 0 && focusedTaskIndex < filteredByStatus.length) {
        const task = filteredByStatus[focusedTaskIndex];
        toggleSubtasksExpanded(task.id);
      }
    }},
    { key: ' ', ctrl: true, description: 'Select all tasks', action: handleSelectAll },
    { key: 'Escape', description: 'Deselect all / Clear focus', action: () => {
      setSelectedTasks(new Set());
      setFocusedTaskIndex(-1);
    }},
  ], taskPanelOpen);

  const handleCreate = async () => {
    if (newTaskTitle.trim()) {
      const task = await onCreateTask(
        newTaskTitle.trim(),
        selectedAgentId || undefined
      );
      if (task) {
        setNewTaskTitle('');
        setNewTaskDescription('');
        setSelectedAgentId('');
        setShowCreateModal(false);
      }
    }
  };

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={14} className="text-green-500" />;
      case 'running':
        return <Clock size={14} className="text-yellow-500 animate-spin" />;
      case 'failed':
        return <AlertCircle size={14} className="text-red-500" />;
      default:
        return <Clock size={14} className="text-gray-400" />;
    }
  };

  const getAgentName = (agentId?: string) => {
    if (!agentId) return 'Unassigned';
    const agent = agents.find((a) => a.id === agentId);
    return agent?.name || 'Unknown';
  };

  return (
    <>
      {/* Open button - shown when panel is closed */}
      {!taskPanelOpen && (
        <button
          onClick={toggleTaskPanel}
          className="absolute z-20 p-2 bg-gray-800 rounded-r-lg text-white hover:bg-gray-700 transition-colors"
          style={{
            left: `${taskPanelLeft}px`,
            top: '88px'
          }}
        >
          <ClipboardList size={20} />
        </button>
      )}

      {/* Task Panel - position based on Agent Sidebar and Pipeline History */}
      <div
        className={`absolute top-0 h-full bg-gray-800/95 backdrop-blur transition-all duration-300 z-10 ${
          taskPanelOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        style={{
          left: `${taskPanelLeft}px`,
          width: `${taskPanelWidth}px`,
          transform: taskPanelOpen ? 'translateX(0)' : `translateX(-${taskPanelWidth + 10}px)`
        }}
      >
        {/* Close button - top right corner */}
        <button
          onClick={toggleTaskPanel}
          className="absolute top-3 right-3 z-20 p-2 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors"
        >
          <X size={18} />
        </button>

        <div className="p-4 pt-12 h-full flex flex-col">
          {/* Header with actions */}
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-white">Tasks</h2>
            <div className="flex items-center gap-1">
              <button
                onClick={handlePasteFromClipboard}
                className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
                title="Quick create from clipboard"
              >
                <ClipboardPaste size={14} />
              </button>
              {/* Export dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  className={`p-1 rounded transition-colors ${showExportMenu ? 'bg-blue-600 text-white' : 'hover:bg-gray-700 text-gray-400 hover:text-white'}`}
                  title="Export Tasks"
                >
                  <Download size={14} />
                </button>
                {showExportMenu && (
                  <div className="absolute top-full right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-10 min-w-[120px]">
                    <button
                      onClick={() => { exportToMarkdown(); setShowExportMenu(false); }}
                      className="w-full text-left px-3 py-2 text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2 rounded-t-lg"
                    >
                      <FileDown size={12} className="text-gray-400" />
                      Markdown
                    </button>
                    <button
                      onClick={() => { exportToJSON(); setShowExportMenu(false); }}
                      className="w-full text-left px-3 py-2 text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                    >
                      <FileJson size={12} className="text-yellow-400" />
                      JSON
                    </button>
                    <button
                      onClick={() => { exportToCSV(); setShowExportMenu(false); }}
                      className="w-full text-left px-3 py-2 text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2 rounded-b-lg"
                    >
                      <FileSpreadsheet size={12} className="text-green-400" />
                      CSV
                    </button>
                  </div>
                )}
              </div>
              <button
                onClick={() => setGroupByPriority(!groupByPriority)}
                className={`p-1 rounded transition-colors ${groupByPriority ? 'bg-blue-600 text-white' : 'hover:bg-gray-700 text-gray-400 hover:text-white'}`}
                title="Group by priority"
              >
                <Flag size={14} />
              </button>
              {/* View mode toggle */}
              <div className="flex items-center bg-gray-700 rounded">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-1 rounded-l transition-colors ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
                  title="List view"
                >
                  <List size={12} />
                </button>
                <button
                  onClick={() => setViewMode('kanban')}
                  className={`p-1 transition-colors border-l border-gray-600 ${viewMode === 'kanban' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
                  title="Kanban view"
                >
                  <Columns size={12} />
                </button>
                <button
                  onClick={() => setViewMode('calendar')}
                  className={`p-1 transition-colors border-l border-gray-600 ${viewMode === 'calendar' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
                  title="Calendar view"
                >
                  <Calendar size={12} />
                </button>
                <button
                  onClick={() => setViewMode('dependency')}
                  className={`p-1 rounded-r transition-colors border-l border-gray-600 ${viewMode === 'dependency' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
                  title="Dependency graph"
                >
                  <Network size={12} />
                </button>
              </div>
              {/* Sort dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowSortMenu(!showSortMenu)}
                  className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white flex items-center gap-0.5"
                  title="Sort tasks"
                >
                  <ArrowUpDown size={14} />
                  {sortOrder === 'asc' ? <ArrowUp size={10} /> : <ArrowDown size={10} />}
                </button>
                {showSortMenu && (
                  <div className="absolute top-full right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-20 min-w-[120px]">
                    <div className="p-1">
                      {[
                        { key: 'created', label: 'Created Date' },
                        { key: 'due_date', label: 'Due Date' },
                        { key: 'priority', label: 'Priority' },
                        { key: 'title', label: 'Title' },
                      ].map((option) => (
                        <button
                          key={option.key}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (sortBy === option.key) {
                              setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                            } else {
                              setSortBy(option.key as typeof sortBy);
                              setSortOrder('desc');
                            }
                            setShowSortMenu(false);
                          }}
                          className={`w-full text-left px-2 py-1 text-xs rounded flex items-center justify-between ${
                            sortBy === option.key ? 'bg-blue-600/30 text-white' : 'text-gray-300 hover:bg-gray-700'
                          }`}
                        >
                          <span>{option.label}</span>
                          {sortBy === option.key && (
                            sortOrder === 'asc' ? <ArrowUp size={10} /> : <ArrowDown size={10} />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <button
                onClick={() => setShowTemplateManager(true)}
                className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
                title="Manage Templates"
              >
                <Bookmark size={14} />
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="p-1 hover:bg-gray-700 rounded transition-colors text-white"
              >
                <Plus size={16} />
              </button>
            </div>
          </div>

          {/* Statistics Summary */}
          <div className="mb-2 p-2 bg-gray-700/50 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-gray-400">Total: <span className="text-white font-medium">{tasks.length}</span></span>
                <span className="text-[10px] text-blue-400">Done: {tasks.filter(t => t.status === 'completed').length}</span>
                <span className="text-[10px] text-green-400">Run: {tasks.filter(t => t.status === 'running').length}</span>
                <span className="text-[10px] text-yellow-400">Wait: {tasks.filter(t => t.status === 'pending').length}</span>
              </div>
              {(() => {
                const overdueCount = tasks.filter(t => {
                  if (!t.due_date || t.status === 'completed') return false;
                  return new Date(t.due_date) < new Date();
                }).length;
                return overdueCount > 0 ? (
                  <span className="text-[10px] text-red-400 flex items-center gap-0.5">
                    <AlertTriangle size={10} />
                    {overdueCount} overdue
                  </span>
                ) : null;
              })()}
            </div>
            {/* Completion Progress Bar */}
            <div className="relative h-1.5 bg-gray-600 rounded-full overflow-hidden">
              {(() => {
                const completionRate = tasks.length > 0
                  ? Math.round((tasks.filter(t => t.status === 'completed').length / tasks.length) * 100)
                  : 0;
                return (
                  <>
                    <div
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-300"
                      style={{ width: `${completionRate}%` }}
                    />
                    <span className="absolute right-1 top-1/2 -translate-y-1/2 text-[8px] text-gray-300 font-medium">
                      {completionRate}%
                    </span>
                  </>
                );
              })()}
            </div>
            {/* Estimation Accuracy Stats */}
            {(() => {
              const tasksWithEstimation = tasks.filter(t => t.estimated_hours && t.started_at && t.completed_at);
              if (tasksWithEstimation.length === 0) return null;
              const avgAccuracy = tasksWithEstimation.reduce((sum, t) => {
                const actualHours = (new Date(t.completed_at!).getTime() - new Date(t.started_at!).getTime()) / (1000 * 60 * 60);
                const ratio = actualHours / t.estimated_hours!;
                return sum + Math.min(ratio, 2); // Cap at 200%
              }, 0) / tasksWithEstimation.length;
              const onTimeCount = tasksWithEstimation.filter(t => {
                const actualHours = (new Date(t.completed_at!).getTime() - new Date(t.started_at!).getTime()) / (1000 * 60 * 60);
                return actualHours <= t.estimated_hours!;
              }).length;
              return (
                <div className="mt-1 flex items-center justify-between text-[9px]">
                  <span className="text-purple-400 flex items-center gap-1">
                    <Timer size={8} />
                    Est. accuracy: {Math.round((1 / avgAccuracy) * 100)}%
                  </span>
                  <span className="text-gray-400">
                    {onTimeCount}/{tasksWithEstimation.length} on time
                  </span>
                </div>
              );
            })()}
          </div>

          {/* Sprint Overview */}
          {(() => {
            // Calculate current sprint (this week)
            const now = new Date();
            const startOfWeek = new Date(now);
            startOfWeek.setDate(now.getDate() - now.getDay()); // Sunday
            startOfWeek.setHours(0, 0, 0, 0);
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 6); // Saturday
            endOfWeek.setHours(23, 59, 59, 999);

            const sprintTasks = tasks.filter(t => {
              if (t.archived) return false;
              if (!t.due_date) return false;
              const dueDate = new Date(t.due_date);
              return dueDate >= startOfWeek && dueDate <= endOfWeek;
            });
            const sprintCompleted = sprintTasks.filter(t => t.status === 'completed').length;
            const sprintTotal = sprintTasks.length;
            const sprintProgress = sprintTotal > 0 ? Math.round((sprintCompleted / sprintTotal) * 100) : 0;
            const daysRemaining = Math.max(0, Math.ceil((endOfWeek.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));

            if (sprintTotal === 0) return null;

            return (
              <div className="mb-2 p-2 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/30">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1">
                    <Zap size={10} className="text-purple-400" />
                    <span className="text-[10px] text-purple-300 font-medium">Current Sprint</span>
                  </div>
                  <span className="text-[9px] text-gray-400">
                    {daysRemaining} days left
                  </span>
                </div>
                {/* Sprint Progress Bar */}
                <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden mb-1">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-300"
                    style={{ width: `${sprintProgress}%` }}
                  />
                  <span className="absolute right-1 top-1/2 -translate-y-1/2 text-[8px] text-gray-300 font-medium">
                    {sprintProgress}%
                  </span>
                </div>
                {/* Sprint Stats */}
                <div className="flex items-center justify-between text-[9px]">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">
                      <span className="text-white font-medium">{sprintTotal}</span> tasks
                    </span>
                    <span className="text-blue-400">
                      <span className="font-medium">{sprintCompleted}</span> done
                    </span>
                    <span className="text-yellow-400">
                      <span className="font-medium">{sprintTasks.filter(t => t.status === 'pending').length}</span> pending
                    </span>
                  </div>
                  {/* Burndown indicator */}
                  <div className="flex items-center gap-1 text-green-400">
                    <TrendingDown size={8} />
                    <span>On track</span>
                  </div>
                </div>
                {/* Quick sprint task preview */}
                <div className="mt-1.5 pt-1.5 border-t border-gray-700/50 max-h-[60px] overflow-y-auto">
                  {sprintTasks.slice(0, 3).map(task => (
                    <div key={task.id} className="flex items-center gap-1 text-[9px] text-gray-300 py-0.5">
                      {task.status === 'completed' ? (
                        <Check size={8} className="text-green-400" />
                      ) : task.status === 'running' ? (
                        <Play size={8} className="text-blue-400" />
                      ) : (
                        <Clock size={8} className="text-gray-500" />
                      )}
                      <span className="truncate">{task.title}</span>
                      {task.priority === 'p0' && (
                        <span className="px-1 rounded bg-red-500/30 text-red-300 text-[7px]">P0</span>
                      )}
                    </div>
                  ))}
                  {sprintTasks.length > 3 && (
                    <div className="text-[8px] text-gray-500 mt-0.5">
                      +{sprintTasks.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })()}

          {/* Search box */}
          <div className="relative mb-2">
            <Search size={12} className="absolute left-2 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tasks..."
              className="w-full pl-7 pr-2 py-1.5 bg-gray-700 rounded text-sm text-white border border-gray-600 focus:border-blue-500 focus:outline-none placeholder-gray-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
              >
                <X size={12} />
              </button>
            )}
          </div>

          {/* Status filter chips */}
          <div className="flex items-center gap-1 mb-2 flex-wrap">
            <Layers size={10} className="text-gray-500" />
            {(['all', 'pending', 'running', 'completed', 'failed'] as const).map(status => {
              const count = statusCounts[status];
              if (count === 0 && status !== 'all') return null;
              const colors: Record<typeof status, string> = {
                all: statusFilter === 'all' ? 'bg-gray-600 text-white' : 'bg-gray-700 text-gray-400',
                pending: statusFilter === 'pending' ? 'bg-yellow-600 text-white' : 'bg-gray-700 text-yellow-400',
                running: statusFilter === 'running' ? 'bg-green-600 text-white' : 'bg-gray-700 text-green-400',
                completed: statusFilter === 'completed' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-blue-400',
                failed: statusFilter === 'failed' ? 'bg-red-600 text-white' : 'bg-gray-700 text-red-400',
              };
              const labels: Record<typeof status, string> = {
                all: 'All',
                pending: 'Pending',
                running: 'Running',
                completed: 'Done',
                failed: 'Failed',
              };
              return (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${colors[status]}`}
                >
                  {labels[status]} {count}
                </button>
              );
            })}
            {/* Archive toggle */}
            <button
              onClick={() => setShowArchived(!showArchived)}
              className={`px-1.5 py-0.5 text-[10px] rounded transition-colors flex items-center gap-1 ${
                showArchived ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
              }`}
              title={showArchived ? 'Show active tasks' : 'Show archived tasks'}
            >
              <Archive size={10} />
              {showArchived ? 'Archived' : 'Archive'}
              <span className="text-[8px] opacity-75">({tasks.filter(t => t.archived).length})</span>
            </button>
          </div>

          {/* Quick filters */}
          <div className="flex items-center gap-1 mb-2 flex-wrap">
            <Filter size={10} className="text-gray-500" />
            {[
              { key: 'today', label: 'Today', icon: <CalendarDays size={10} /> },
              { key: 'week', label: 'This Week', icon: <Calendar size={10} /> },
              { key: 'highPriority', label: 'High P', icon: <Flag size={10} /> },
              { key: 'unassigned', label: 'Unassigned', icon: <User size={10} /> },
            ].map((filter) => (
              <button
                key={filter.key}
                onClick={() => toggleQuickFilter(filter.key as 'today' | 'week' | 'highPriority' | 'unassigned')}
                className={`px-1.5 py-0.5 text-[10px] rounded transition-colors flex items-center gap-0.5 ${
                  quickFilters.has(filter.key as 'today' | 'week' | 'highPriority' | 'unassigned')
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
                title={filter.label}
              >
                {filter.icon}
                <span>{filter.label}</span>
              </button>
            ))}
            {quickFilters.size > 0 && (
              <button
                onClick={() => setQuickFilters(new Set())}
                className="px-1.5 py-0.5 text-[10px] rounded bg-red-600/50 text-red-200 hover:bg-red-600 transition-colors"
              >
                Clear
              </button>
            )}
          </div>

          {/* Tag filter */}
          {customTags.length > 0 && (
            <div className="flex items-center gap-1 mb-2 flex-wrap">
              <Tag size={10} className="text-gray-400" />
              <button
                onClick={() => setTagFilter(null)}
                className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
                  tagFilter === null ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                All
              </button>
              {customTags.map(tag => (
                <button
                  key={tag.id}
                  onClick={() => setTagFilter(tag.id)}
                  className={`px-1.5 py-0.5 text-[10px] rounded transition-colors flex items-center gap-1 ${
                    tagFilter === tag.id ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                  }`}
                >
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: tag.color }}
                  />
                  {tag.name}
                </button>
              ))}
            </div>
          )}

          {/* Batch actions */}
          {selectedTasks.size > 0 && (
            <div className="mb-2 p-2 bg-blue-900/30 rounded-lg space-y-2">
              {/* Selection info and quick actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ListChecks size={14} className="text-blue-400" />
                  <span className="text-xs text-blue-300 font-medium">{selectedTasks.size} selected</span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={handleSelectAll}
                    className="px-1.5 py-0.5 text-[10px] bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
                    title="Select all"
                  >
                    All
                  </button>
                  <button
                    onClick={handleDeselectAll}
                    className="px-1.5 py-0.5 text-[10px] bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
                    title="Deselect all"
                  >
                    None
                  </button>
                </div>
              </div>
              {/* Batch action buttons */}
              <div className="flex items-center gap-1 flex-wrap">
                {/* Priority dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setShowBatchPriorityMenu(!showBatchPriorityMenu)}
                    className="px-2 py-1 bg-orange-600/80 text-white text-xs rounded hover:bg-orange-500 flex items-center gap-1"
                  >
                    <Flag size={12} />
                    Priority
                  </button>
                  {showBatchPriorityMenu && (
                    <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-10 min-w-[80px]">
                      {(['p0', 'p1', 'p2', 'p3'] as const).map(p => (
                        <button
                          key={p}
                          onClick={() => { handleBatchPriorityChange(p); setShowBatchPriorityMenu(false); }}
                          className={`w-full px-2 py-1 text-xs text-left hover:bg-gray-700 ${PRIORITY_COLORS[p].text}`}
                        >
                          {PRIORITY_COLORS[p].label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {/* Tag dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setShowBatchTagMenu(!showBatchTagMenu)}
                    className="px-2 py-1 bg-purple-600/80 text-white text-xs rounded hover:bg-purple-500 flex items-center gap-1"
                  >
                    <Tag size={12} />
                    Tag
                  </button>
                  {showBatchTagMenu && (
                    <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-600 rounded shadow-lg z-10 min-w-[100px]">
                      {customTags.map(tag => (
                        <button
                          key={tag.id}
                          onClick={() => { handleBatchTagChange(tag.id); setShowBatchTagMenu(false); }}
                          className="w-full px-2 py-1 text-xs text-left hover:bg-gray-700 flex items-center gap-1"
                        >
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: tag.color }} />
                          {tag.name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {/* Complete button */}
                <button
                  onClick={handleBatchComplete}
                  className="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-500 flex items-center gap-1"
                >
                  <Check size={12} />
                  Complete
                </button>
                {/* Delete button */}
                <button
                  onClick={handleBatchDelete}
                  className="px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-500 flex items-center gap-1"
                >
                  <Trash2 size={12} />
                  Delete
                </button>
                {/* Batch Edit button */}
                {onBatchEditTasks && (
                  <button
                    onClick={() => setShowBatchEditModal(true)}
                    className="px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-500 flex items-center gap-1"
                  >
                    <Edit3 size={12} />
                    Edit
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Task list, Calendar or Kanban view */}
          <div className="flex-1 overflow-y-auto space-y-1">
            {/* Show skeleton during initial load */}
            {isInitialLoad && tasks.length === 0 ? (
              <div className="space-y-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <TaskItemSkeleton key={i} />
                ))}
              </div>
            ) : viewMode === 'kanban' ? (
              /* Kanban View */
              <div className="flex flex-col h-full gap-2">
                {/* Kanban Columns */}
                <div className="flex-1 grid grid-cols-4 gap-1 min-h-0">
                  {(['pending', 'running', 'completed', 'failed'] as const).map(status => {
                    const columnTasks = filteredByStatus.filter(t => t.status === status);
                    const statusConfig = {
                      pending: { label: 'Pending', color: 'border-yellow-500', bg: 'bg-yellow-500/10', icon: <Clock size={12} className="text-yellow-400" /> },
                      running: { label: 'Running', color: 'border-green-500', bg: 'bg-green-500/10', icon: <Play size={12} className="text-green-400" /> },
                      completed: { label: 'Done', color: 'border-blue-500', bg: 'bg-blue-500/10', icon: <CheckCircle size={12} className="text-blue-400" /> },
                      failed: { label: 'Failed', color: 'border-red-500', bg: 'bg-red-500/10', icon: <AlertCircle size={12} className="text-red-400" /> },
                    };
                    const config = statusConfig[status];
                    return (
                      <div
                        key={status}
                        className={`flex flex-col border-t-2 ${config.color} ${config.bg} rounded-b`}
                        onDragOver={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.add('ring-2', 'ring-blue-400');
                        }}
                        onDragLeave={(e) => {
                          e.currentTarget.classList.remove('ring-2', 'ring-blue-400');
                        }}
                        onDrop={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove('ring-2', 'ring-blue-400');
                          if (draggedTaskId) {
                            const task = tasks.find(t => t.id === draggedTaskId);
                            if (task && task.status !== status) {
                              // Update task status via appropriate action
                              if (status === 'completed') {
                                onCompleteTasks([draggedTaskId]);
                              } else if (status === 'running') {
                                onStartTask(draggedTaskId);
                              }
                              // Note: pending and failed status changes would need backend support
                            }
                          }
                          setDraggedTaskId(null);
                        }}
                      >
                        {/* Column Header */}
                        <div className="flex items-center justify-between px-1.5 py-1 border-b border-gray-700">
                          <div className="flex items-center gap-1">
                            {config.icon}
                            <span className="text-[10px] font-medium text-gray-300">{config.label}</span>
                          </div>
                          <span className="text-[9px] bg-gray-700 px-1 rounded text-gray-400">{columnTasks.length}</span>
                        </div>
                        {/* Column Tasks */}
                        <div className="flex-1 overflow-y-auto p-1 space-y-1">
                          {columnTasks.map(task => (
                            <div
                              key={task.id}
                              draggable
                              onDragStart={(e) => {
                                e.dataTransfer.setData('text/plain', task.id);
                                setDraggedTaskId(task.id);
                              }}
                              className="p-1.5 bg-gray-800 rounded border border-gray-600 hover:border-gray-500 cursor-grab active:cursor-grabbing text-[10px]"
                            >
                              <div className="flex items-start gap-1">
                                <GripVertical size={10} className="text-gray-500 flex-shrink-0 mt-0.5" />
                                <div className="flex-1 min-w-0">
                                  <p className="text-gray-200 truncate">{task.title}</p>
                                  <div className="flex items-center gap-1 mt-0.5">
                                    <span className={`px-1 rounded text-[8px] ${
                                      task.priority === 'p0' ? 'bg-red-600 text-white' :
                                      task.priority === 'p1' ? 'bg-orange-600 text-white' :
                                      task.priority === 'p2' ? 'bg-yellow-600 text-black' :
                                      'bg-gray-600 text-white'
                                    }`}>
                                      {task.priority?.toUpperCase() || 'NP'}
                                    </span>
                                    {task.agent_id && (
                                      <span className="text-gray-500 text-[8px] truncate">
                                        {getAgentName(task.agent_id)}
                                      </span>
                                    )}
                                  </div>
                                  {/* Progress bar for tasks with subtasks */}
                                  {task.subtasks && task.subtasks.length > 0 && (
                                    <div className="mt-1">
                                      <div className="h-1 bg-gray-700 rounded overflow-hidden">
                                        <div
                                          className="h-full bg-blue-500 transition-all"
                                          style={{
                                            width: `${Math.round((task.subtasks.filter(s => s.completed).length / task.subtasks.length) * 100)}%`
                                          }}
                                        />
                                      </div>
                                      <span className="text-[8px] text-gray-500">
                                        {task.subtasks.filter(s => s.completed).length}/{task.subtasks.length}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                          {columnTasks.length === 0 && (
                            <div className="text-center py-4 text-[10px] text-gray-500">
                              No tasks
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : viewMode === 'calendar' ? (
              /* Calendar View */
              <div className="flex flex-col h-full">
                {/* Calendar Navigation */}
                <div className="flex items-center justify-between mb-2 px-1">
                  <button
                    onClick={() => navigateMonth('prev')}
                    className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  >
                    <ChevronLeft size={14} />
                  </button>
                  <span className="text-xs text-white font-medium">
                    {calendarMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </span>
                  <button
                    onClick={() => navigateMonth('next')}
                    className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  >
                    <ChevronRight size={14} />
                  </button>
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-0.5 text-center mb-1">
                  {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) => (
                    <div key={i} className="text-[8px] text-gray-500 py-0.5">{d}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-0.5 flex-1">
                  {calendarDays.map((day, i) => {
                    if (!day) {
                      return <div key={`empty-${i}`} className="aspect-square" />;
                    }
                    const { date, tasks: dayTasks } = day;
                    const dateKey = formatDateKey(date);
                    const isToday = formatDateKey(new Date()) === dateKey;
                    const isSelected = selectedCalendarDate === dateKey;

                    return (
                      <button
                        key={dateKey}
                        onClick={() => setSelectedCalendarDate(isSelected ? null : dateKey)}
                        className={`aspect-square p-0.5 rounded text-[10px] flex flex-col items-center justify-start relative transition-colors ${
                          isSelected
                            ? 'bg-blue-600 text-white'
                            : isToday
                            ? 'bg-gray-700 text-white ring-1 ring-blue-400'
                            : 'hover:bg-gray-700 text-gray-300'
                        }`}
                      >
                        <span className="font-medium">{date.getDate()}</span>
                        {dayTasks.length > 0 && (
                          <div className="flex gap-0.5 mt-0.5">
                            {dayTasks.slice(0, 3).map((t, idx) => (
                              <div
                                key={idx}
                                className={`w-1 h-1 rounded-full ${
                                  t.status === 'completed' ? 'bg-green-400' :
                                  t.status === 'running' ? 'bg-yellow-400' :
                                  t.status === 'failed' ? 'bg-red-400' :
                                  'bg-gray-400'
                                }`}
                              />
                            ))}
                            {dayTasks.length > 3 && (
                              <span className="text-[6px] text-gray-400">+{dayTasks.length - 3}</span>
                            )}
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Selected Date Tasks */}
                {selectedCalendarDate && (
                  <div className="mt-2 pt-2 border-t border-gray-700 max-h-[40%] overflow-y-auto">
                    <div className="text-[10px] text-gray-400 mb-1 px-1">
                      Tasks on {new Date(selectedCalendarDate + 'T00:00:00').toLocaleDateString()}
                    </div>
                    <div className="space-y-1">
                      {getTasksForDate(selectedCalendarDate).map(task => (
                        <div
                          key={task.id}
                          className="p-1.5 bg-gray-700/50 rounded text-[10px] text-gray-300 flex items-center gap-2"
                        >
                          {getStatusIcon(task.status)}
                          <span className="truncate flex-1">{task.title}</span>
                          <span className={`px-1 rounded text-[8px] ${
                            task.priority === 'p0' ? 'bg-red-600' :
                            task.priority === 'p1' ? 'bg-orange-600' :
                            task.priority === 'p2' ? 'bg-yellow-600' :
                            task.priority === 'p3' ? 'bg-blue-600' :
                            'bg-gray-600'
                          }`}>
                            {task.priority?.toUpperCase() || 'NP'}
                          </span>
                        </div>
                      ))}
                      {getTasksForDate(selectedCalendarDate).length === 0 && (
                        <div className="text-[10px] text-gray-500 text-center py-2">
                          No tasks on this date
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : viewMode === 'dependency' ? (
              /* Dependency Graph View */
              <div className="flex flex-col h-full">
                <div className="text-[10px] text-gray-400 mb-2 px-1">
                  {filteredByStatus.filter(t => t.dependencies && t.dependencies.length > 0).length} tasks with dependencies
                </div>
                <div className="flex-1 overflow-auto">
                  {filteredByStatus.filter(t => t.dependencies && t.dependencies.length > 0).length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center py-8">
                      <Network size={32} className="text-gray-500 mb-2" />
                      <p className="text-gray-400 text-xs">No task dependencies found</p>
                      <p className="text-gray-500 text-[10px] mt-1">Add dependencies to tasks to see them here</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {filteredByStatus
                        .filter(t => t.dependencies && t.dependencies.length > 0)
                        .map(task => (
                          <div
                            key={task.id}
                            className="p-2 bg-gray-700/50 rounded-lg border border-gray-600"
                          >
                            {/* Current Task */}
                            <div className="flex items-center gap-2 mb-2">
                              {getStatusIcon(task.status)}
                              <span className="text-xs text-white font-medium truncate flex-1">
                                {task.title}
                              </span>
                              <span className={`px-1.5 py-0.5 rounded text-[8px] font-medium ${
                                task.priority === 'p0' ? 'bg-red-600 text-white' :
                                task.priority === 'p1' ? 'bg-orange-600 text-white' :
                                task.priority === 'p2' ? 'bg-yellow-600 text-black' :
                                'bg-gray-600 text-white'
                              }`}>
                                {task.priority?.toUpperCase() || 'NP'}
                              </span>
                            </div>
                            {/* Dependencies */}
                            <div className="ml-4 space-y-1">
                              {task.dependencies?.map(depId => {
                                const depTask = tasks.find(t => t.id === depId);
                                const isCompleted = depTask?.status === 'completed';
                                const isBlocked = depTask && depTask.status !== 'completed';
                                return (
                                  <div
                                    key={depId}
                                    className={`flex items-center gap-2 p-1.5 rounded text-[10px] ${
                                      isCompleted
                                        ? 'bg-green-500/10 text-green-300'
                                        : isBlocked
                                        ? 'bg-yellow-500/10 text-yellow-300'
                                        : 'bg-gray-600/50 text-gray-400'
                                    }`}
                                  >
                                    <div className="flex items-center">
                                      <div className="w-3 h-3 border-l-2 border-b-2 border-gray-500 rounded-bl-sm" />
                                      <div className="w-4 border-t border-gray-500" />
                                    </div>
                                    {depTask ? (
                                      <>
                                        {getStatusIcon(depTask.status)}
                                        <span className="truncate">{depTask.title}</span>
                                        {isCompleted && <Check size={10} className="text-green-400 ml-auto" />}
                                        {isBlocked && <span title="Blocking"><AlertTriangle size={10} className="text-yellow-400 ml-auto" /></span>}
                                      </>
                                    ) : (
                                      <>
                                        <AlertCircle size={10} className="text-red-400" />
                                        <span className="text-red-400">Unknown task ({depId.slice(0, 8)}...)</span>
                                      </>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
                {/* Legend */}
                <div className="mt-2 pt-2 border-t border-gray-700 flex items-center gap-3 text-[9px] text-gray-400">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded bg-green-500" />
                    <span>Completed</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded bg-yellow-500" />
                    <span>Blocking</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded bg-red-500" />
                    <span>Unknown</span>
                  </div>
                </div>
              </div>
            ) : tasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12 px-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mb-4">
                  <ClipboardList size={32} className="text-blue-400" />
                </div>
                <h3 className="text-white text-base font-medium mb-2">No tasks yet</h3>
                <p className="text-gray-400 text-xs mb-4 max-w-[200px]">
                  Create your first task to start tracking work and assigning to agents
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                >
                  <Plus size={16} />
                  Create Task
                </button>
                <div className="mt-6 flex items-center gap-2 text-[10px] text-gray-500">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 rounded">Ctrl+N</kbd>
                  <span>or</span>
                  <kbd className="px-1.5 py-0.5 bg-gray-700 rounded">⌘+N</kbd>
                  <span>to quick create</span>
                </div>
              </div>
            ) : filteredByStatus.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12 px-4">
                <div className="w-14 h-14 rounded-full bg-yellow-500/20 flex items-center justify-center mb-3">
                  <Search size={24} className="text-yellow-400" />
                </div>
                <h3 className="text-white text-sm font-medium mb-1">No matching tasks</h3>
                <p className="text-gray-400 text-xs mb-3">
                  {statusFilter !== 'all' ? `No ${statusFilter} tasks` :
                   searchQuery ? `No tasks matching "${searchQuery}"` :
                   'No tasks match your filters'}
                </p>
                {(statusFilter !== 'all' || searchQuery || quickFilters.size > 0) && (
                  <button
                    onClick={() => {
                      setStatusFilter('all');
                      setSearchQuery('');
                      setQuickFilters(new Set());
                    }}
                    className="px-3 py-1.5 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            ) : groupByPriority ? (
              <>
                {(['p0', 'p1', 'p2', 'p3', 'none'] as const).map(priority => {
                  const groupTasks = groupedTasks[priority] || [];
                  if (groupTasks.length === 0) return null;
                  const priorityColors: Record<string, string> = {
                    p0: 'text-red-400 border-red-500',
                    p1: 'text-orange-400 border-orange-500',
                    p2: 'text-yellow-400 border-yellow-500',
                    p3: 'text-blue-400 border-blue-500',
                    none: 'text-gray-400 border-gray-500'
                  };
                  const priorityLabels: Record<string, string> = {
                    p0: 'P0 (Critical)',
                    p1: 'P1 (High)',
                    p2: 'P2 (Medium)',
                    p3: 'P3 (Low)',
                    none: 'No Priority'
                  };
                  const isCollapsed = collapsedGroups.has(priority);
                  return (
                    <div key={priority} className="mb-3">
                      <div
                        className={`text-xs font-medium ${priorityColors[priority]} border-b pb-1 mb-2 flex items-center justify-between cursor-pointer hover:opacity-80`}
                        onClick={() => toggleGroupCollapse(priority)}
                      >
                        <div className="flex items-center gap-1">
                          {isCollapsed ? (
                            <ChevronRight size={12} />
                          ) : (
                            <ChevronDown size={12} />
                          )}
                          {priorityLabels[priority]} ({groupTasks.length})
                        </div>
                      </div>
                      {!isCollapsed && (
                      <div className="space-y-1">
                        {groupTasks.map(task => (
                          <TaskItem
                            key={task.id}
                            task={task}
                            agents={agents}
                            selected={selectedTasks.has(task.id)}
                            onSelect={() => toggleTaskSelection(task.id)}
                            onStart={() => onStartTask(task.id)}
                            onDelete={() => onDeleteTasks([task.id])}
                            onComplete={() => onCompleteTasks([task.id])}
                            onDuplicate={() => onDuplicateTask(task.id)}
                            onUpdatePriority={(priority) => _onUpdateTaskPriority(task.id, priority)}
                            onUpdateTags={(tags) => onUpdateTaskTags(task.id, tags)}
                            onShowComments={() => {
                              setSelectedTaskForComments(task);
                              setShowComments(true);
                            }}
                            customTags={customTags}
                            getAgentName={getAgentName}
                            getStatusIcon={getStatusIcon}
                            getTaskDuration={getTaskDuration}
                            formatDuration={formatDuration}
                            isDragging={draggedTaskId === task.id}
                            isDragOver={dragOverTaskId === task.id}
                            dragPosition={dragPosition}
                            isDropSuccess={dropSuccessId === task.id}
                            isFocused={focusedTaskIndex >= 0 && filteredByStatus[focusedTaskIndex]?.id === task.id}
                            onDragStart={(e) => handleDragStart(e, task.id)}
                            onDragOver={(e) => handleDragOver(e, task.id)}
                            onDragLeave={handleDragLeave}
                            onDrop={(e) => handleDrop(e, task.id)}
                            onDragEnd={handleDragEnd}
                            subtasksExpanded={expandedSubtasks.has(task.id)}
                            onToggleSubtasks={() => toggleSubtasksExpanded(task.id)}
                            onAddSubtask={(_title) => handleAddSubtask(task.id)}
                            onToggleSubtask={(subtaskId) => handleToggleSubtask(task.id, subtaskId)}
                            onDeleteSubtask={(subtaskId) => handleDeleteSubtask(task.id, subtaskId)}
                            addingSubtask={addingSubtaskTo === task.id}
                            onStartAddSubtask={() => { setAddingSubtaskTo(task.id); setNewSubtaskTitle(''); }}
                            onCancelAddSubtask={() => { setAddingSubtaskTo(null); setNewSubtaskTitle(''); }}
                            newSubtaskTitle={newSubtaskTitle}
                            onNewSubtaskTitleChange={setNewSubtaskTitle}
                            allTasks={tasks}
                            onSaveAsTemplate={() => handleSaveAsTemplate(task)}
                            onArchive={onArchiveTask ? (archived) => onArchiveTask(task.id, archived) : undefined}
                          />
                        ))}
                      </div>
                      )}
                    </div>
                  );
                })}
              </>
            ) : (
              filteredByStatus.map(task => (
                <TaskItem
                  key={task.id}
                  task={task}
                  agents={agents}
                  selected={selectedTasks.has(task.id)}
                  onSelect={() => toggleTaskSelection(task.id)}
                  onStart={() => onStartTask(task.id)}
                  onDelete={() => onDeleteTasks([task.id])}
                  onComplete={() => onCompleteTasks([task.id])}
                  onDuplicate={() => onDuplicateTask(task.id)}
                  onUpdatePriority={(priority) => _onUpdateTaskPriority(task.id, priority)}
                  onUpdateTags={(tags) => onUpdateTaskTags(task.id, tags)}
                  onShowComments={() => {
                    setSelectedTaskForComments(task);
                    setShowComments(true);
                  }}
                  customTags={customTags}
                  getAgentName={getAgentName}
                  getStatusIcon={getStatusIcon}
                  getTaskDuration={getTaskDuration}
                  formatDuration={formatDuration}
                  isDragging={draggedTaskId === task.id}
                  isDragOver={dragOverTaskId === task.id}
                  dragPosition={dragPosition}
                  isDropSuccess={dropSuccessId === task.id}
                  isFocused={focusedTaskIndex >= 0 && filteredByStatus[focusedTaskIndex]?.id === task.id}
                  onDragStart={(e) => handleDragStart(e, task.id)}
                  onDragOver={(e) => handleDragOver(e, task.id)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, task.id)}
                  onDragEnd={handleDragEnd}
                  subtasksExpanded={expandedSubtasks.has(task.id)}
                  onToggleSubtasks={() => toggleSubtasksExpanded(task.id)}
                  onAddSubtask={(_title) => handleAddSubtask(task.id)}
                  onToggleSubtask={(subtaskId) => handleToggleSubtask(task.id, subtaskId)}
                  onDeleteSubtask={(subtaskId) => handleDeleteSubtask(task.id, subtaskId)}
                  addingSubtask={addingSubtaskTo === task.id}
                  onStartAddSubtask={() => { setAddingSubtaskTo(task.id); setNewSubtaskTitle(''); }}
                  onCancelAddSubtask={() => { setAddingSubtaskTo(null); setNewSubtaskTitle(''); }}
                  newSubtaskTitle={newSubtaskTitle}
                  onNewSubtaskTitleChange={setNewSubtaskTitle}
                  allTasks={tasks}
                  onSaveAsTemplate={() => handleSaveAsTemplate(task)}
                  onArchive={onArchiveTask ? (archived) => onArchiveTask(task.id, archived) : undefined}
                />
              ))
            )}
          </div>

          {/* Batch Edit Modal */}
          {showBatchEditModal && onBatchEditTasks && (
            <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-30">
              <div className="bg-gray-800 rounded-lg p-4 w-[260px] mx-4 max-h-[90%] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white text-lg font-bold flex items-center gap-2">
                    <Edit3 size={16} className="text-blue-400" />
                    Batch Edit
                  </h3>
                  <button
                    onClick={() => setShowBatchEditModal(false)}
                    className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  >
                    <X size={16} />
                  </button>
                </div>
                <p className="text-xs text-gray-400 mb-3">
                  Editing {selectedTasks.size} selected tasks
                </p>
                <div className="space-y-3">
                  {/* Description */}
                  <div>
                    <label className="text-gray-400 text-xs block mb-1 flex items-center gap-1">
                      <Edit3 size={10} />
                      Description (optional)
                    </label>
                    <textarea
                      value={batchEditDescription}
                      onChange={(e) => setBatchEditDescription(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm resize-none"
                      placeholder="Set description for all selected tasks..."
                      rows={3}
                    />
                  </div>
                  {/* Due Date */}
                  <div>
                    <label className="text-gray-400 text-xs block mb-1 flex items-center gap-1">
                      <CalendarDays size={10} />
                      Due Date (optional)
                    </label>
                    <input
                      type="date"
                      value={batchEditDueDate}
                      onChange={(e) => setBatchEditDueDate(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
                    />
                  </div>
                  {/* Agent Assignment */}
                  <div>
                    <label className="text-gray-400 text-xs block mb-1 flex items-center gap-1">
                      <User size={10} />
                      Assign to Agent (optional)
                    </label>
                    <select
                      value={batchEditAgentId}
                      onChange={(e) => setBatchEditAgentId(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
                    >
                      <option value="">Keep current assignment</option>
                      {agents.map((agent) => (
                        <option key={agent.id} value={agent.id}>
                          {agent.name} ({getAgentDisplayType(agent)})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => {
                      setShowBatchEditModal(false);
                      setBatchEditDescription('');
                      setBatchEditDueDate('');
                      setBatchEditAgentId('');
                    }}
                    className="flex-1 px-3 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={async () => {
                      const updates: { description?: string; due_date?: string; agent_id?: string } = {};
                      if (batchEditDescription.trim()) updates.description = batchEditDescription.trim();
                      if (batchEditDueDate) updates.due_date = batchEditDueDate;
                      if (batchEditAgentId) updates.agent_id = batchEditAgentId;

                      if (Object.keys(updates).length > 0) {
                        await onBatchEditTasks(Array.from(selectedTasks), updates);
                        setSelectedTasks(new Set());
                        setShowBatchEditModal(false);
                        setBatchEditDescription('');
                        setBatchEditDueDate('');
                        setBatchEditAgentId('');
                      }
                    }}
                    disabled={!batchEditDescription.trim() && !batchEditDueDate && !batchEditAgentId}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                  >
                    Apply Changes
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Create Task Modal - positioned within the panel */}
          {showCreateModal && (
            <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-30">
              <div className="bg-gray-800 rounded-lg p-6 w-[280px] mx-4 max-h-[90%] overflow-y-auto">
                <h3 className="text-white text-lg font-bold mb-4">Create New Task</h3>

                <div className="space-y-4">
                  {/* Template selector */}
                  <div>
                    <label className="text-gray-400 text-sm block mb-1 flex items-center gap-1">
                      <Sparkles size={12} className="text-yellow-400" />
                      Quick Templates
                    </label>
                    <select
                      onChange={(e) => handleSelectTemplate(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
                      value=""
                    >
                      <option value="">Choose a template...</option>
                      {templates.map(template => (
                        <option key={template.id} value={template.id}>
                          {template.name} ({template.priority.toUpperCase()})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="border-t border-gray-700 pt-3">
                    <label className="text-gray-400 text-sm block mb-1">Title</label>
                    <input
                      type="text"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="Task title..."
                    />
                  </div>

                  <div>
                    <label className="text-gray-400 text-sm block mb-1">Description</label>
                    <textarea
                      value={newTaskDescription}
                      onChange={(e) => setNewTaskDescription(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                      placeholder="Task description..."
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="text-gray-400 text-sm block mb-1">Priority</label>
                    <div className="flex gap-1">
                      {(['p0', 'p1', 'p2', 'p3'] as const).map(p => (
                        <button
                          key={p}
                          onClick={() => setNewTaskPriority(p)}
                          className={`flex-1 py-1.5 text-xs rounded transition-colors ${
                            newTaskPriority === p
                              ? p === 'p0' ? 'bg-red-600 text-white' :
                                p === 'p1' ? 'bg-orange-600 text-white' :
                                p === 'p2' ? 'bg-yellow-600 text-white' :
                                'bg-blue-600 text-white'
                              : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                          }`}
                        >
                          {p.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-gray-400 text-sm block mb-1 flex items-center gap-1">
                      <Clock size={12} />
                      Estimated Time (hours)
                    </label>
                    <input
                      type="number"
                      value={newTaskEstimatedHours}
                      onChange={(e) => setNewTaskEstimatedHours(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="e.g., 2.5"
                      min="0"
                      step="0.5"
                    />
                  </div>

                  <div>
                    <label className="text-gray-400 text-sm block mb-1">Assign to Agent</label>
                    <select
                      value={selectedAgentId}
                      onChange={(e) => setSelectedAgentId(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="">Select an agent...</option>
                      {agents.map((agent) => (
                        <option key={agent.id} value={agent.id}>
                          {agent.name} ({getAgentDisplayType(agent)})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreate}
                    disabled={!newTaskTitle.trim()}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Create
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Undo Delete Toast */}
        {recentlyDeleted.length > 0 && (
          <div className="absolute bottom-12 left-2 right-2 z-30">
            <div className="bg-orange-600/90 backdrop-blur rounded-lg p-2 flex items-center justify-between shadow-lg">
              <div className="flex items-center gap-2">
                <Trash2 size={14} className="text-white" />
                <span className="text-white text-xs">
                  {recentlyDeleted.length} task{recentlyDeleted.length > 1 ? 's' : ''} deleted
                </span>
              </div>
              <button
                onClick={() => {
                  recentlyDeleted.forEach(d => handleUndoDelete(d.task.id));
                }}
                className="px-2 py-1 bg-white/20 hover:bg-white/30 rounded text-white text-xs font-medium transition-colors"
              >
                Undo
              </button>
            </div>
          </div>
        )}

        {/* Keyboard Shortcuts Hint Bar */}
        <div className="border-t border-gray-700 px-2 py-1.5 bg-gray-800/50">
          <div className="flex items-center justify-center gap-3 text-[9px] text-gray-500">
            <div className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-300 font-mono">Space</kbd>
              <span>Select</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-300 font-mono">Enter</kbd>
              <span>Start</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-300 font-mono">Del</kbd>
              <span>Delete</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-300 font-mono">?</kbd>
              <span>Help</span>
            </div>
          </div>
        </div>
      </div>

      {/* Task Comment Panel */}
      {showComments && selectedTaskForComments && (
        <TaskCommentPanel
          task={selectedTaskForComments}
          agents={agents}
          onClose={() => {
            setShowComments(false);
            setSelectedTaskForComments(null);
          }}
          onAddComment={onAddComment}
          onEditComment={onEditComment}
          onDeleteComment={onDeleteComment}
        />
      )}

      {/* Template Manager Panel */}
      {showTemplateManager && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-30">
          <div className="bg-gray-800 rounded-lg p-4 w-[320px] max-h-[80%] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Bookmark size={16} className="text-blue-400" />
                <h3 className="text-white text-sm font-bold">模板管理</h3>
              </div>
              <button
                onClick={() => setShowTemplateManager(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>

            {/* Save as Template Dialog */}
            {savingTaskAsTemplate && (
              <div className="mb-4 p-3 bg-blue-900/30 rounded-lg border border-blue-500/50">
                <p className="text-xs text-blue-300 mb-2">保存任务为模板</p>
                <input
                  type="text"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="模板名称"
                  className="w-full px-2 py-1 bg-gray-700 text-white text-sm rounded border border-gray-600 focus:border-blue-500 focus:outline-none mb-2"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      const task = tasks.find(t => t.id === savingTaskAsTemplate);
                      if (task) confirmSaveAsTemplate(task);
                      setSavingTaskAsTemplate(null);
                      setNewTemplateName('');
                    }}
                    className="flex-1 px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-500"
                  >
                    保存
                  </button>
                  <button
                    onClick={() => { setSavingTaskAsTemplate(null); setNewTemplateName(''); }}
                    className="flex-1 px-2 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-500"
                  >
                    取消
                  </button>
                </div>
              </div>
            )}

            {/* Templates List */}
            {templates.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Bookmark size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">暂无模板</p>
                <p className="text-xs">点击任务上的书签按钮保存为模板</p>
              </div>
            ) : (
              <div className="space-y-2">
                {templates.map(template => (
                  <div
                    key={template.id}
                    className="bg-gray-700/50 rounded-lg p-3"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-white text-sm font-medium truncate">{template.name}</h4>
                        <p className="text-gray-400 text-xs truncate">{template.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs ${PRIORITY_COLORS[template.priority].text}`}>
                            {PRIORITY_COLORS[template.priority].label}
                          </span>
                          {template.dueDays && (
                            <span className="text-xs text-gray-500">{template.dueDays}天后到期</span>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteTemplate(template.id)}
                        className="p-1 text-gray-400 hover:text-red-400 rounded"
                        title="删除模板"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// Task Item Component
interface TaskItemProps {
  task: Task;
  agents: any[];
  selected: boolean;
  onSelect: () => void;
  onStart: () => void;
  onDelete: () => void;
  onComplete: () => void;
  onDuplicate: () => void;
  onUpdatePriority: (priority: TaskPriority) => void;
  onUpdateTags: (tags: string[]) => void;
  onShowComments: () => void;
  customTags: TaskTag[];
  getAgentName: (id?: string) => string;
  getStatusIcon: (status: Task['status']) => React.ReactNode;
  getTaskDuration: (task: Task) => number | null;
  formatDuration: (seconds: number) => string;
  // Archive props
  onArchive?: (archived: boolean) => void;
  // Focus props
  isFocused?: boolean;
  // Drag and drop props
  isDragging?: boolean;
  isDragOver?: boolean;
  dragPosition?: 'before' | 'after';
  isDropSuccess?: boolean;
  onDragStart?: (e: React.DragEvent) => void;
  onDragOver?: (e: React.DragEvent) => void;
  onDragLeave?: () => void;
  onDrop?: (e: React.DragEvent) => void;
  onDragEnd?: () => void;
  // Subtask props
  subtasksExpanded?: boolean;
  onToggleSubtasks?: () => void;
  onAddSubtask?: (title: string) => void;
  onToggleSubtask?: (subtaskId: string) => void;
  onDeleteSubtask?: (subtaskId: string) => void;
  addingSubtask?: boolean;
  onStartAddSubtask?: () => void;
  onCancelAddSubtask?: () => void;
  newSubtaskTitle?: string;
  onNewSubtaskTitleChange?: (title: string) => void;
  // Dependency props
  allTasks?: Task[];
  // Template props
  onSaveAsTemplate?: () => void;
}

// Skeleton component for loading state
function TaskItemSkeleton() {
  return (
    <div className="p-2 rounded-lg bg-gray-700/50 animate-pulse">
      <div className="flex items-start gap-2">
        {/* Checkbox skeleton */}
        <div className="w-3 h-3 rounded bg-gray-600 mt-1" />
        {/* Status icon skeleton */}
        <div className="w-3.5 h-3.5 rounded-full bg-gray-600 mt-0.5" />
        <div className="flex-1 min-w-0">
          {/* Title skeleton */}
          <div className="h-4 bg-gray-600 rounded w-3/4 mb-2" />
          <div className="flex items-center gap-2">
            {/* Priority skeleton */}
            <div className="h-3 bg-gray-600 rounded w-8" />
            {/* Tags skeleton */}
            <div className="h-3 bg-gray-600 rounded w-12" />
          </div>
        </div>
      </div>
    </div>
  );
}

function TaskItem({
  task,
  agents: _agents,
  selected,
  onSelect,
  onStart,
  onDelete,
  onComplete,
  onDuplicate,
  onUpdatePriority,
  onUpdateTags,
  onShowComments,
  customTags,
  getAgentName,
  getStatusIcon,
  getTaskDuration,
  formatDuration,
  onArchive,
  isFocused = false,
  isDragging = false,
  isDragOver = false,
  dragPosition = 'after',
  isDropSuccess = false,
  onDragStart,
  onDragOver,
  onDragLeave,
  onDrop,
  onDragEnd,
  // Subtask props
  subtasksExpanded = false,
  onToggleSubtasks,
  onAddSubtask,
  onToggleSubtask,
  onDeleteSubtask,
  addingSubtask = false,
  onStartAddSubtask,
  onCancelAddSubtask,
  newSubtaskTitle = '',
  onNewSubtaskTitleChange,
  // Dependency props
  allTasks = [],
  // Template props
  onSaveAsTemplate,
}: TaskItemProps) {
  const duration = getTaskDuration(task);
  const [showPriorityMenu, setShowPriorityMenu] = useState(false);
  const [showTagMenu, setShowTagMenu] = useState(false);
  const [liveTimer, setLiveTimer] = useState<number | null>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isDoubleClicked, setIsDoubleClicked] = useState(false);

  // Handle double-click with visual feedback
  const handleDoubleClick = () => {
    setIsDoubleClicked(true);
    setTimeout(() => setIsDoubleClicked(false), 200);

    // Different actions based on task status
    if (task.status === 'pending' && task.agent_id) {
      onStart();
    } else if (task.status === 'running') {
      onShowComments();
    } else if (task.status === 'completed' || task.status === 'failed') {
      onShowComments();
    }
  };

  // Live timer for running tasks
  useEffect(() => {
    if (task.status === 'running' && task.started_at) {
      const updateTimer = () => {
        const start = new Date(task.started_at!).getTime();
        const now = Date.now();
        setLiveTimer(Math.floor((now - start) / 1000));
      };
      updateTimer();
      const interval = setInterval(updateTimer, 1000);
      return () => clearInterval(interval);
    } else {
      setLiveTimer(null);
    }
  }, [task.status, task.started_at]);

  // Format timestamp to readable time
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };

  // Toggle tag on task
  const toggleTag = (tagId: string) => {
    const currentTags = task.tags || [];
    if (currentTags.includes(tagId)) {
      onUpdateTags(currentTags.filter(t => t !== tagId));
    } else {
      onUpdateTags([...currentTags, tagId]);
    }
  };

  // Get priority border color
  const getPriorityBorderColor = () => {
    if (!task.priority) return '';
    switch (task.priority) {
      case 'p0': return 'border-l-4 border-l-red-500';
      case 'p1': return 'border-l-4 border-l-orange-500';
      case 'p2': return 'border-l-4 border-l-yellow-500';
      case 'p3': return 'border-l-4 border-l-blue-500';
      default: return '';
    }
  };

  // Calculate due date status
  const getDueDateStatus = (): { status: 'overdue' | 'today' | 'soon' | 'ok' | 'none'; remaining: string; color: string } => {
    if (!task.due_date || task.status === 'completed') {
      return { status: 'none', remaining: '', color: '' };
    }
    const now = new Date();
    const dueDate = new Date(task.due_date);
    const diffMs = dueDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.ceil(diffMs / (1000 * 60 * 60));

    if (diffMs < 0) {
      const daysLate = Math.abs(diffDays);
      return {
        status: 'overdue',
        remaining: `Overdue ${daysLate}d`,
        color: 'text-red-400'
      };
    } else if (diffHours <= 24) {
      return {
        status: 'today',
        remaining: diffHours <= 1 ? 'Due now!' : `Due today`,
        color: 'text-orange-400'
      };
    } else if (diffDays <= 3) {
      return {
        status: 'soon',
        remaining: `${diffDays}d left`,
        color: 'text-yellow-400'
      };
    } else {
      return {
        status: 'ok',
        remaining: `${diffDays}d left`,
        color: 'text-gray-400'
      };
    }
  };

  const dueDateStatus = getDueDateStatus();

  // Get due date border glow effect
  const getDueDateBorderGlow = (): string => {
    if (dueDateStatus.status === 'overdue') return 'ring-1 ring-red-500/50';
    if (dueDateStatus.status === 'today') return 'ring-1 ring-orange-500/50';
    if (dueDateStatus.status === 'soon') return 'ring-1 ring-yellow-500/30';
    return '';
  };

  // Close priority menu when clicking outside
  useEffect(() => {
    const handleClick = () => setShowPriorityMenu(false);
    if (showPriorityMenu) {
      setTimeout(() => document.addEventListener('click', handleClick), 0);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [showPriorityMenu]);

  // Close tag menu when clicking outside
  useEffect(() => {
    const handleClick = () => setShowTagMenu(false);
    if (showTagMenu) {
      setTimeout(() => document.addEventListener('click', handleClick), 0);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [showTagMenu]);

  return (
    <div
      data-task-id={task.id}
      draggable={!!onDragStart}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onDragEnd={onDragEnd}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`p-2 rounded-lg transition-all cursor-pointer relative ${
        selected ? 'bg-blue-600/30 ring-1 ring-blue-500' : 'bg-gray-700/50 hover:bg-gray-700'
      } ${isFocused ? 'ring-2 ring-yellow-400 bg-yellow-500/10' : ''
      } ${isDragging ? 'opacity-40 scale-[0.98] rotate-1' : ''} ${
        isDropSuccess ? 'scale-[1.02] bg-green-600/30 ring-2 ring-green-400' : ''
      } ${
        isDoubleClicked ? 'scale-[1.02] bg-blue-600/40' : ''
      } ${
        isDragOver && dragPosition === 'before' ? 'border-t-2 border-purple-400 shadow-[0_-4px_8px_rgba(168,85,247,0.3)]' : ''
      } ${isDragOver && dragPosition === 'after' ? 'border-b-2 border-purple-400 shadow-[0_4px_8px_rgba(168,85,247,0.3)]' : ''
      } ${getPriorityBorderColor()} ${getDueDateBorderGlow()}`}
      onDoubleClick={handleDoubleClick}
      title={`Double-click: ${task.status === 'pending' ? 'Start task' : task.status === 'running' ? 'View progress' : 'View details'}`}
    >
      {/* Keyboard shortcut hint on hover */}
      {isHovered && (
        <div className="absolute top-1 right-1 flex items-center gap-0.5 opacity-60">
          <kbd className="px-0.5 py-0 bg-gray-600 rounded text-[7px] text-gray-300">⏎</kbd>
        </div>
      )}
      <div className="flex items-start gap-2">
        {/* Drag handle */}
        {onDragStart && (
          <div
            className="cursor-grab active:cursor-grabbing text-gray-500 hover:text-gray-300 mt-0.5"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <GripVertical size={14} />
          </div>
        )}
        {/* Selection checkbox */}
        <input
          type="checkbox"
          checked={selected}
          onChange={onSelect}
          className="mt-1 w-3 h-3 rounded border-gray-500 bg-gray-700 text-blue-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
          onClick={(e) => e.stopPropagation()}
        />
        <div className="mt-0.5">{getStatusIcon(task.status)}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="text-white text-sm font-medium truncate flex-1">{task.title}</span>
            {/* Due date warning indicator */}
            {dueDateStatus.status !== 'none' && (
              <div className={`flex items-center gap-0.5 text-[9px] ${dueDateStatus.color}`}
                title={`Due: ${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'N/A'}`}
              >
                {dueDateStatus.status === 'overdue' && <AlertTriangle size={10} />}
                {dueDateStatus.status === 'today' && <Clock size={10} />}
                <span>{dueDateStatus.remaining}</span>
              </div>
            )}
            {/* Priority indicator and selector */}
            <div className="relative">
              <button
                onClick={(e) => { e.stopPropagation(); setShowPriorityMenu(!showPriorityMenu); }}
                className={`p-0.5 rounded hover:bg-gray-600 transition-colors ${
                  task.priority ? '' : 'opacity-40 hover:opacity-100'
                }`}
                title="设置优先级"
              >
                <Flag size={10} className={
                  task.priority === 'p0' ? 'text-red-400' :
                  task.priority === 'p1' ? 'text-orange-400' :
                  task.priority === 'p2' ? 'text-yellow-400' :
                  task.priority === 'p3' ? 'text-blue-400' : 'text-gray-400'
                } />
              </button>
              {/* Priority dropdown menu */}
              {showPriorityMenu && (
                <div className="absolute top-full right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-20 min-w-[100px]">
                  <div className="p-1">
                    {(['p0', 'p1', 'p2', 'p3'] as TaskPriority[]).map(p => (
                      <button
                        key={p}
                        onClick={(e) => {
                          e.stopPropagation();
                          onUpdatePriority(p);
                          setShowPriorityMenu(false);
                        }}
                        className={`w-full text-left px-2 py-1 text-xs rounded flex items-center gap-1.5 ${
                          task.priority === p ? 'bg-blue-600/30 text-white' : 'text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        <Flag size={10} className={
                          p === 'p0' ? 'text-red-400' :
                          p === 'p1' ? 'text-orange-400' :
                          p === 'p2' ? 'text-yellow-400' : 'text-blue-400'
                        } />
                        <span>{PRIORITY_COLORS[p].label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            {/* Tag indicator and selector */}
            <div className="relative">
              <button
                onClick={(e) => { e.stopPropagation(); setShowTagMenu(!showTagMenu); }}
                className={`p-0.5 rounded hover:bg-gray-600 transition-colors ${
                  task.tags && task.tags.length > 0 ? '' : 'opacity-40 hover:opacity-100'
                }`}
                title="管理标签"
              >
                <Tag size={10} className={task.tags && task.tags.length > 0 ? 'text-purple-400' : 'text-gray-400'} />
              </button>
              {/* Tag dropdown menu */}
              {showTagMenu && (
                <div className="absolute top-full right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl z-20 min-w-[120px]">
                  <div className="p-1 border-b border-gray-700 text-[10px] text-gray-400 px-2">
                    选择标签
                  </div>
                  <div className="p-1 max-h-40 overflow-y-auto">
                    {customTags.map(tag => (
                      <button
                        key={tag.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleTag(tag.id);
                        }}
                        className={`w-full text-left px-2 py-1 text-xs rounded flex items-center gap-1.5 ${
                          task.tags?.includes(tag.id) ? 'bg-purple-600/30 text-white' : 'text-gray-300 hover:bg-gray-700'
                        }`}
                      >
                        <span
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: tag.color }}
                        />
                        <span className="flex-1">{tag.name}</span>
                        {task.tags?.includes(tag.id) && (
                          <X size={10} className="text-gray-400" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 text-gray-400 text-xs mt-0.5">
            <span>Agent: {getAgentName(task.agent_id)}</span>
            {/* Live timer for running tasks */}
            {task.status === 'running' && liveTimer !== null && (
              <span className="text-yellow-400 flex items-center gap-0.5">
                <Clock size={8} className="animate-pulse" />
                {formatDuration(liveTimer)}
              </span>
            )}
            {/* Duration for completed tasks */}
            {task.status !== 'running' && duration !== null && (
              <span className="text-blue-400">{formatDuration(duration)}</span>
            )}
          </div>

          {/* Time tracking info */}
          {(task.started_at || task.completed_at || task.estimated_hours) && (
            <div className="flex items-center gap-2 text-gray-500 text-[10px] mt-0.5 flex-wrap">
              {task.estimated_hours && (
                <span className="flex items-center gap-0.5 text-purple-400">
                  <Timer size={8} />
                  Est: {task.estimated_hours}h
                </span>
              )}
              {task.started_at && (
                <span className="flex items-center gap-0.5">
                  <Clock size={8} />
                  开始: {formatTime(task.started_at)}
                </span>
              )}
              {task.completed_at && (
                <span className="flex items-center gap-0.5">
                  完成: {formatTime(task.completed_at)}
                </span>
              )}
              {/* Actual vs Estimated comparison */}
              {task.completed_at && task.started_at && task.estimated_hours && (
                <span className={`flex items-center gap-0.5 ${
                  (() => {
                    const actualMs = new Date(task.completed_at).getTime() - new Date(task.started_at).getTime();
                    const actualHours = actualMs / (1000 * 60 * 60);
                    const ratio = actualHours / task.estimated_hours;
                    return ratio > 1.5 ? 'text-red-400' : ratio > 1 ? 'text-yellow-400' : 'text-green-400';
                  })()
                }`}>
                  {(() => {
                    const actualMs = new Date(task.completed_at).getTime() - new Date(task.started_at).getTime();
                    const actualHours = actualMs / (1000 * 60 * 60);
                    const ratio = actualHours / task.estimated_hours;
                    if (ratio > 1.5) return `⏰ ${actualHours.toFixed(1)}h (${Math.round((ratio - 1) * 100)}% over)`;
                    if (ratio > 1) return `⏱️ ${actualHours.toFixed(1)}h (${Math.round((ratio - 1) * 100)}% over)`;
                    return `✓ ${actualHours.toFixed(1)}h (on time)`;
                  })()}
                </span>
              )}
            </div>
          )}

          {/* Progress bar */}
          {(() => {
            // Calculate progress percentage
            let progressPercent = 0;
            if (typeof task.progress === 'number' && task.progress > 0) {
              progressPercent = Math.min(100, task.progress);
            } else if (task.subtasks && task.subtasks.length > 0) {
              const completedSubtasks = task.subtasks.filter(st => st.completed).length;
              progressPercent = Math.round((completedSubtasks / task.subtasks.length) * 100);
            }
            return progressPercent > 0 && progressPercent < 100 ? (
              <div className="mt-2">
                <div className="flex items-center justify-between text-[10px] mb-1">
                  <span className="text-gray-400">Progress</span>
                  <span className="text-gray-300">{progressPercent}%</span>
                </div>
                <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${progressPercent}%`,
                      backgroundColor: progressPercent >= 80 ? '#22c55e' : progressPercent >= 50 ? '#3b82f6' : '#6366f1'
                    }}
                  />
                </div>
              </div>
            ) : null;
          })()}

          {/* Dependencies display */}
          {task.dependencies && task.dependencies.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {task.dependencies.map(depId => {
                const depTask = allTasks?.find(t => t.id === depId);
                const isCompleted = depTask?.status === 'completed';
                const isBlocked = depTask && depTask.status !== 'completed';
                return (
                  <div
                    key={depId}
                    className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] ${
                      isCompleted
                        ? 'bg-green-500/20 text-green-400'
                        : isBlocked
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-gray-600/50 text-gray-400'
                    }`}
                    title={depTask ? `${depTask.title} (${depTask.status})` : '未知任务'}
                  >
                    {isBlocked ? (
                      <AlertTriangle size={8} />
                    ) : (
                      <Link2 size={8} />
                    )}
                    <span className="max-w-[60px] truncate">
                      {depTask?.title || depId.slice(0, 6)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Progress bar */}
          {task.status === 'running' && (
            <div className="mt-1">
              <div className="w-full h-1 bg-gray-600 rounded-full overflow-hidden">
                <div
                  className="h-full bg-yellow-500 transition-all"
                  style={{ width: `${(task.progress || 0) * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Tags display */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {task.tags.map(tagId => {
                const tag = customTags.find(t => t.id === tagId);
                if (!tag) return null;
                return (
                  <span
                    key={tagId}
                    className="px-1.5 py-0.5 text-[9px] rounded-full text-white font-medium"
                    style={{ backgroundColor: tag.color }}
                  >
                    {tag.name}
                  </span>
                );
              })}
            </div>
          )}

          {/* Subtasks display */}
          {task.subtasks && task.subtasks.length > 0 && (
            <div className="mt-1.5">
              <button
                onClick={(e) => { e.stopPropagation(); onToggleSubtasks?.(); }}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-white transition-colors"
              >
                {subtasksExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                <ListChecks size={10} />
                <span>{task.subtasks.filter(s => s.completed).length}/{task.subtasks.length} 子任务</span>
              </button>
              {subtasksExpanded && (
                <div className="mt-1 space-y-1 pl-4">
                  {task.subtasks.map(subtask => (
                    <div key={subtask.id} className="flex items-center gap-1.5 group">
                      <button
                        onClick={(e) => { e.stopPropagation(); onToggleSubtask?.(subtask.id); }}
                        className={`w-3.5 h-3.5 rounded border flex items-center justify-center transition-colors ${
                          subtask.completed
                            ? 'bg-green-500 border-green-500 text-white'
                            : 'border-gray-500 hover:border-gray-400'
                        }`}
                      >
                        {subtask.completed && <Check size={8} />}
                      </button>
                      <span className={`text-[10px] flex-1 ${subtask.completed ? 'text-gray-500 line-through' : 'text-gray-300'}`}>
                        {subtask.title}
                      </span>
                      <button
                        onClick={(e) => { e.stopPropagation(); onDeleteSubtask?.(subtask.id); }}
                        className="p-0.5 opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-all"
                      >
                        <X size={8} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Add subtask input */}
          {addingSubtask && (
            <div className="mt-1.5 flex items-center gap-1">
              <input
                type="text"
                value={newSubtaskTitle}
                onChange={(e) => onNewSubtaskTitleChange?.(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && newSubtaskTitle.trim()) {
                    onAddSubtask?.(newSubtaskTitle.trim());
                  }
                  if (e.key === 'Escape') {
                    onCancelAddSubtask?.();
                  }
                }}
                placeholder="输入子任务标题..."
                className="flex-1 px-2 py-1 text-[10px] bg-gray-700 text-white border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                autoFocus
                onClick={(e) => e.stopPropagation()}
              />
              <button
                onClick={(e) => { e.stopPropagation(); onAddSubtask?.(newSubtaskTitle.trim()); }}
                disabled={!newSubtaskTitle.trim()}
                className="p-1 bg-green-600 text-white rounded hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Check size={10} />
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); onCancelAddSubtask?.(); }}
                className="p-1 text-gray-400 hover:text-white"
              >
                <X size={10} />
              </button>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-1 mt-1.5">
            {task.status === 'pending' && task.agent_id && (
              <button
                onClick={(e) => { e.stopPropagation(); onStart(); }}
                className="px-2 py-0.5 bg-green-600 text-white text-[10px] rounded hover:bg-green-500 flex items-center gap-0.5"
              >
                <Play size={8} />
                Start
              </button>
            )}
            {task.status !== 'completed' && (
              <button
                onClick={(e) => { e.stopPropagation(); onComplete(); }}
                className="px-1.5 py-0.5 bg-gray-600 text-white text-[10px] rounded hover:bg-gray-500"
              >
                Done
              </button>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); onShowComments(); }}
              className={`p-0.5 rounded flex items-center gap-0.5 ${
                (task.comments?.length || 0) > 0
                  ? 'text-blue-400 hover:bg-blue-500/20'
                  : 'text-gray-500 hover:text-white hover:bg-gray-600'
              }`}
              title="评论"
            >
              <MessageCircle size={10} />
              {(task.comments?.length || 0) > 0 && (
                <span className="text-[9px]">{task.comments?.length}</span>
              )}
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onDuplicate(); }}
              className="p-0.5 text-gray-500 hover:text-white hover:bg-gray-600 rounded"
              title="Duplicate"
            >
              <Copy size={10} />
            </button>
            {onSaveAsTemplate && (
              <button
                onClick={(e) => { e.stopPropagation(); onSaveAsTemplate(); }}
                className="p-0.5 text-gray-500 hover:text-blue-400 hover:bg-gray-600 rounded"
                title="Save as Template"
              >
                <Bookmark size={10} />
              </button>
            )}
            {onArchive && (
              <button
                onClick={(e) => { e.stopPropagation(); onArchive(!task.archived); }}
                className={`p-0.5 rounded ${task.archived ? 'text-purple-400 hover:text-purple-300' : 'text-gray-500 hover:text-purple-400'} hover:bg-gray-600`}
                title={task.archived ? 'Restore from archive' : 'Archive task'}
              >
                {task.archived ? <ArchiveRestore size={10} /> : <Archive size={10} />}
              </button>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(); }}
              className="p-0.5 text-gray-500 hover:text-red-400 hover:bg-gray-600 rounded"
              title="Delete"
            >
              <Trash2 size={10} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onStartAddSubtask?.(); }}
              className="p-0.5 text-gray-500 hover:text-green-400 hover:bg-gray-600 rounded"
              title="添加子任务"
            >
              <Plus size={10} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
