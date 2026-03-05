import { useEffect, useState } from 'react';
import { useAgentStore } from '../../stores/agentStore';
import { Trophy, X } from 'lucide-react';

export function AchievementNotification() {
  const { achievementNotifications, removeAchievementNotification, agents } = useAgentStore();

  // Auto-remove notifications after 5 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      removeAchievementNotification(0);
    }, 5000);

    return () => clearInterval(timer);
  }, [removeAchievementNotification]);

  if (achievementNotifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {achievementNotifications.map((notification, index) => (
        <AchievementCard
          key={`${notification.agent_id}-${notification.achievement.id}-${index}`}
          notification={notification}
          agent={agents.find(a => a.id === notification.agent_id)}
          onDismiss={() => removeAchievementNotification(index)}
        />
      ))}
    </div>
  );
}

interface AchievementCardProps {
  notification: {
    agent_id: string;
    agent_name: string;
    achievement: {
      id: string;
      name: string;
      description: string;
      icon: string;
      xp_reward: number;
    };
  };
  agent?: {
    name: string;
  };
  onDismiss: () => void;
}

function AchievementCard({ notification, agent, onDismiss }: AchievementCardProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Animate in
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className={`
        pointer-events-auto w-80 bg-gradient-to-br from-yellow-900/95 to-amber-900/95 backdrop-blur
        rounded-lg border border-yellow-500/50 shadow-2xl overflow-hidden
        transform transition-all duration-500 ease-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0'}
      `}
    >
      {/* Header with dismiss button */}
      <div className="px-4 py-2 bg-yellow-500/20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Trophy className="w-4 h-4 text-yellow-400" />
          <span className="text-yellow-300 text-sm font-semibold">Achievement Unlocked!</span>
        </div>
        <button
          onClick={onDismiss}
          className="text-yellow-400/70 hover:text-yellow-400 transition-colors"
        >
          <X size={16} />
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Achievement Icon */}
          <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">{notification.achievement.icon}</span>
          </div>

          {/* Achievement Info */}
          <div className="flex-1 min-w-0">
            <h4 className="text-white font-semibold text-sm truncate">
              {notification.achievement.name}
            </h4>
            <p className="text-yellow-200/70 text-xs mt-1 line-clamp-2">
              {notification.achievement.description}
            </p>

            {/* XP Reward */}
            <div className="mt-2 flex items-center gap-1 text-yellow-400 text-xs font-medium">
              <Trophy size={12} />
              <span>+{notification.achievement.xp_reward} XP</span>
            </div>
          </div>
        </div>

        {/* Agent Name */}
        {agent && (
          <div className="mt-3 pt-3 border-t border-yellow-500/20">
            <p className="text-yellow-200/50 text-xs">
              Unlocked by <span className="text-yellow-300 font-medium">{agent.name}</span>
            </p>
          </div>
        )}
      </div>

      {/* Shimmer effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-yellow-400/10 to-transparent animate-shimmer" />
      </div>
    </div>
  );
}

// Add shimmer animation
const style = document.createElement('style');
style.textContent = `
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
  .animate-shimmer {
    animation: shimmer 2s infinite;
  }
`;
document.head.appendChild(style);
