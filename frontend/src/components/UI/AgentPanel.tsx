import { useState } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { X, Trash2, Edit2, Check, Loader2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

export function AgentPanel() {
  const { agents, selectedAgentId, selectAgent, removeAgent, updateAgent } = useAgentStore();

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDisplayType, setEditDisplayType] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [saving, setSaving] = useState(false);

  if (!selectedAgent) return null;

  const handleDelete = async () => {
    try {
      await fetch(`${API_BASE}/api/agents/${selectedAgent.id}`, {
        method: 'DELETE',
      });
      removeAgent(selectedAgent.id);
    } catch (error) {
      console.error('Failed to delete agent:', error);
    }
  };

  const startEditing = () => {
    setEditName(selectedAgent.name);
    setEditDisplayType(selectedAgent.display_type || '');
    setEditDescription(selectedAgent.description || '');
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setEditName('');
    setEditDisplayType('');
    setEditDescription('');
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/agents/${selectedAgent.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editName || undefined,
          display_type: editDisplayType || null,
          description: editDescription || null,
        }),
      });

      if (res.ok) {
        const updatedAgent = await res.json();
        updateAgent(selectedAgent.id, updatedAgent);
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Failed to update agent:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800/95 backdrop-blur rounded-lg p-4 z-10 min-w-80 max-w-md">
      {isEditing ? (
        // Edit Mode
        <div className="space-y-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white font-bold">Edit Agent</h3>
            <div className="flex gap-1">
              <button
                onClick={cancelEditing}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                disabled={saving}
              >
                <X size={16} className="text-gray-400" />
              </button>
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">Name</label>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="Agent name"
            />
          </div>

          {/* Display Type */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">
              Display Type <span className="text-gray-500">(e.g., UI设计师, 前端工程师)</span>
            </label>
            <input
              type="text"
              value={editDisplayType}
              onChange={(e) => setEditDisplayType(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
              placeholder="Custom display name (optional)"
            />
            <p className="text-gray-500 text-xs mt-1">
              Base type: <span className="text-gray-400">{selectedAgent.type}</span>
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="text-gray-400 text-xs block mb-1">Description</label>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white text-sm border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
              rows={2}
              placeholder="Agent description (optional)"
            />
          </div>

          {/* Save Button */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={cancelEditing}
              className="flex-1 px-4 py-2 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors text-sm"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 transition-colors text-sm flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Check size={14} />
                  Save
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        // View Mode
        <>
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: AGENT_COLORS[selectedAgent.type].primary }}
              >
                <span className="text-white font-bold">
                  {selectedAgent.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h3 className="text-white font-bold">{selectedAgent.name}</h3>
                <p className="text-gray-400 text-sm">{getAgentDisplayType(selectedAgent)}</p>
              </div>
            </div>
            <div className="flex gap-1">
              <button
                onClick={startEditing}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                title="Edit agent"
              >
                <Edit2 size={16} className="text-gray-400" />
              </button>
              <button
                onClick={() => selectAgent(null)}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
              >
                <X size={16} className="text-gray-400" />
              </button>
              <button
                onClick={handleDelete}
                className="p-1 hover:bg-red-600 rounded transition-colors"
                title="Delete agent"
              >
                <Trash2 size={16} className="text-gray-400" />
              </button>
            </div>
          </div>

          {selectedAgent.description && (
            <p className="text-gray-300 text-sm mb-3">{selectedAgent.description}</p>
          )}

          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-400">Status:</span>
            <span
              className={`px-2 py-0.5 rounded ${
                selectedAgent.status === 'idle'
                  ? 'bg-gray-600 text-gray-300'
                  : selectedAgent.status === 'working'
                  ? 'bg-green-600/50 text-green-300'
                  : selectedAgent.status === 'error'
                  ? 'bg-red-600/50 text-red-300'
                  : 'bg-yellow-600/50 text-yellow-300'
              }`}
            >
              {selectedAgent.status}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
