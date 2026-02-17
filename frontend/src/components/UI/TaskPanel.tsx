import { useState } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import type { Task, AgentType } from '../../types';
import { ClipboardList, Play, Plus, X, CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface TaskPanelProps {
  tasks: Task[];
  onCreateTask: (title: string, agentId?: string) => Promise<Task | null>;
  onStartTask: (taskId: string) => void;
}

export function TaskPanel({ tasks, onCreateTask, onStartTask }: TaskPanelProps) {
  const { agents, taskPanelOpen, toggleTaskPanel } = useAgentStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');

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
      {/* Toggle button */}
      <button
        onClick={toggleTaskPanel}
        className="absolute right-2 top-2 z-20 p-2 bg-gray-800 rounded-lg text-white hover:bg-gray-700 transition-colors"
      >
        {taskPanelOpen ? <X size={20} /> : <ClipboardList size={20} />}
      </button>

      {/* Task Panel */}
      <div
        className={`absolute right-0 top-0 h-full bg-gray-800/95 backdrop-blur transition-transform duration-300 z-10 ${
          taskPanelOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        style={{ width: '320px' }}
      >
        <div className="p-4 pt-14 h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Tasks</h2>
            <button
              onClick={() => setShowCreateModal(true)}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
            >
              <Plus size={16} className="text-white" />
            </button>
          </div>

          {/* Task list */}
          <div className="flex-1 overflow-y-auto space-y-2">
            {tasks.length === 0 ? (
              <div className="text-gray-400 text-sm text-center py-8">
                No tasks yet. Click + to create one.
              </div>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.id}
                  className="p-3 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-start gap-2">
                    <div className="mt-1">{getStatusIcon(task.status)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="text-white text-sm font-medium truncate">
                        {task.title}
                      </div>
                      <div className="text-gray-400 text-xs mt-1">
                        Agent: {getAgentName(task.agent_id)}
                      </div>

                      {/* Progress bar */}
                      {task.status === 'running' && (
                        <div className="mt-2">
                          <div className="w-full h-1.5 bg-gray-600 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-yellow-500 transition-all"
                              style={{ width: `${task.progress * 100}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Start button for pending tasks */}
                      {task.status === 'pending' && task.agent_id && (
                        <button
                          onClick={() => onStartTask(task.id)}
                          className="mt-2 px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-500 transition-colors flex items-center gap-1"
                        >
                          <Play size={12} />
                          Start
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Create Task Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96">
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
                      {agent.name} ({agent.type})
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
    </>
  );
}
