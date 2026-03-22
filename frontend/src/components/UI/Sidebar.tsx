import { useState, useEffect, useMemo, useRef } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { AGENT_COLORS, AGENT_LABELS, getAgentDisplayType, type AgentType, type Agent } from '../../types';
import { Plus, Users, X, Star, ChevronDown, MoreVertical, MessageSquare, Trash2, BarChart2, ClipboardList, Search, Filter, Copy, ExternalLink, Image } from 'lucide-react';
import { AgentCardSkeleton } from '../common/Skeleton';
import { Tooltip } from '../common/Tooltip';

interface SidebarProps {
  onCreateAgent: (name: string, type: AgentType, avatarUrl?: string) => void;
  onCreateTask?: (title: string, agentId?: string) => void;
  onDeleteAgent?: (agentId: string) => void;
  onStartChat?: (agentId: string) => void;
  isLoading?: boolean;
}

export function Sidebar({ onCreateAgent, onCreateTask, onDeleteAgent, onStartChat, isLoading = false }: SidebarProps) {
  const { agents, selectedAgentId, selectAgent, sidebarOpen, toggleSidebar, agentStats, fetchAgentStats, tasks } = useAgentStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentType, setNewAgentType] = useState<AgentType>('assistant');
  const [newAgentAvatarUrl, setNewAgentAvatarUrl] = useState('');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // Favorite agents - persisted to localStorage
  const [favoriteAgents, setFavoriteAgents] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem('aiteam_favorite_agents');
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  });

  // Persist favorites to localStorage
  useEffect(() => {
    localStorage.setItem('aiteam_favorite_agents', JSON.stringify([...favoriteAgents]));
  }, [favoriteAgents]);

  const toggleFavorite = (agentId: string) => {
    setFavoriteAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) {
        newSet.delete(agentId);
      } else {
        newSet.add(agentId);
      }
      return newSet;
    });
  };
  const [activeQuickMenu, setActiveQuickMenu] = useState<string | null>(null);
  const quickMenuRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut to focus search (/)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only trigger if sidebar is open and no other input is focused
      if (!sidebarOpen) return;
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      if (e.key === '/') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [sidebarOpen]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'workload'>('name');

  // Close quick menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (quickMenuRef.current && !quickMenuRef.current.contains(e.target as Node)) {
        setActiveQuickMenu(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Calculate agent workload (pending + running tasks)
  const getAgentWorkload = (agentId: string): number => {
    return tasks.filter(t => t.agent_id === agentId && (t.status === 'pending' || t.status === 'running')).length;
  };

  const handleQuickMenuToggle = (e: React.MouseEvent, agentId: string) => {
    e.stopPropagation();
    setActiveQuickMenu(activeQuickMenu === agentId ? null : agentId);
  };

  const handleCreateTask = (agent: Agent) => {
    const title = prompt('Enter task title for ' + agent.name + ':');
    if (title && onCreateTask) {
      onCreateTask(title, agent.id);
    }
    setActiveQuickMenu(null);
  };

  const handleStartChat = (agent: Agent) => {
    if (onStartChat) {
      onStartChat(agent.id);
    }
    setActiveQuickMenu(null);
  };

  const handleDeleteAgent = (agent: Agent) => {
    if (confirm(`Delete agent "${agent.name}"? This cannot be undone.`) && onDeleteAgent) {
      onDeleteAgent(agent.id);
    }
    setActiveQuickMenu(null);
  };

  // Copy agent ID to clipboard
  const handleCopyAgentId = async (agent: Agent) => {
    try {
      await navigator.clipboard.writeText(agent.id);
      // Show brief feedback (could use toast in future)
      setActiveQuickMenu(null);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Toggle stats expansion
  const [expandedStatsAgent, setExpandedStatsAgent] = useState<string | null>(null);

  const handleViewStats = (agent: Agent) => {
    setExpandedStatsAgent(expandedStatsAgent === agent.id ? null : agent.id);
    setActiveQuickMenu(null);
    fetchAgentStats(agent.id);
  };

  // Group agents by display_type (filter out invalid agents)
  const groupedAgents = useMemo(() => {
    const groups: Record<string, Agent[]> = {};

    // First, filter agents based on search and filters
    const filteredAgents = agents.filter(agent => {
      // Skip invalid agents (missing id or name)
      if (!agent || !agent.id || !agent.name) return false;

      // Search filter - check name matches
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!agent.name.toLowerCase().includes(query)) return false;
      }

      // Type filter
      if (typeFilter !== 'all') {
        const agentType = agent.type || 'assistant';
        if (agentType !== typeFilter) return false;
      }

      // Status filter
      if (statusFilter !== 'all') {
        const agentStatus = agent.status || 'idle';
        if (agentStatus !== statusFilter) return false;
      }

      return true;
    });

    // Then group by display type
    filteredAgents.forEach(agent => {
      const displayType = getAgentDisplayType(agent);
      if (!groups[displayType]) {
        groups[displayType] = [];
      }
      groups[displayType].push(agent);
    });

    // Sort agents within each group
    Object.keys(groups).forEach(groupName => {
      groups[groupName].sort((a, b) => {
        if (sortBy === 'name') {
          return a.name.localeCompare(b.name);
        } else if (sortBy === 'status') {
          const statusOrder = { working: 0, error: 1, idle: 2 };
          return (statusOrder[a.status as keyof typeof statusOrder] || 3) - (statusOrder[b.status as keyof typeof statusOrder] || 3);
        } else if (sortBy === 'workload') {
          return getAgentWorkload(b.id) - getAgentWorkload(a.id);
        }
        return 0;
      });
    });

    return groups;
  }, [agents, searchQuery, typeFilter, statusFilter, sortBy]);

  // Calculate filtered agent count
  const filteredCount = useMemo(() => {
    return Object.values(groupedAgents).flat().length;
  }, [groupedAgents]);

  // Initialize all groups as expanded by default
  useEffect(() => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      Object.keys(groupedAgents).forEach(groupName => {
        newSet.add(groupName);
      });
      return newSet;
    });
  }, [groupedAgents]);

  const toggleGroup = (groupName: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupName)) {
        newSet.delete(groupName);
      } else {
        newSet.add(groupName);
      }
      return newSet;
    });
  };

  // Fetch stats when agents change or sidebar opens
  useEffect(() => {
    if (sidebarOpen && agents.length > 0) {
      agents.forEach(agent => fetchAgentStats(agent.id));
    }
  }, [agents, sidebarOpen, fetchAgentStats]);

  const handleCreate = () => {
    if (newAgentName.trim()) {
      onCreateAgent(newAgentName.trim(), newAgentType, newAgentAvatarUrl.trim() || undefined);
      setNewAgentName('');
      setNewAgentAvatarUrl('');
      setShowCreateModal(false);
    }
  };

  return (
    <>
      {/* Toggle button - only shown when sidebar is closed */}
      {!sidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="absolute left-2 top-2 z-20 p-2 bg-gray-800 rounded-lg text-white hover:bg-gray-700 transition-colors"
        >
          <Users size={20} />
        </button>
      )}

      {/* Sidebar */}
      <div
        className={`absolute left-0 top-0 h-full bg-gray-800/95 backdrop-blur transition-transform duration-300 z-10 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: '320px' }}
      >
        {/* Close button - top right corner */}
        <button
          onClick={toggleSidebar}
          className="absolute top-3 right-3 z-20 p-2 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors"
        >
          <X size={18} />
        </button>

        <div className="h-full flex flex-col p-4 pt-12 overflow-hidden">
          <h2 className="text-lg font-bold text-white mb-4">AITeam</h2>

          {/* Workload Distribution Chart */}
          {agents.length > 0 && (
            <div className="mb-4 p-3 bg-gray-700/30 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-400">Workload Distribution</span>
                <span className="text-xs text-gray-500">{tasks.filter(t => t.status === 'running' || t.status === 'pending').length} active</span>
              </div>
              <div className="flex items-end gap-1 h-8">
                {agents.slice(0, 8).map((agent) => {
                  const workload = getAgentWorkload(agent.id);
                  const maxWorkload = Math.max(...agents.map(a => getAgentWorkload(a.id)), 1);
                  const height = (workload / maxWorkload) * 100;
                  const color = AGENT_COLORS[agent.type]?.primary || '#888';
                  return (
                    <div
                      key={agent.id}
                      className="flex-1 flex flex-col items-center justify-end h-full"
                      title={`${agent.name}: ${workload} tasks`}
                    >
                      <div
                        className="w-full rounded-t transition-all duration-300"
                        style={{
                          height: `${Math.max(height, 5)}%`,
                          backgroundColor: color,
                          opacity: workload > 0 ? 1 : 0.3,
                        }}
                      />
                      <span className="text-[8px] text-gray-500 mt-0.5 truncate w-full text-center">
                        {workload > 0 ? workload : ''}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Search and Filter Bar */}
          <div className="mb-4 space-y-2">
            {/* Search Input */}
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search agents... (/)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-8 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-white"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* Sort Controls */}
            <div className="flex items-center gap-1 mb-2">
              <span className="text-xs text-gray-500 mr-1">Sort:</span>
              {(['name', 'status', 'workload'] as const).map((sort) => (
                <button
                  key={sort}
                  onClick={() => setSortBy(sort)}
                  className={`px-2 py-1 rounded text-xs transition-colors ${
                    sortBy === sort
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-400 hover:text-white'
                  }`}
                >
                  {sort === 'name' ? '名称' : sort === 'status' ? '状态' : '负载'}
                </button>
              ))}
            </div>

            {/* Filter Toggle */}
            <div className="flex items-center justify-between">
              <Tooltip content={showFilters ? "Hide filters" : "Show filters"} position="top">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors ${
                    showFilters ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400 hover:text-white'
                  }`}
                >
                <Filter size={12} />
                <span>Filters</span>
              </button>
              </Tooltip>
              {(searchQuery || typeFilter !== 'all' || statusFilter !== 'all') && (
                <Tooltip content="Reset all filters" position="top">
                  <button
                    onClick={() => {
                      setSearchQuery('');
                      setTypeFilter('all');
                      setStatusFilter('all');
                    }}
                    className="text-xs text-gray-500 hover:text-white transition-colors"
                  >
                    Clear all
                  </button>
                </Tooltip>
              )}
            </div>

            {/* Filter Options */}
            {showFilters && (
              <div className="flex gap-2">
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="flex-1 px-2 py-1.5 bg-gray-700 border border-gray-600 rounded text-white text-xs focus:outline-none focus:border-blue-500"
                >
                  <option value="all">All Types</option>
                  <option value="coder">Coder</option>
                  <option value="analyst">Analyst</option>
                  <option value="assistant">Assistant</option>
                  <option value="tester">Tester</option>
                </select>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="flex-1 px-2 py-1.5 bg-gray-700 border border-gray-600 rounded text-white text-xs focus:outline-none focus:border-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="idle">Idle</option>
                  <option value="working">Working</option>
                  <option value="waiting">Waiting</option>
                  <option value="error">Error</option>
                </select>
              </div>
            )}
          </div>

          {/* Performance Ranking Section */}
          {agents.length > 1 && Object.keys(agentStats).length > 0 && (
            <div className="mt-2 mb-3">
              <button
                onClick={() => setExpandedGroups(prev => {
                  const newSet = new Set(prev);
                  if (newSet.has('ranking')) newSet.delete('ranking');
                  else newSet.add('ranking');
                  return newSet;
                })}
                className="w-full flex items-center justify-between px-2 py-1.5 rounded hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <BarChart2 size={14} className="text-yellow-400" />
                  <span className="text-xs font-medium text-gray-300">Performance Ranking</span>
                </div>
                <ChevronDown
                  size={14}
                  className={`text-gray-400 transition-transform ${expandedGroups.has('ranking') ? 'rotate-180' : ''}`}
                />
              </button>

              {expandedGroups.has('ranking') && (
                <div className="mt-2 space-y-1">
                  {agents
                    .filter(a => agentStats[a.id])
                    .sort((a, b) => {
                      const statsA = agentStats[a.id];
                      const statsB = agentStats[b.id];
                      // Sort by score, then by tasks completed
                      if (statsB.score !== statsA.score) return statsB.score - statsA.score;
                      return statsB.tasks_completed - statsA.tasks_completed;
                    })
                    .slice(0, 5)
                    .map((agent, index) => {
                      const stats = agentStats[agent.id];
                      const color = AGENT_COLORS[agent.type]?.primary || '#888';
                      const medals = ['🥇', '🥈', '🥉'];

                      return (
                        <div
                          key={agent.id}
                          className={`flex items-center gap-2 px-2 py-1.5 rounded transition-colors cursor-pointer ${
                            selectedAgentId === agent.id ? 'bg-gray-700' : 'hover:bg-gray-700/50'
                          }`}
                          onClick={() => selectAgent(agent.id)}
                        >
                          {/* Rank */}
                          <span className="w-5 text-center text-sm">
                            {index < 3 ? medals[index] : `${index + 1}.`}
                          </span>

                          {/* Agent Avatar */}
                          <div
                            className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                            style={{ backgroundColor: color }}
                          >
                            {(agent.name || '?').charAt(0)}
                          </div>

                          {/* Name & Stats */}
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-white truncate">{agent.name}</div>
                            <div className="flex items-center gap-2 text-[10px] text-gray-400">
                              <span>Lv.{stats.level}</span>
                              <span>•</span>
                              <span>{stats.tasks_completed} tasks</span>
                            </div>
                          </div>

                          {/* Score */}
                          <div className="text-right">
                            <div className="text-xs font-bold text-yellow-400">{stats.score}</div>
                            <div className="text-[9px] text-gray-500">pts</div>
                          </div>
                        </div>
                      );
                    })}
                </div>
              )}
            </div>
          )}

          {/* Global shimmer animation style */}
          <style>{`
            @keyframes shimmer {
              0% { background-position: -200% 0; }
              100% { background-position: 200% 0; }
            }
          `}</style>

          {/* Agent list */}
          <div className="flex-1 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">
                Agents {filteredCount !== agents.length ? `(${filteredCount}/${agents.length})` : `(${agents.length})`}
              </span>
              <Tooltip content="Create new agent" position="top">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="p-1 hover:bg-gray-700 rounded transition-colors"
                >
                  <Plus size={16} className="text-white" />
                </button>
              </Tooltip>
            </div>

            {/* Grouped Agent List */}
            <div className="space-y-2">
              {/* Loading Skeleton */}
              {isLoading ? (
                <>
                  {Array.from({ length: 4 }).map((_, i) => (
                    <AgentCardSkeleton key={i} />
                  ))}
                </>
              ) : Object.keys(groupedAgents).length === 0 ? (
                <div className="text-gray-500 text-sm text-center py-4">
                  No agents found
                </div>
              ) : (
                Object.entries(groupedAgents).map(([groupName, groupAgents]) => (
                <div key={groupName} className="mb-2">
                  {/* Group Header */}
                  <button
                    onClick={() => toggleGroup(groupName)}
                    className="w-full flex items-center gap-2 px-2 py-1.5 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded transition-colors"
                  >
                    <ChevronDown
                      size={14}
                      className={`transition-transform duration-200 ${expandedGroups.has(groupName) ? '' : '-rotate-90'}`}
                    />
                    <span className="text-xs font-medium">{groupName}</span>
                    <span className="text-xs text-gray-500">({groupAgents.length})</span>
                  </button>

                  {/* Group Content */}
                  {expandedGroups.has(groupName) && (
                    <div className="space-y-1 mt-1 pl-2">
                      {groupAgents.map((agent) => (
                        <div
                          key={agent.id}
                          onClick={() => selectAgent(selectedAgentId === agent.id ? null : agent.id)}
                          className={`relative p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                            selectedAgentId === agent.id
                              ? 'bg-gray-700 ring-2 ring-blue-500 scale-[1.02]'
                              : 'bg-gray-700/50 hover:bg-gray-700 hover:scale-[1.01] hover:shadow-lg hover:shadow-black/20'
                          }`}
                          style={{
                            borderLeftWidth: selectedAgentId === agent.id ? '3px' : '0px',
                            borderLeftColor: AGENT_COLORS[agent.type]?.primary || '#6B7280',
                          }}
                        >
                          {/* Left color indicator on hover */}
                          {selectedAgentId !== agent.id && (
                            <div
                              className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-0 group-hover:h-8 transition-all duration-200 opacity-0 hover:opacity-100"
                              style={{ backgroundColor: AGENT_COLORS[agent.type]?.primary || '#6B7280' }}
                            />
                          )}
                          <div className="flex items-start gap-3">
                            <div className="relative">
                              <div
                                className="w-8 h-8 rounded-full flex items-center justify-center overflow-hidden"
                                style={{ backgroundColor: AGENT_COLORS[agent.type]?.primary || '#6B7280' }}
                              >
                                {agent.avatar_url ? (
                                  <img
                                    src={agent.avatar_url}
                                    alt={agent.name}
                                    className="w-full h-full object-cover"
                                    onError={(e) => {
                                      // Fallback to initial on image load error
                                      (e.target as HTMLImageElement).style.display = 'none';
                                    }}
                                  />
                                ) : (
                                  <span className="text-white text-xs font-bold">
                                    {(agent.name || '?').charAt(0).toUpperCase()}
                                  </span>
                                )}
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
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1.5 flex-1 min-w-0">
                                  {favoriteAgents.has(agent.id) && (
                                    <Star size={10} className="text-yellow-400 fill-yellow-400 flex-shrink-0" />
                                  )}
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
                                {/* Quick Actions Menu Button */}
                                <button
                                  onClick={(e) => handleQuickMenuToggle(e, agent.id)}
                                  className="p-1 rounded hover:bg-gray-600 text-gray-400 hover:text-white transition-colors"
                                >
                                  <MoreVertical size={14} />
                                </button>
                              </div>
                              {/* Quick Actions Dropdown */}
                              {activeQuickMenu === agent.id && (
                                <div
                                  ref={quickMenuRef}
                                  className="absolute right-4 top-12 bg-gray-800 rounded-lg shadow-xl border border-gray-700 py-1 z-50 min-w-[140px]"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <button
                                    onClick={() => { toggleFavorite(agent.id); setActiveQuickMenu(null); }}
                                    className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <Star size={14} className={favoriteAgents.has(agent.id) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-400'} />
                                    <span>{favoriteAgents.has(agent.id) ? '取消收藏' : '收藏'}</span>
                                  </button>
                                  <button
                                    onClick={() => handleCreateTask(agent)}
                                    className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <ClipboardList size={14} className="text-blue-400" />
                                    <span>Create Task</span>
                                  </button>
                                  <button
                                    onClick={() => handleStartChat(agent)}
                                    className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <MessageSquare size={14} className="text-green-400" />
                                    <span>Start Chat</span>
                                  </button>
                                  <button
                                    onClick={() => handleViewStats(agent)}
                                    className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <BarChart2 size={14} className="text-yellow-400" />
                                    <span>View Stats</span>
                                  </button>
                                  <button
                                    onClick={() => handleCopyAgentId(agent)}
                                    className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <Copy size={14} className="text-gray-400" />
                                    <span>Copy ID</span>
                                  </button>
                                  <button
                                    onClick={() => {
                                      selectAgent(agent.id);
                                      setActiveQuickMenu(null);
                                    }}
                                    className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <ExternalLink size={14} className="text-purple-400" />
                                    <span>View Details</span>
                                  </button>
                                  <div className="border-t border-gray-700 my-1" />
                                  <button
                                    onClick={() => handleDeleteAgent(agent)}
                                    className="w-full px-3 py-2 text-left text-sm text-red-400 hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <Trash2 size={14} />
                                    <span>Delete Agent</span>
                                  </button>
                                </div>
                              )}
                              <div className="text-gray-400 text-xs flex items-center gap-2">
                                <span>{getAgentDisplayType(agent)}</span>
                                <StatusDot status={agent.status} />
                                {/* Workload badge */}
                                {(() => {
                                  const workload = getAgentWorkload(agent.id);
                                  return workload > 0 ? (
                                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                                      workload >= 3 ? 'bg-red-500/20 text-red-400' :
                                      workload >= 2 ? 'bg-yellow-500/20 text-yellow-400' :
                                      'bg-blue-500/20 text-blue-400'
                                    }`}>
                                      {workload} task{workload > 1 ? 's' : ''}
                                    </span>
                                  ) : null;
                                })()}
                              </div>
                              {/* Tags */}
                              {agent.tags && agent.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-1.5">
                                  {agent.tags.slice(0, 3).map((tag, idx) => (
                                    <span
                                      key={idx}
                                      className="px-1.5 py-0.5 bg-blue-500/20 text-blue-300 rounded text-[10px] truncate max-w-[60px]"
                                      title={tag}
                                    >
                                      {tag}
                                    </span>
                                  ))}
                                  {agent.tags.length > 3 && (
                                    <span className="px-1.5 py-0.5 bg-gray-600/50 text-gray-400 rounded text-[10px]">
                                      +{agent.tags.length - 3}
                                    </span>
                                  )}
                                </div>
                              )}
                              {/* Task Progress Bar when working */}
                              {agent.status === 'working' && (
                                <div className="mt-2">
                                  <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
                                    <span>Processing...</span>
                                    <span className="text-blue-400">Working</span>
                                  </div>
                                  <div className="h-1.5 bg-gray-600 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-blue-500 rounded-full animate-pulse"
                                      style={{
                                        width: '100%',
                                        backgroundSize: '200% 100%',
                                        animation: 'shimmer 1.5s infinite linear'
                                      }}
                                    />
                                  </div>
                                </div>
                              )}
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
                                  {/* Task Stats */}
                                  <div className="flex items-center gap-2 mt-1 text-[10px]">
                                    <span className="text-green-400 flex items-center gap-0.5">
                                      <ClipboardList size={10} />
                                      <span>{agentStats[agent.id].tasks_completed ?? 0}</span>
                                    </span>
                                    <span className="text-gray-600">|</span>
                                    <span className="text-emerald-400 flex items-center gap-0.5">
                                      <span>Success:</span>
                                      <span>
                                        {agentStats[agent.id].tasks_completed > 0
                                          ? Math.round((agentStats[agent.id].tasks_successful / agentStats[agent.id].tasks_completed) * 100)
                                          : 0}%
                                      </span>
                                    </span>
                                    {agentStats[agent.id].achievements?.length > 0 && (
                                      <>
                                        <span className="text-gray-600">|</span>
                                        <span className="text-purple-400 flex items-center gap-0.5">
                                          <Star size={10} />
                                          <span>{agentStats[agent.id].achievements.length}</span>
                                        </span>
                                      </>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )))}
            </div>
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
                  {([
                    'coder', 'analyst', 'assistant', 'tester', 'custom',
                    'pua-coder', 'pua-analyst', 'pua-assistant', 'pua-tester'
                  ] as AgentType[]).map((type) => (
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
                            ? AGENT_COLORS[type]?.primary || '#6B7280'
                            : undefined,
                      }}
                    >
                      {AGENT_LABELS[type]}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-gray-400 text-sm block mb-1 flex items-center gap-1">
                  <Image size={12} />
                  Avatar URL (optional)
                </label>
                <input
                  type="text"
                  value={newAgentAvatarUrl}
                  onChange={(e) => setNewAgentAvatarUrl(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
                  placeholder="https://example.com/avatar.png"
                />
                {newAgentAvatarUrl && (
                  <div className="mt-2 flex items-center gap-2">
                    <div
                      className="w-8 h-8 rounded-full overflow-hidden bg-gray-700 flex items-center justify-center"
                      style={{ backgroundColor: AGENT_COLORS[newAgentType]?.primary || '#6B7280' }}
                    >
                      <img
                        src={newAgentAvatarUrl}
                        alt="Preview"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none';
                        }}
                      />
                    </div>
                    <span className="text-xs text-gray-400">Preview</span>
                  </div>
                )}
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
