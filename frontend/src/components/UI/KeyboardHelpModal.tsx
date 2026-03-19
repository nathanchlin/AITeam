import { X, Keyboard } from 'lucide-react';

export interface ShortcutItem {
  key: string;
  description: string;
  ctrl?: boolean;
  shift?: boolean;
}

interface KeyboardHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: ShortcutItem[];
}

export function KeyboardHelpModal({ isOpen, onClose, shortcuts }: KeyboardHelpModalProps) {
  if (!isOpen) return null;

  const formatKey = (shortcut: ShortcutItem) => {
    const parts: string[] = [];
    if (shortcut.ctrl) parts.push('⌃');
    if (shortcut.shift) parts.push('⇧');
    parts.push(shortcut.key.toUpperCase());
    return parts.join(' + ');
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[100]" onClick={onClose}>
      <div
        className="bg-gray-800 rounded-xl shadow-2xl w-[400px] max-h-[80vh] overflow-hidden border border-gray-700"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-800/80">
          <div className="flex items-center gap-2">
            <Keyboard size={18} className="text-blue-400" />
            <h3 className="text-white font-semibold">Keyboard Shortcuts</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Shortcuts List */}
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          <div className="space-y-2">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-700/50 transition-colors"
              >
                <span className="text-gray-300 text-sm">{shortcut.description}</span>
                <kbd className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300 font-mono border border-gray-600 min-w-[60px] text-center">
                  {formatKey(shortcut)}
                </kbd>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-700 bg-gray-800/80">
          <p className="text-xs text-gray-500 text-center">
            Press <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-[10px]">?</kbd> anytime to toggle this help
          </p>
        </div>
      </div>
    </div>
  );
}
