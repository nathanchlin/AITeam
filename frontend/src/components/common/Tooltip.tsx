import { useState, useRef, useEffect, ReactNode } from 'react';
import { createPortal } from 'react-dom';

type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';

interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  position?: TooltipPosition;
  delay?: number;
  className?: string;
}

export function Tooltip({
  content,
  children,
  position = 'top',
  delay = 300,
  className = '',
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [coords, setCoords] = useState({ x: 0, y: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const calculatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const gap = 8;

    let x = 0;
    let y = 0;

    switch (position) {
      case 'top':
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        y = triggerRect.top - tooltipRect.height - gap;
        break;
      case 'bottom':
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        y = triggerRect.bottom + gap;
        break;
      case 'left':
        x = triggerRect.left - tooltipRect.width - gap;
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        break;
      case 'right':
        x = triggerRect.right + gap;
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        break;
    }

    // Keep tooltip within viewport
    const padding = 8;
    x = Math.max(padding, Math.min(x, window.innerWidth - tooltipRect.width - padding));
    y = Math.max(padding, Math.min(y, window.innerHeight - tooltipRect.height - padding));

    setCoords({ x, y });
  };

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    if (isVisible) {
      calculatePosition();
    }
  }, [isVisible, position]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const getArrowClasses = () => {
    const arrowSize = '6px';
    const arrowColor = '#1f2937';

    switch (position) {
      case 'top':
        return `after:content-[''] after:absolute after:left-1/2 after:-translate-x-1/2 after:top-full after:border-[${arrowSize}] after:border-transparent after:border-t-[${arrowColor}]`;
      case 'bottom':
        return `after:content-[''] after:absolute after:left-1/2 after:-translate-x-1/2 after:bottom-full after:border-[${arrowSize}] after:border-transparent after:border-b-[${arrowColor}]`;
      case 'left':
        return `after:content-[''] after:absolute after:left-full after:top-1/2 after:-translate-y-1/2 after:border-[${arrowSize}] after:border-transparent after:border-l-[${arrowColor}]`;
      case 'right':
        return `after:content-[''] after:absolute after:right-full after:top-1/2 after:-translate-y-1/2 after:border-[${arrowSize}] after:border-transparent after:border-r-[${arrowColor}]`;
    }
  };

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="inline-block"
      >
        {children}
      </div>

      {isVisible &&
        createPortal(
          <div
            ref={tooltipRef}
            className={`fixed z-[9999] px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg whitespace-nowrap transition-opacity duration-150 ${getArrowClasses()} ${className}`}
            style={{
              left: coords.x,
              top: coords.y,
              opacity: coords.x === 0 && coords.y === 0 ? 0 : 1,
            }}
          >
            {content}
          </div>,
          document.body
        )}
    </>
  );
}

// Simple wrapper for icon buttons with tooltip
interface IconButtonWithTooltipProps {
  icon: ReactNode;
  tooltip: string;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  position?: TooltipPosition;
}

export function IconButtonWithTooltip({
  icon,
  tooltip,
  onClick,
  className = '',
  disabled = false,
  position = 'top',
}: IconButtonWithTooltipProps) {
  return (
    <Tooltip content={tooltip} position={position}>
      <button
        onClick={onClick}
        disabled={disabled}
        className={`p-1 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        {icon}
      </button>
    </Tooltip>
  );
}
