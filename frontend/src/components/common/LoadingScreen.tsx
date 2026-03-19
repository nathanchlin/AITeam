import { useState, useEffect } from 'react';
import { Users, Cpu, Zap, Globe } from 'lucide-react';

export function LoadingScreen() {
  const [fadeIn, setFadeIn] = useState(false);
  const [showHints, setShowHints] = useState(false);

  useEffect(() => {
    // Trigger fade in animation
    const fadeTimer = setTimeout(() => setFadeIn(true), 100);
    // Show loading hints after delay
    const hintsTimer = setTimeout(() => setShowHints(true), 800);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(hintsTimer);
    };
  }, []);

  return (
    <div
      className={`flex flex-col items-center justify-center w-full h-full bg-gray-900 transition-opacity duration-500 ${
        fadeIn ? 'opacity-100' : 'opacity-0'
      }`}
    >
      {/* Logo and Brand */}
      <div className="flex items-center gap-4 mb-8">
        <div className="relative">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Users size={32} className="text-white" />
          </div>
          {/* Animated ring */}
          <div className="absolute inset-0 rounded-2xl border-2 border-blue-400/50 animate-ping" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">AITeam</h1>
          <p className="text-gray-400 text-sm">Multi-Agent Collaboration Platform</p>
        </div>
      </div>

      {/* Loading Progress Bar */}
      <div className="w-64 mb-8">
        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 rounded-full animate-pulse"
            style={{
              width: '60%',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s infinite linear',
            }}
          />
        </div>
        <p className="text-gray-500 text-xs text-center mt-2">Loading agents...</p>
      </div>

      {/* Loading Hints */}
      {showHints && (
        <div className="flex flex-col gap-3 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
          <LoadingHint icon={<Cpu size={16} />} text="Connecting to AI Agents" delay={0} />
          <LoadingHint icon={<Zap size={16} />} text="Initializing Pipeline" delay={200} />
          <LoadingHint icon={<Globe size={16} />} text="Loading 3D Workspace" delay={400} />
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

function LoadingHint({ icon, text, delay }: { icon: React.ReactNode; text: string; delay: number }) {
  return (
    <div
      className="flex items-center gap-3 text-gray-400 text-sm"
      style={{
        animation: `fadeIn 0.5s ease-out ${delay}ms forwards`,
        opacity: 0,
      }}
    >
      <div className="w-6 h-6 bg-gray-800 rounded flex items-center justify-center text-gray-500">
        {icon}
      </div>
      <span>{text}</span>
      <div className="flex gap-1 ml-auto">
        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}
