import { useEffect, useRef } from 'react';

interface UseAutoResizeOptions {
  /** Minimum height in pixels */
  minHeight?: number;
  /** Maximum height in pixels */
  maxHeight?: number;
  /** Dependency value that triggers resize (e.g., message content) */
  value: string;
}

/**
 * Hook for auto-resizing textarea based on content.
 * Automatically adjusts height between minHeight and maxHeight.
 *
 * @example
 * ```tsx
 * const textareaRef = useAutoResize({ value: message, minHeight: 40, maxHeight: 200 });
 * return <textarea ref={textareaRef} value={message} onChange={...} />
 * ```
 */
export function useAutoResize({ value, minHeight = 40, maxHeight = 200 }: UseAutoResizeOptions) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto';
      // Calculate new height within bounds
      const newHeight = Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight);
      textarea.style.height = `${newHeight}px`;
    }
  }, [value, minHeight, maxHeight]);

  return textareaRef;
}
