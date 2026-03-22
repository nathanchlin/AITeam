import { useState } from 'react';
import { Smile, X } from 'lucide-react';

export interface MessageReaction {
  emoji: string;
  users: string[]; // Array of user/agent names
}

interface ReactionPickerProps {
  reactions: MessageReaction[];
  currentUserName: string;
  onAddReaction: (emoji: string) => void;
  onRemoveReaction: (emoji: string) => void;
  showTrigger?: boolean;
}

const AVAILABLE_EMOJIS = ['👍', '👎', '❤️', '😄', '🎉', '😮', '😢', '🔥'];

export function ReactionPicker({
  reactions,
  currentUserName,
  onAddReaction,
  onRemoveReaction,
  showTrigger = true,
}: ReactionPickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const hasReacted = (emoji: string): boolean => {
    const reaction = reactions.find(r => r.emoji === emoji);
    return reaction?.users.includes(currentUserName) || false;
  };

  const handleEmojiClick = (emoji: string) => {
    if (hasReacted(emoji)) {
      onRemoveReaction(emoji);
    } else {
      onAddReaction(emoji);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {/* Trigger Button */}
      {showTrigger && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 hover:bg-gray-700 rounded transition-colors text-gray-400 hover:text-white"
          title="添加表情反应"
        >
          <Smile size={14} />
        </button>
      )}

      {/* Emoji Picker Popup */}
      {isOpen && (
        <div className="absolute bottom-full right-0 mb-1 bg-gray-800 border border-gray-600 rounded-lg shadow-xl p-2 z-20">
          <div className="flex items-center justify-between mb-2 pb-1 border-b border-gray-700">
            <span className="text-xs text-gray-400">添加反应</span>
            <button
              onClick={() => setIsOpen(false)}
              className="p-0.5 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
            >
              <X size={12} />
            </button>
          </div>
          <div className="flex gap-1">
            {AVAILABLE_EMOJIS.map(emoji => (
              <button
                key={emoji}
                onClick={() => handleEmojiClick(emoji)}
                className={`w-8 h-8 flex items-center justify-center text-lg rounded hover:bg-gray-700 transition-colors ${
                  hasReacted(emoji) ? 'bg-blue-500/20 ring-1 ring-blue-500' : ''
                }`}
                title={hasReacted(emoji) ? '点击移除' : '点击添加'}
              >
                {emoji}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Display Existing Reactions */}
      {reactions.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {reactions.map(reaction => (
            <button
              key={reaction.emoji}
              onClick={() => handleEmojiClick(reaction.emoji)}
              className={`flex items-center gap-1 px-1.5 py-0.5 rounded-full text-xs transition-colors ${
                hasReacted(reaction.emoji)
                  ? 'bg-blue-500/30 text-blue-200 ring-1 ring-blue-500/50'
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
              title={`${reaction.users.join(', ')} 的反应`}
            >
              <span>{reaction.emoji}</span>
              <span className="text-[10px]">{reaction.users.length}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Standalone reaction display component (without picker)
interface ReactionDisplayProps {
  reactions: MessageReaction[];
  currentUserName: string;
  onToggleReaction: (emoji: string) => void;
}

export function ReactionDisplay({
  reactions,
  currentUserName,
  onToggleReaction,
}: ReactionDisplayProps) {
  if (reactions.length === 0) return null;

  const hasReacted = (emoji: string): boolean => {
    const reaction = reactions.find(r => r.emoji === emoji);
    return reaction?.users.includes(currentUserName) || false;
  };

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {reactions.map(reaction => (
        <button
          key={reaction.emoji}
          onClick={() => onToggleReaction(reaction.emoji)}
          className={`flex items-center gap-1 px-1.5 py-0.5 rounded-full text-xs transition-colors ${
            hasReacted(reaction.emoji)
              ? 'bg-blue-500/30 text-blue-200 ring-1 ring-blue-500/50'
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
          }`}
          title={`${reaction.users.join(', ')} 的反应`}
        >
          <span>{reaction.emoji}</span>
          <span className="text-[10px]">{reaction.users.length}</span>
        </button>
      ))}
    </div>
  );
}
