import { useState, useEffect } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, AGENT_LABELS, getAgentDisplayType, type AgentType } from '../../types';
import { Plus, Users, X, Star } from 'lucide-react';

interface SidebarProps {
  onCreateAgent: (name: string, type: AgentType) => void;
}

export function Sidebar({ onCreateAgent }: SidebarProps) {
  const { agents, selectedAgentId, selectAgent, sidebarOpen, toggleSidebar, agentStats, fetchAgentStats } = useAgentStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentType, setNewAgentType] = useState<AgentType>('assistant');

  // Fetch stats when agents change or sidebar opens
  useEffect(() => {
    if (sidebarOpen && agents.length > 0) {
      agents.forEach(agent => fetchAgentStats(agent.id));
    }
  }, [agents, sidebarOpen, fetchAgentStats]);

  const handleCreate = () => {
    if (newAgentName.trim()) {
      onCreateAgent(newAgentName.trim(), newAgentType);
      setNewAgentName('');
      setShowCreateModal(false);
    }
  };

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={toggleSidebar}
        className="absolute left-2 top-2 z-20 p-2 bg-gray-800 rounded-lg text-white hover:bg-gray-700 transition-colors"
      >
        {sidebarOpen ? <X size={20} /> : <Users size={20} />}
      </button>

      {/* Sidebar */}
      <div
        className={`absolute left-0 top-0 h-full bg-gray-800/95 backdrop-blur transition-transform duration-300 z-10 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: '280px' }}
      >
        <div className="h-full flex flex-col p-4 pt-14 overflow-hidden">
          <h2 className="text-lg font-bold text-white mb-4">AITeam</h2>

          {/* Agent list */}
          <div className="flex-1 overflow-y-auto space-y-2">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">Agents ({agents.length})</span>
              <button
                onClick={() => setShowCreateModal(true)}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
              >
                <Plus size={16} className="text-white" />
              </button>
            </div>

            {agents.map((agent) => (
              <div
                key={agent.id}
                onClick={() => selectAgent(selectedAgentId === agent.id ? null : agent.id)}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedAgentId === agent.id
                    ? 'bg-gray-700 ring-2 ring-blue-500'
                    : 'bg-gray-700/50 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="relative">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: AGENT_COLORS[agent.type].primary }}
                    >
                      <span className="text-white text-xs font-bold">
                        {agent.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    {/* Level Badge */}
                    {agentStats[agent.id] && (
                      <div className="absolute -top-1 -right-1 bg-yellow-500 rounded-full w-4 h-4 flex items-center justify-center border-2 border-gray-800">
                        <span className="text-[10px] font-bold text-gray-900">
                          {agentStats[agent.id].level}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-white text-sm font-medium truncate">
                        {agent.name}
                      </div>
                      {/* Emotion State */}
                      {(() => {
                        const stats = agentStats[agent.id];
                        return stats?.emotion_state ? (
                          <span className="text-sm" title={stats.emotion_state.label}>
                            {stats.emotion_state.emoji}
                          </span>
                        ) : null;
                      })()}
                    </div>
                    <div className="text-gray-400 text-xs flex items-center gap-2">
                      <span>{getAgentDisplayType(agent)}</span>
                      <StatusDot status={agent.status} />
                    </div>
                    {/* XP Progress Bar */}
                    {agentStats[agent.id] && (
                      <div className="mt-2">
                        <div className="flex items-center gap-1 text-[10px] text-gray-400">
                          <Star size={10} className="text-yellow-500" />
                          <span className="text-yellow-400 font-medium">
                            Lv.{agentStats[agent.id].level}
                          </span>
                          <span className="text-gray-500">
                            {agentStats[agent.id].xp} / {agentStats[agent.id].xp_to_next_level} XP
                          </span>
                        </div>
                        <div className="mt-1 h-1.5 bg-gray-600 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-yellow-500 to-amber-400 rounded-full transition-all duration-300"
                            style={{
                              width: `${Math.min(
                                (agentStats[agent.id].xp / agentStats[agent.id].xp_to_next_level) * 100,
                                100
                              )}%`,
                            }}
                          />
                        </div>
                        {/* Score Display */}
                        <div className="flex items-center gap-2 mt-1.5 text-[10px]">
                          <span className="text-amber-400 font-bold flex items-center gap-0.5">
                            <span>Score:</span>
                            <span>{agentStats[agent.id].score ?? 0}</span>
                          </span>
                          <span className="text-gray-600">|</span>
                          <span className="text-blue-400 flex items-center gap-0.5">
                            <span>Msg:</span>
                            <span>{agentStats[agent.id].discussion_count ?? 0}</span>
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Create Agent Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-80">
            <h3 className="text-white text-lg font-bold mb-4">Create New Agent</h3>

            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm block mb-1">Name</label>
                <input
                  type="text"
                  value={newAgentName}
                  onChange={(e) => setNewAgentName(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none"
                  placeholder="Agent name..."
                />
              </div>

              <div>
                <label className="text-gray-400 text-sm block mb-2">Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {(['coder', 'analyst', 'assistant', 'tester', 'custom'] as AgentType[]).map((type) => (
                    <button
                      key={type}
                      onClick={() => setNewAgentType(type)}
                      className={`px-3 py-2 rounded text-sm transition-colors ${
                        newAgentType === type
                          ? 'text-white ring-2 ring-blue-500'
                          : 'text-gray-300 hover:bg-gray-700'
                      }`}
                      style={{
                        backgroundColor:
                          newAgentType === type
                            ? AGENT_COLORS[type].primary
                            : undefined,
                      }}
                    >
                      {AGENT_LABELS[type]}
                    </button>
                  ))}
                </div>
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
                disabled={!newAgentName.trim()}
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

function StatusDot({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    idle: 'bg-gray-400',
    working: 'bg-green-500 animate-pulse',
    waiting: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  return (
    <span className={`w-2 h-2 rounded-full ${colorMap[status] || 'bg-gray-400'}`} />
  );
}
