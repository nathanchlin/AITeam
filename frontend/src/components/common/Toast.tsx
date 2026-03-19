import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  timestamp: number; // Added for history
}

export interface ToastHistoryItem extends Toast {
  dismissedAt?: number;
}

interface ToastContextType {
  toasts: Toast[];
  history: ToastHistoryItem[];
  addToast: (type: ToastType, message: string, duration?: number) => void;
  removeToast: (id: string) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
  info: (message: string) => void;
  clearHistory: () => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

// Default durations by type (in milliseconds)
const DEFAULT_DURATIONS: Record<ToastType, number> = {
  error: 8000,    // Errors need more time to read
  warning: 6000,  // Warnings are important
  info: 5000,     // Info is moderate
  success: 3000,  // Success is quick confirmation
};

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [history, setHistory] = useState<ToastHistoryItem[]>([]);

  const addToast = useCallback((type: ToastType, message: string, duration?: number) => {
    // Use provided duration or default based on type
    const actualDuration = duration ?? DEFAULT_DURATIONS[type];
    const timestamp = Date.now();
    const id = `toast-${timestamp}-${Math.random().toString(36).slice(2, 11)}`;
    const newToast: Toast = { id, type, message, duration: actualDuration, timestamp };

    setToasts(prev => [...prev, newToast]);

    // Add to history
    setHistory(prev => {
      const updated = [...prev, { ...newToast }];
      // Keep only last 50 items
      return updated.slice(-50);
    });

    if (actualDuration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
        // Update history with dismissal time
        setHistory(prev => prev.map(h =>
          h.id === id ? { ...h, dismissedAt: Date.now() } : h
        ));
      }, actualDuration);
    }
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
    // Update history with dismissal time
    setHistory(prev => prev.map(h =>
      h.id === id ? { ...h, dismissedAt: Date.now() } : h
    ));
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  const success = useCallback((message: string) => addToast('success', message), [addToast]);
  const error = useCallback((message: string) => addToast('error', message), [addToast]);
  const warning = useCallback((message: string) => addToast('warning', message), [addToast]);
  const info = useCallback((message: string) => addToast('info', message), [addToast]);

  return (
    <ToastContext.Provider value={{ toasts, history, addToast, removeToast, success, error, warning, info, clearHistory }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

function ToastContainer({ toasts, removeToast }: { toasts: Toast[]; removeToast: (id: string) => void }) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-[200] flex flex-col gap-2 max-w-sm pointer-events-auto">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const icons = {
    success: <CheckCircle size={18} className="text-green-400" />,
    error: <AlertCircle size={18} className="text-red-400" />,
    warning: <AlertTriangle size={18} className="text-yellow-400" />,
    info: <Info size={18} className="text-blue-400" />,
  };

  const bgColors = {
    success: 'bg-green-900/90 border-green-700',
    error: 'bg-red-900/90 border-red-700',
    warning: 'bg-yellow-900/90 border-yellow-700',
    info: 'bg-blue-900/90 border-blue-700',
  };

  const textColors = {
    success: 'text-green-200',
    error: 'text-red-200',
    warning: 'text-yellow-200',
    info: 'text-blue-200',
  };

  const progressColors = {
    success: 'bg-green-400',
    error: 'bg-red-400',
    warning: 'bg-yellow-400',
    info: 'bg-blue-400',
  };

  const duration = toast.duration || DEFAULT_DURATIONS[toast.type];

  return (
    <div
      className={`relative overflow-hidden flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border backdrop-blur-sm animate-slide-in ${bgColors[toast.type]}`}
      role="alert"
    >
      {icons[toast.type]}
      <p className={`text-sm flex-1 ${textColors[toast.type]}`}>{toast.message}</p>
      <button
        onClick={onClose}
        className="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        aria-label="Close notification"
      >
        <X size={14} />
      </button>
      {/* Progress bar */}
      {duration > 0 && (
        <div
          className={`absolute bottom-0 left-0 h-0.5 ${progressColors[toast.type]}`}
          style={{
            animation: `toast-progress ${duration}ms linear forwards`,
          }}
        />
      )}
      <style>{`
        @keyframes toast-progress {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
}
