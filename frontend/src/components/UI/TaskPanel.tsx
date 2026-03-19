import { useState, useMemo } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { Task, TaskPriority, TaskStatus } from '../../types';
import { getAgentDisplayType } from '../../types';
import { ClipboardList, Play, Plus, X, CheckCircle, Clock, AlertCircle, Trash2, Copy, Download, ClipboardPaste, Flag, Layers } from 'lucide-react';

interface TaskPanelProps {
  tasks: Task[];
  onCreateTask: (title: string, agentId?: string) => Promise<Task | null>;
  onStartTask: (taskId: string) => void;
  onDeleteTasks: (taskIds: string[]) => void;
  onCompleteTasks: (taskIds: string[]) => void;
  onUpdateTaskPriority: (taskId: string, priority: TaskPriority) => void;
  onDuplicateTask: (taskId: string) => void;
  onBatchUpdatePriority: (ids: string[], priority: TaskPriority) => Promise<void>;
}

export function TaskPanel({ tasks, onCreateTask, onStartTask, onDeleteTasks, onCompleteTasks, onUpdateTaskPriority: _onUpdateTaskPriority, onDuplicateTask, onBatchUpdatePriority: _onBatchUpdatePriority }: TaskPanelProps) {
  const { agents, taskPanelOpen, toggleTaskPanel, sidebarOpen, pipelineHistoryOpen } = useAgentStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set());
  const [groupByPriority, setGroupByPriority] = useState(true);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');

  // Calculate position: stack horizontally after Agent Sidebar and Pipeline History
  const agentSidebarWidth = sidebarOpen ? 320 : 0;
  const pipelineHistoryWidth = pipelineHistoryOpen ? 280 : 0;
  const taskPanelLeft = agentSidebarWidth + pipelineHistoryWidth + 8;
  const taskPanelWidth = 280;
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');

  // Filter tasks by status first
  const filteredByStatus = useMemo(() => {
    if (statusFilter === 'all') return tasks;
    return tasks.filter(t => t.status === statusFilter);
  }, [tasks, statusFilter]);

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
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tasks-${new Date().toISOString().slice(0, 10)}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

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
  const handleBatchDelete = () => {
    if (selectedTasks.size > 0) {
      onDeleteTasks(Array.from(selectedTasks));
      setSelectedTasks(new Set());
    }
  };

  const handleBatchComplete = () => {
    if (selectedTasks.size > 0) {
      onCompleteTasks(Array.from(selectedTasks));
      setSelectedTasks(new Set());
    }
  };

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
              <button
                onClick={exportToMarkdown}
                className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
                title="Export to Markdown"
              >
                <Download size={14} />
              </button>
              <button
                onClick={() => setGroupByPriority(!groupByPriority)}
                className={`p-1 rounded transition-colors ${groupByPriority ? 'bg-blue-600 text-white' : 'hover:bg-gray-700 text-gray-400 hover:text-white'}`}
                title="Group by priority"
              >
                <Flag size={14} />
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="p-1 hover:bg-gray-700 rounded transition-colors text-white"
              >
                <Plus size={16} />
              </button>
            </div>
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
          </div>

          {/* Batch actions */}
          {selectedTasks.size > 0 && (
            <div className="flex items-center gap-1 mb-2 p-2 bg-blue-900/30 rounded-lg">
              <span className="text-xs text-blue-300 mr-2">{selectedTasks.size} selected</span>
              <button
                onClick={handleBatchComplete}
                className="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-500"
              >
                Complete
              </button>
              <button
                onClick={handleBatchDelete}
                className="px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-500"
              >
                Delete
              </button>
              <button
                onClick={() => setSelectedTasks(new Set())}
                className="px-2 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-500"
              >
                Clear
              </button>
            </div>
          )}

          {/* Task list with grouping */}
          <div className="flex-1 overflow-y-auto space-y-1">
            {tasks.length === 0 ? (
              <div className="text-gray-400 text-sm text-center py-8">
                No tasks yet. Click + to create one.
              </div>
            ) : filteredByStatus.length === 0 ? (
              <div className="text-gray-400 text-sm text-center py-8">
                No {statusFilter} tasks.
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
                  return (
                    <div key={priority} className="mb-3">
                      <div className={`text-xs font-medium ${priorityColors[priority]} border-b pb-1 mb-2`}>
                        {priorityLabels[priority]} ({groupTasks.length})
                      </div>
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
                            getAgentName={getAgentName}
                            getStatusIcon={getStatusIcon}
                            getTaskDuration={getTaskDuration}
                            formatDuration={formatDuration}
                          />
                        ))}
                      </div>
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
                  getAgentName={getAgentName}
                  getStatusIcon={getStatusIcon}
                  getTaskDuration={getTaskDuration}
                  formatDuration={formatDuration}
                />
              ))
            )}
          </div>

          {/* Create Task Modal - positioned within the panel */}
          {showCreateModal && (
            <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-30">
              <div className="bg-gray-800 rounded-lg p-6 w-[260px] mx-4">
                <h3 className="text-white text-lg font-bold mb-4">Create New Task</h3>

                <div className="space-y-4">
                  <div>
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
      </div>
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
  getAgentName: (id?: string) => string;
  getStatusIcon: (status: Task['status']) => React.ReactNode;
  getTaskDuration: (task: Task) => number | null;
  formatDuration: (seconds: number) => string;
}

function TaskItem({ task, selected, onSelect, onStart, onDelete, onComplete, onDuplicate, getAgentName, getStatusIcon, getTaskDuration, formatDuration }: TaskItemProps) {
  const duration = getTaskDuration(task);

  return (
    <div
      className={`p-2 rounded-lg transition-colors cursor-pointer ${
        selected ? 'bg-blue-600/30 ring-1 ring-blue-500' : 'bg-gray-700/50 hover:bg-gray-700'
      }`}
      onDoubleClick={() => task.status === 'pending' && task.agent_id && onStart()}
    >
      <div className="flex items-start gap-2">
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
            {task.priority && (
              <Flag size={10} className={
                task.priority === 'p0' ? 'text-red-400' :
                task.priority === 'p1' ? 'text-orange-400' :
                task.priority === 'p2' ? 'text-yellow-400' : 'text-blue-400'
              } />
            )}
          </div>
          <div className="flex items-center gap-2 text-gray-400 text-xs mt-0.5">
            <span>Agent: {getAgentName(task.agent_id)}</span>
            {duration !== null && (
              <span className="text-blue-400">{formatDuration(duration)}</span>
            )}
          </div>

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
              onClick={(e) => { e.stopPropagation(); onDuplicate(); }}
              className="p-0.5 text-gray-500 hover:text-white hover:bg-gray-600 rounded"
              title="Duplicate"
            >
              <Copy size={10} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(); }}
              className="p-0.5 text-gray-500 hover:text-red-400 hover:bg-gray-600 rounded"
              title="Delete"
            >
              <Trash2 size={10} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
