import { useState, useEffect } from 'react';
import { X, Trash2, RefreshCw, Download, Database, AlertTriangle, CheckCircle, ClipboardList } from 'lucide-react';
import { useToast } from '../common/Toast';
import { useAgentStore } from '../../stores/agentStore';

interface DevToolsPanelProps {
  onClose: () => void;
}

interface StorageItem {
  key: string;
  size: number;
  preview: string;
}

// Known AITeam storage keys
const AITEAM_KEYS = [
  'aiteam_favorite_agents',
  'aiteam_pinned_conversations',
  'aiteam_last_viewed_conversations',
  'aiteam_event_notifications',
  'aiteam_theme',
];

function getStorageSize(str: string): number {
  return new Blob([str]).size;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

export function DevToolsPanel({ onClose }: DevToolsPanelProps) {
  const toast = useToast();
  const { agents, tasks, plans, wsConnected } = useAgentStore();
  const [items, setItems] = useState<StorageItem[]>([]);
  const [totalSize, setTotalSize] = useState(0);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [itemValue, setItemValue] = useState<string>('');

  const loadStorageItems = () => {
    const storageItems: StorageItem[] = [];
    let total = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        const value = localStorage.getItem(key) || '';
        const size = getStorageSize(value);
        total += size;

        storageItems.push({
          key,
          size,
          preview: value.length > 50 ? value.slice(0, 50) + '...' : value,
        });
      }
    }

    // Sort by size descending
    storageItems.sort((a, b) => b.size - a.size);
    setItems(storageItems);
    setTotalSize(total);
  };

  useEffect(() => {
    loadStorageItems();
  }, []);

  const handleViewItem = (key: string) => {
    const value = localStorage.getItem(key);
    if (value) {
      try {
        // Try to parse as JSON for better display
        const parsed = JSON.parse(value);
        setItemValue(JSON.stringify(parsed, null, 2));
      } catch {
        setItemValue(value);
      }
      setSelectedKey(key);
    }
  };

  const handleDeleteItem = (key: string) => {
    if (confirm(`Delete localStorage key "${key}"?`)) {
      localStorage.removeItem(key);
      loadStorageItems();
      if (selectedKey === key) {
        setSelectedKey(null);
        setItemValue('');
      }
      toast.success(`Deleted key: ${key}`);
    }
  };

  const handleClearAITeam = () => {
    const deleted: string[] = [];
    AITEAM_KEYS.forEach(key => {
      if (localStorage.getItem(key)) {
        localStorage.removeItem(key);
        deleted.push(key);
      }
    });
    loadStorageItems();
    toast.success(`Cleared ${deleted.length} AITeam keys`);
  };

  const handleExportAll = () => {
    const data: Record<string, string> = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        data[key] = localStorage.getItem(key) || '';
      }
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `localStorage-backup-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Exported localStorage');
  };

  const handleClearAll = () => {
    if (confirm('Clear ALL localStorage? This cannot be undone!')) {
      localStorage.clear();
      loadStorageItems();
      setSelectedKey(null);
      setItemValue('');
      toast.success('Cleared all localStorage');
    }
  };

  // Copy debug info for bug reports
  const handleCopyDebugInfo = () => {
    const debugInfo = {
      timestamp: new Date().toISOString(),
      version: '1.5.0',
      system: {
        agents: agents.length,
        tasks: tasks.length,
        plans: plans.length,
        wsConnected,
      },
      agentStatus: {
        working: agents.filter(a => a.status === 'working').length,
        idle: agents.filter(a => a.status === 'idle').length,
        error: agents.filter(a => a.status === 'error').length,
      },
      taskStatus: {
        pending: tasks.filter(t => t.status === 'pending').length,
        running: tasks.filter(t => t.status === 'running').length,
        completed: tasks.filter(t => t.status === 'completed').length,
        failed: tasks.filter(t => t.status === 'failed').length,
      },
      localStorage: {
        keys: items.length,
        totalSize: formatBytes(totalSize),
        aiteamKeys: items.filter(i => AITEAM_KEYS.includes(i.key)).map(i => i.key),
      },
      browser: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
      },
    };

    navigator.clipboard.writeText(JSON.stringify(debugInfo, null, 2));
    toast.success('Debug info copied to clipboard');
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg w-[700px] max-h-[80vh] flex flex-col shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <Database size={18} className="text-purple-400" />
            <h3 className="text-white font-semibold">Dev Tools - localStorage Manager</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">Total: {formatBytes(totalSize)}</span>
            <button onClick={onClose} className="p-1.5 hover:bg-gray-700 rounded text-gray-400">
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 p-3 border-b border-gray-700 bg-gray-800/50">
          <button
            onClick={loadStorageItems}
            className="px-3 py-1.5 bg-gray-700 text-gray-300 rounded text-xs hover:bg-gray-600 flex items-center gap-1"
          >
            <RefreshCw size={12} />
            Refresh
          </button>
          <button
            onClick={handleExportAll}
            className="px-3 py-1.5 bg-blue-600/20 text-blue-400 rounded text-xs hover:bg-blue-600/30 flex items-center gap-1"
          >
            <Download size={12} />
            Export All
          </button>
          <button
            onClick={handleClearAITeam}
            className="px-3 py-1.5 bg-yellow-600/20 text-yellow-400 rounded text-xs hover:bg-yellow-600/30 flex items-center gap-1"
          >
            <AlertTriangle size={12} />
            Clear AITeam Data
          </button>
          <button
            onClick={handleClearAll}
            className="px-3 py-1.5 bg-red-600/20 text-red-400 rounded text-xs hover:bg-red-600/30 flex items-center gap-1"
          >
            <Trash2 size={12} />
            Clear All
          </button>
          <button
            onClick={handleCopyDebugInfo}
            className="px-3 py-1.5 bg-purple-600/20 text-purple-400 rounded text-xs hover:bg-purple-600/30 flex items-center gap-1"
            title="Copy system info for bug reports"
          >
            <ClipboardList size={12} />
            Copy Debug Info
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Item List */}
          <div className="w-1/2 border-r border-gray-700 overflow-y-auto">
            {items.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                No items in localStorage
              </div>
            ) : (
              <div className="divide-y divide-gray-700">
                {items.map(item => (
                  <div
                    key={item.key}
                    className={`p-3 cursor-pointer transition-colors ${
                      selectedKey === item.key ? 'bg-blue-600/20' : 'hover:bg-gray-700/50'
                    }`}
                    onClick={() => handleViewItem(item.key)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {AITEAM_KEYS.includes(item.key) ? (
                          <CheckCircle size={12} className="text-green-400" />
                        ) : (
                          <Database size={12} className="text-gray-500" />
                        )}
                        <span className="text-white text-sm font-mono truncate">{item.key}</span>
                      </div>
                      <span className="text-xs text-gray-500">{formatBytes(item.size)}</span>
                    </div>
                    <p className="text-gray-500 text-xs mt-1 font-mono truncate">{item.preview}</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteItem(item.key); }}
                      className="mt-2 px-2 py-0.5 bg-red-600/20 text-red-400 rounded text-xs hover:bg-red-600/30"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Value Viewer */}
          <div className="w-1/2 p-3 bg-gray-900/50 overflow-y-auto">
            {selectedKey ? (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-xs font-mono">{selectedKey}</span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(itemValue);
                      toast.success('Copied to clipboard');
                    }}
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    Copy
                  </button>
                </div>
                <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap break-all bg-gray-800 p-2 rounded max-h-96 overflow-y-auto">
                  {itemValue}
                </pre>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                Select an item to view value
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-gray-700 bg-gray-800/50">
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span>AITeam Keys: {items.filter(i => AITEAM_KEYS.includes(i.key)).length}</span>
            <span>Total Keys: {items.length}</span>
            <span className="text-gray-500">|</span>
            <span className="flex items-center gap-1">
              <CheckCircle size={10} className="text-green-400" /> = AITeam managed
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
