import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { X, Trash2 } from 'lucide-react';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

export function AgentPanel() {
  const { agents, selectedAgentId, selectAgent, removeAgent } = useAgentStore();

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

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

  return (
    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800/95 backdrop-blur rounded-lg p-4 z-10 min-w-80">
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
            onClick={() => selectAgent(null)}
            className="p-1 hover:bg-gray-700 rounded transition-colors"
          >
            <X size={16} className="text-gray-400" />
          </button>
          <button
            onClick={handleDelete}
            className="p-1 hover:bg-red-600 rounded transition-colors"
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
    </div>
  );
}
