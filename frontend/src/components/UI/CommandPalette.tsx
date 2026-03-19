import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Search, X, Plus, Users, Layout, MessageSquare, GitBranch, Settings, Moon, Sun, Bell, BellOff, Volume2, VolumeX, Layers, FolderOpen, HelpCircle, Zap, ArrowRight } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { useTheme } from '../../hooks/useTheme';
import { useNotifications } from '../../hooks/useNotifications';
import { useSoundNotifications } from '../../hooks/useSoundNotifications';
import { AGENT_COLORS, getAgentDisplayType, type Agent } from '../../types';

interface Command {
  id: string;
  label: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void;
  category: 'navigation' | 'agents' | 'actions' | 'settings';
  keywords?: string[];
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateAgent: () => void;
  onSelectAgent: (agent: Agent) => void;
}

export function CommandPalette({ isOpen, onClose, onCreateAgent, onSelectAgent }: CommandPaletteProps) {
  const { agents, toggleSidebar, toggleTaskPanel, togglePipelinePanel, toggleIMPanel, toggleProjectsPanel } = useAgentStore();
  const { theme, toggleTheme } = useTheme();
  const { enabled: notificationsEnabled, toggleNotifications } = useNotifications();
  const { enabled: soundEnabled, toggleEnabled: toggleSound } = useSoundNotifications();

  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Build commands list
  const commands = useMemo<Command[]>(() => {
    const cmds: Command[] = [
      // Navigation
      { id: 'toggle-sidebar', label: 'Toggle Sidebar', description: 'Show/hide agent list', icon: <Users size={16} />, action: toggleSidebar, category: 'navigation', keywords: ['agents', 'list'] },
      { id: 'toggle-tasks', label: 'Toggle Task Panel', description: 'Show/hide task management', icon: <Layout size={16} />, action: toggleTaskPanel, category: 'navigation', keywords: ['todos'] },
      { id: 'toggle-pipeline', label: 'Toggle Pipeline Panel', description: 'Show/hide pipeline view', icon: <GitBranch size={16} />, action: togglePipelinePanel, category: 'navigation', keywords: ['workflow'] },
      { id: 'toggle-im', label: 'Toggle IM Panel', description: 'Show/hide messaging panel', icon: <MessageSquare size={16} />, action: toggleIMPanel, category: 'navigation', keywords: ['chat', 'messages'] },
      { id: 'toggle-projects', label: 'Toggle Projects Panel', description: 'Show/hide projects view', icon: <FolderOpen size={16} />, action: toggleProjectsPanel, category: 'navigation', keywords: ['files'] },

      // Actions
      { id: 'create-agent', label: 'Create New Agent', description: 'Add a new AI agent', icon: <Plus size={16} />, action: onCreateAgent, category: 'actions', keywords: ['add', 'new'] },

      // Settings
      { id: 'toggle-theme', label: theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode', icon: theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />, action: toggleTheme, category: 'settings', keywords: ['appearance', 'color'] },
      { id: 'toggle-notifications', label: notificationsEnabled ? 'Disable Notifications' : 'Enable Notifications', icon: notificationsEnabled ? <BellOff size={16} /> : <Bell size={16} />, action: toggleNotifications, category: 'settings', keywords: ['alerts'] },
      { id: 'toggle-sound', label: soundEnabled ? 'Mute Sounds' : 'Unmute Sounds', icon: soundEnabled ? <VolumeX size={16} /> : <Volume2 size={16} />, action: toggleSound, category: 'settings', keywords: ['audio'] },
      { id: 'keyboard-help', label: 'Show Keyboard Shortcuts', description: 'View all shortcuts', icon: <HelpCircle size={16} />, action: () => { onClose(); /* Will trigger via keyboard */ }, category: 'settings', keywords: ['keys', '?'] },
    ];

    // Add agent selection commands
    agents.forEach(agent => {
      if (agent && agent.id && agent.name) {
        cmds.push({
          id: `select-agent-${agent.id}`,
          label: agent.name,
          description: getAgentDisplayType(agent),
          icon: (
            <div
              className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
              style={{ backgroundColor: AGENT_COLORS[agent.type]?.primary || '#6B7280' }}
            >
              {agent.name.charAt(0).toUpperCase()}
            </div>
          ),
          action: () => onSelectAgent(agent),
          category: 'agents',
          keywords: [agent.type, agent.display_type].filter(Boolean) as string[],
        });
      }
    });

    return cmds;
  }, [agents, theme, notificationsEnabled, soundEnabled, toggleSidebar, toggleTaskPanel, togglePipelinePanel, toggleIMPanel, toggleProjectsPanel, onCreateAgent, onSelectAgent, toggleTheme, toggleNotifications, toggleSound, onClose]);

  // Filter commands by query
  const filteredCommands = useMemo(() => {
    if (!query.trim()) return commands;

    const q = query.toLowerCase();
    return commands.filter(cmd => {
      if (cmd.label.toLowerCase().includes(q)) return true;
      if (cmd.description?.toLowerCase().includes(q)) return true;
      if (cmd.keywords?.some(k => k.includes(q))) return true;
      return false;
    });
  }, [commands, query]);

  // Group commands by category
  const groupedCommands = useMemo(() => {
    const groups: Record<string, Command[]> = {};
    const order = ['actions', 'agents', 'navigation', 'settings'];

    order.forEach(cat => {
      const cmds = filteredCommands.filter(c => c.category === cat);
      if (cmds.length > 0) {
        const labels: Record<string, string> = {
          actions: 'Actions',
          agents: 'Agents',
          navigation: 'Navigation',
          settings: 'Settings',
        };
        groups[labels[cat]] = cmds;
      }
    });

    return groups;
  }, [filteredCommands]);

  // Reset state when opening
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [isOpen]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const totalItems = filteredCommands.length;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => (prev + 1) % totalItems);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => (prev - 1 + totalItems) % totalItems);
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredCommands[selectedIndex]) {
            filteredCommands[selectedIndex].action();
            onClose();
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredCommands, selectedIndex, onClose]);

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedElement = listRef.current.querySelector(`[data-index="${selectedIndex}"]`);
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  const handleCommandClick = useCallback((cmd: Command, index: number) => {
    setSelectedIndex(index);
    cmd.action();
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-start justify-center pt-[15vh] z-[200]" onClick={onClose}>
      <div
        className="bg-gray-800 rounded-xl shadow-2xl w-[560px] max-h-[60vh] overflow-hidden border border-gray-700"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-700">
          <Search size={18} className="text-gray-500" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search commands, agents, actions..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            className="flex-1 bg-transparent text-white text-sm placeholder-gray-500 focus:outline-none"
          />
          <kbd className="px-2 py-0.5 bg-gray-700 rounded text-[10px] text-gray-400 border border-gray-600">ESC</kbd>
        </div>

        {/* Commands List */}
        <div ref={listRef} className="overflow-y-auto max-h-[50vh]">
          {Object.entries(groupedCommands).map(([category, cmds]) => (
            <div key={category}>
              <div className="px-4 py-2 text-xs text-gray-500 font-medium bg-gray-800/50 sticky top-0">
                {category}
              </div>
              {cmds.map((cmd, idx) => {
                const globalIndex = filteredCommands.indexOf(cmd);
                return (
                  <div
                    key={cmd.id}
                    data-index={globalIndex}
                    onClick={() => handleCommandClick(cmd, globalIndex)}
                    className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors ${
                      globalIndex === selectedIndex
                        ? 'bg-blue-600/30 text-white'
                        : 'text-gray-300 hover:bg-gray-700/50'
                    }`}
                  >
                    <div className={`${globalIndex === selectedIndex ? 'text-blue-400' : 'text-gray-500'}`}>
                      {cmd.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{cmd.label}</div>
                      {cmd.description && (
                        <div className="text-xs text-gray-500 truncate">{cmd.description}</div>
                      )}
                    </div>
                    {globalIndex === selectedIndex && (
                      <ArrowRight size={14} className="text-blue-400" />
                    )}
                  </div>
                );
              })}
            </div>
          ))}

          {filteredCommands.length === 0 && (
            <div className="flex flex-col items-center justify-center py-8 text-gray-500">
              <Zap size={24} className="mb-2 opacity-50" />
              <p className="text-sm">No commands found</p>
              <p className="text-xs mt-1">Try a different search term</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-2 border-t border-gray-700 bg-gray-800/50 text-xs text-gray-500">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1 bg-gray-700 rounded text-[10px]">↑</kbd>
              <kbd className="px-1 bg-gray-700 rounded text-[10px]">↓</kbd>
              <span className="ml-1">Navigate</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1 bg-gray-700 rounded text-[10px]">Enter</kbd>
              <span className="ml-1">Select</span>
            </span>
          </div>
          <span>{filteredCommands.length} commands</span>
        </div>
      </div>
    </div>
  );
}
