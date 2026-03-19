import { useEffect, useState } from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'shimmer' | 'none';
}

export function Skeleton({
  className = '',
  variant = 'text',
  width,
  height,
  animation = 'shimmer',
}: SkeletonProps) {
  const getVariantClasses = () => {
    switch (variant) {
      case 'circular':
        return 'rounded-full';
      case 'rectangular':
        return 'rounded-none';
      case 'rounded':
        return 'rounded-lg';
      case 'text':
      default:
        return 'rounded';
    }
  };

  const getAnimationClasses = () => {
    switch (animation) {
      case 'pulse':
        return 'animate-pulse';
      case 'shimmer':
        return 'skeleton-shimmer';
      case 'none':
      default:
        return '';
    }
  };

  const style: React.CSSProperties = {
    width: width,
    height: height,
  };

  return (
    <div
      className={`bg-gray-700 ${getVariantClasses()} ${getAnimationClasses()} ${className}`}
      style={style}
    />
  );
}

// Agent Card Skeleton
export function AgentCardSkeleton() {
  return (
    <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
      <div className="flex items-center gap-3">
        <Skeleton variant="circular" width={40} height={40} />
        <div className="flex-1 space-y-2">
          <Skeleton width="60%" height={16} />
          <Skeleton width="40%" height={12} />
        </div>
      </div>
      <div className="mt-3 space-y-2">
        <Skeleton width="100%" height={8} />
        <Skeleton width="80%" height={8} />
      </div>
    </div>
  );
}

// Task Card Skeleton
export function TaskCardSkeleton() {
  return (
    <div className="p-3 bg-gray-700/50 rounded-lg">
      <div className="flex items-start gap-2">
        <Skeleton variant="circular" width={14} height={14} />
        <div className="flex-1 space-y-2">
          <Skeleton width="70%" height={14} />
          <Skeleton width="50%" height={10} />
        </div>
        <Skeleton variant="rounded" width={24} height={16} />
      </div>
    </div>
  );
}

// Pipeline Plan Skeleton
export function PipelinePlanSkeleton() {
  return (
    <div className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
      <div className="flex items-center justify-between mb-3">
        <Skeleton width="50%" height={18} />
        <Skeleton variant="rounded" width={60} height={20} />
      </div>
      <Skeleton width="100%" height={12} className="mb-2" />
      <Skeleton width="80%" height={12} className="mb-3" />
      <div className="space-y-2">
        <Skeleton width="100%" height={24} />
        <Skeleton width="100%" height={24} />
        <Skeleton width="100%" height={24} />
      </div>
    </div>
  );
}

// Chat Message Skeleton
export function ChatMessageSkeleton() {
  return (
    <div className="flex gap-3 p-3">
      <Skeleton variant="circular" width={32} height={32} />
      <div className="flex-1 space-y-2">
        <Skeleton width="30%" height={12} />
        <Skeleton width="100%" height={14} />
        <Skeleton width="90%" height={14} />
      </div>
    </div>
  );
}

// Stat Card Skeleton
export function StatCardSkeleton() {
  return (
    <div className="bg-gray-700/50 rounded p-3 text-center">
      <Skeleton width="60%" height={24} className="mx-auto mb-1" />
      <Skeleton width="40%" height={10} className="mx-auto" />
    </div>
  );
}

// Loading Overlay with Skeleton Grid
interface SkeletonGridProps {
  count?: number;
  type: 'agent' | 'task' | 'plan' | 'message' | 'stat';
}

export function SkeletonGrid({ count = 5, type }: SkeletonGridProps) {
  const skeletonComponents = {
    agent: AgentCardSkeleton,
    task: TaskCardSkeleton,
    plan: PipelinePlanSkeleton,
    message: ChatMessageSkeleton,
    stat: StatCardSkeleton,
  };

  const SkeletonComponent = skeletonComponents[type];

  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonComponent key={i} />
      ))}
    </div>
  );
}

// Delayed Skeleton - Only shows after a delay to prevent flash
interface DelayedSkeletonProps {
  delay?: number;
  children: React.ReactNode;
}

export function DelayedSkeleton({ delay = 500, children }: DelayedSkeletonProps) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShow(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  if (!show) return null;

  return <>{children}</>;
}
