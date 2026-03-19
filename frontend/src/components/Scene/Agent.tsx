import { useRef, useState, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Float } from '@react-three/drei';
import * as THREE from 'three';
import { useAgentStore } from '../../stores/agentStore';
import type { Agent, DiscussionMessage } from '../../types';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';
import { LowPolyWorker } from './LowPolyWorker';

interface AgentModelProps {
  agent: Agent;
}

// Navigation graph
interface NavNode {
  id: string;
  x: number;
  z: number;
  type: 'desk' | 'lounge' | 'meeting' | 'entry' | 'amenity' | 'corridor';
  connections: string[];
}

const NAV_GRAPH: NavNode[] = [
  { id: 'corridor-1', x: 0, z: 0, type: 'corridor', connections: ['corridor-2', 'corridor-3', 'desk-center'] },
  { id: 'corridor-2', x: -6, z: 0, type: 'corridor', connections: ['corridor-1', 'corridor-4', 'meeting-left-entrance'] },
  { id: 'corridor-3', x: 6, z: 0, type: 'corridor', connections: ['corridor-1', 'corridor-5', 'meeting-right-entrance'] },
  { id: 'corridor-4', x: -6, z: 5, type: 'corridor', connections: ['corridor-2', 'entry-left', 'meeting-left-entrance'] },
  { id: 'corridor-5', x: 6, z: 5, type: 'corridor', connections: ['corridor-3', 'entry-right', 'meeting-right-entrance'] },
  { id: 'corridor-6', x: 0, z: 5, type: 'corridor', connections: ['corridor-1', 'entry-center'] },
  { id: 'corridor-7', x: 0, z: -5, type: 'corridor', connections: ['corridor-1', 'lounge-entrance', 'desk-back'] },
  { id: 'desk-center', x: 0, z: -2, type: 'desk', connections: ['corridor-1'] },
  { id: 'desk-left', x: -4, z: -2, type: 'desk', connections: ['corridor-2'] },
  { id: 'desk-right', x: 4, z: -2, type: 'desk', connections: ['corridor-3'] },
  { id: 'lounge-entrance', x: 0, z: -12, type: 'corridor', connections: ['corridor-7', 'lounge-1', 'lounge-2'] },
  { id: 'lounge-1', x: -2.5, z: -15, type: 'lounge', connections: ['lounge-entrance'] },
  { id: 'lounge-2', x: 2.5, z: -15, type: 'lounge', connections: ['lounge-entrance'] },
  { id: 'meeting-left-1', x: -11, z: 5, type: 'meeting', connections: ['meeting-left-entrance'] },
  { id: 'meeting-left-2', x: -9, z: 3, type: 'meeting', connections: ['meeting-left-1'] },
  { id: 'meeting-left-3', x: -9, z: 7, type: 'meeting', connections: ['meeting-left-1'] },
  { id: 'meeting-left-entrance', x: -9, z: 5, type: 'corridor', connections: ['corridor-4', 'meeting-left-1'] },
  { id: 'meeting-right-1', x: 11, z: 5, type: 'meeting', connections: ['meeting-right-entrance'] },
  { id: 'meeting-right-2', x: 9, z: 3, type: 'meeting', connections: ['meeting-right-1'] },
  { id: 'meeting-right-3', x: 9, z: 7, type: 'meeting', connections: ['meeting-right-1'] },
  { id: 'meeting-right-entrance', x: 9, z: 5, type: 'corridor', connections: ['corridor-5', 'meeting-right-1'] },
  { id: 'entry-center', x: 0, z: 9, type: 'entry', connections: ['corridor-6'] },
  { id: 'entry-left', x: -4, z: 10, type: 'entry', connections: ['corridor-4'] },
  { id: 'entry-right', x: 4, z: 10, type: 'entry', connections: ['corridor-5'] },
];

const MEETING_SEATS = {
  left: ['meeting-left-1', 'meeting-left-2', 'meeting-left-3'],
  right: ['meeting-right-1', 'meeting-right-2', 'meeting-right-3'],
};

function findNode(id: string): NavNode | undefined {
  return NAV_GRAPH.find(n => n.id === id);
}

function findNearestNode(x: number, z: number): NavNode {
  let nearest = NAV_GRAPH[0];
  let minDist = Infinity;
  for (const node of NAV_GRAPH) {
    const dist = Math.sqrt((node.x - x) ** 2 + (node.z - z) ** 2);
    if (dist < minDist) {
      minDist = dist;
      nearest = node;
    }
  }
  return nearest;
}

function findPath(startId: string, endId: string): string[] {
  if (startId === endId) return [startId];
  const visited = new Set<string>();
  const queue: { nodeId: string; path: string[] }[] = [{ nodeId: startId, path: [startId] }];

  while (queue.length > 0) {
    const current = queue.shift()!;
    const node = findNode(current.nodeId);
    if (!node) continue;

    for (const connId of node.connections) {
      if (connId === endId) return [...current.path, connId];
      if (!visited.has(connId)) {
        visited.add(connId);
        queue.push({ nodeId: connId, path: [...current.path, connId] });
      }
    }
  }
  return [startId];
}

function getRandomDestination(currentId: string): string {
  const types = ['desk', 'lounge', 'meeting', 'entry', 'amenity'] as const;
  const targetType = types[Math.floor(Math.random() * types.length)];
  const candidates = NAV_GRAPH.filter(n => n.type === targetType && n.id !== currentId);
  return candidates.length > 0 ? candidates[Math.floor(Math.random() * candidates.length)].id : currentId;
}

export function AgentModel({ agent }: AgentModelProps) {
  const meshRef = useRef<THREE.Group>(null);
  const workingRingRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const { selectAgent, selectedAgentId, updateAgentPosition } = useAgentStore();

  // Navigation state
  const [currentNodeId, setCurrentNodeId] = useState<string>('');
  const [path, setPath] = useState<string[]>([]);
  const [pathIndex, setPathIndex] = useState(0);
  const [isWalking, setIsWalking] = useState(false);
  const [walkSpeed] = useState(1.2 + Math.random() * 0.4);

  // Behavior state
  const [behaviorMode, setBehaviorMode] = useState<'idle' | 'meeting' | 'working' | 'celebrating'>('idle');

  // Speech bubble state
  const [currentSpeech, setCurrentSpeech] = useState<string | null>(null);

  // Get store state
  const plans = useAgentStore((state) => state.plans);
  const currentPlanId = useAgentStore((state) => state.currentPlanId);

  // Home position
  const homeNode = useMemo(() => {
    const deskNodes = NAV_GRAPH.filter(n => n.type === 'desk');
    if (deskNodes.length === 0) {
      return NAV_GRAPH[0]; // Fallback to first node
    }
    // Defensive: ensure agent.id exists before slicing
    const agentIdSafe = agent.id || '0';
    const index = parseInt(agentIdSafe.slice(-1), 16) % deskNodes.length;
    return deskNodes[index];
  }, [agent.id]);

  const isSelected = selectedAgentId === agent.id;
  const colors = AGENT_COLORS[agent.type] || { primary: '#6B7280', secondary: '#9CA3AF', light: '#D1D5DB' };

  // Initialize
  useEffect(() => {
    // Defensive: ensure agent.position exists
    const pos = agent.position || { x: 0, y: 0, z: 0 };
    const nearest = findNearestNode(pos.x, pos.z);
    setCurrentNodeId(nearest.id);
  }, [agent.position?.x, agent.position?.z]);

  // Monitor plan status
  useEffect(() => {
    if (!currentPlanId) {
      setBehaviorMode('idle');
      return;
    }

    const currentPlan = plans.find(p => p.id === currentPlanId);
    if (!currentPlan) {
      setBehaviorMode('idle');
      return;
    }

    // Check if agent is selected - if no selected_agent_ids, default to all agents
    const selectedIds = currentPlan.selected_agent_ids || [];
    const isSelectedAgent = selectedIds.length === 0 || selectedIds.includes(agent.id);

    console.log(`[Agent ${agent.name || 'Unknown'}] Plan status: ${currentPlan.status}, isSelected: ${isSelectedAgent}, selectedIds:`, selectedIds);

    switch (currentPlan.status) {
      case 'discussing':
        if (isSelectedAgent) {
          setBehaviorMode('meeting');
          // Always use left meeting room
          const room = 'left';
          // Use all agents if selected_agent_ids is empty
          const effectiveSelectedIds = selectedIds.length > 0 ? selectedIds : useAgentStore.getState().agents.map(a => a.id);
          const seatIdx = effectiveSelectedIds.indexOf(agent.id) % 3;
          const targetSeatId = MEETING_SEATS[room][seatIdx >= 0 ? seatIdx : Math.floor(Math.random() * 3)];
          console.log(`[Agent ${agent.name || 'Unknown'}] Going to meeting room, seat: ${targetSeatId}`);
          const newPath = findPath(currentNodeId || homeNode.id, targetSeatId);
          if (newPath.length > 1) {
            setPath(newPath);
            setPathIndex(1);
            setIsWalking(true);
          }
        }
        break;

      case 'executing':
        if (isSelectedAgent) {
          setBehaviorMode('working');
          const newPath = findPath(currentNodeId || homeNode.id, homeNode.id);
          if (newPath.length > 1) {
            setPath(newPath);
            setPathIndex(1);
            setIsWalking(true);
          }
        }
        break;

      case 'completed':
        if (isSelectedAgent) {
          setBehaviorMode('celebrating');
          const loungeNodes = NAV_GRAPH.filter(n => n.type === 'lounge');
          const targetLounge = loungeNodes[Math.floor(Math.random() * loungeNodes.length)];
          const newPath = findPath(currentNodeId || homeNode.id, targetLounge.id);
          if (newPath.length > 1) {
            setPath(newPath);
            setPathIndex(1);
            setIsWalking(true);
          }
          setTimeout(() => setBehaviorMode('idle'), 15000);
        }
        break;

      default:
        setBehaviorMode('idle');
    }
  }, [currentPlanId, plans, agent.id, currentNodeId, homeNode.id]);

  // Show discussion messages as speech bubbles
  useEffect(() => {
    if (behaviorMode !== 'meeting' || !currentPlanId) return;

    const plan = plans.find(p => p.id === currentPlanId);
    if (!plan) return;

    const allMessages: DiscussionMessage[] = [...(plan.discussion || [])];
    if (plan.iterations) {
      plan.iterations.forEach(iter => {
        if (iter.discussion) allMessages.push(...iter.discussion);
      });
    }

    const recentMessage = allMessages
      .filter(msg => msg.agent_id === agent.id)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];

    if (recentMessage) {
      const displayText = recentMessage.content.length > 80
        ? recentMessage.content.slice(0, 80) + '...'
        : recentMessage.content;
      setCurrentSpeech(displayText);
      const timeout = setTimeout(() => setCurrentSpeech(null), 5000);
      return () => clearTimeout(timeout);
    }
  }, [behaviorMode, plans, currentPlanId, agent.id]);

  // Random walking when idle
  useEffect(() => {
    if (behaviorMode !== 'idle' || agent.status !== 'idle' || isWalking) return;

    const walkTimer = setTimeout(() => {
      if (Math.random() > 0.4) {
        const destId = getRandomDestination(currentNodeId || homeNode.id);
        const newPath = findPath(currentNodeId || homeNode.id, destId);
        if (newPath.length > 1) {
          setPath(newPath);
          setPathIndex(1);
          setIsWalking(true);
        }
      }
    }, 8000 + Math.random() * 15000);

    return () => clearTimeout(walkTimer);
  }, [behaviorMode, agent.status, isWalking, currentNodeId, homeNode.id]);

  // Animation loop
  useFrame((state, delta) => {
    if (!meshRef.current) return;

    if (isWalking && path.length > 0 && pathIndex < path.length) {
      const targetNode = findNode(path[pathIndex]);
      if (!targetNode) {
        setIsWalking(false);
        return;
      }

      const dx = targetNode.x - meshRef.current.position.x;
      const dz = targetNode.z - meshRef.current.position.z;
      const distance = Math.sqrt(dx * dx + dz * dz);

      if (distance > 0.15) {
        const speed = behaviorMode === 'celebrating' ? walkSpeed * 1.5 : walkSpeed;
        meshRef.current.position.x += (dx / distance) * speed * delta;
        meshRef.current.position.z += (dz / distance) * speed * delta;
        meshRef.current.rotation.y = Math.atan2(dx, dz);
        meshRef.current.position.y = Math.abs(Math.sin(state.clock.elapsedTime * 10)) * 0.03;
      } else {
        setCurrentNodeId(targetNode.id);
        setPathIndex(prev => prev + 1);

        if (pathIndex >= path.length - 1) {
          setIsWalking(false);
          setPath([]);
          setPathIndex(0);
          meshRef.current.position.y = 0;
          updateAgentPosition(agent.id, { x: targetNode.x, y: 0, z: targetNode.z });
        }
      }
    } else {
      if (behaviorMode === 'celebrating') {
        meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 3) * 0.3;
        meshRef.current.position.y = Math.abs(Math.sin(state.clock.elapsedTime * 4)) * 0.1;
      } else if (behaviorMode === 'meeting') {
        meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.02;
      } else if (agent.status === 'working') {
        meshRef.current.position.y = Math.abs(Math.sin(state.clock.elapsedTime * 5)) * 0.02;
      } else if (agent.status === 'idle') {
        meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.03;
      } else {
        meshRef.current.position.y = 0;
      }
    }

    const targetScale = hovered ? 1.1 : isSelected ? 1.05 : 1;
    meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);

    // Rotate working ring
    if (workingRingRef.current && agent.status === 'working') {
      workingRingRef.current.rotation.z = state.clock.elapsedTime * 2;
    }
  });

  const getStatusColor = () => {
    switch (behaviorMode) {
      case 'meeting': return '#8B5CF6';
      case 'working': return '#FBBF24';
      case 'celebrating': return '#22C55E';
      default: return isWalking ? '#22C55E' : colors.primary;
    }
  };

  // Defensive: ensure position exists with defaults
  const position = agent.position || { x: 0, y: 0, z: 0 };

  return (
    <group
      ref={meshRef}
      position={[position.x, position.y, position.z]}
      onClick={() => selectAgent(isSelected ? null : agent.id)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
        <Float speed={agent.status === 'idle' && !isWalking && behaviorMode === 'idle' ? 1.5 : 0} floatIntensity={0.08}>
          <group position={[0, 0.35, 0]}>
            <LowPolyWorker color={colors.primary} secondaryColor={colors.light} status={agent.status} />
          </group>
        </Float>

        <mesh receiveShadow position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <circleGeometry args={[0.35, 32]} />
          <meshStandardMaterial color={colors.light} transparent opacity={0.25} roughness={0.8} />
        </mesh>

        {isSelected && (
          <>
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
              <ringGeometry args={[0.4, 0.5, 32]} />
              <meshBasicMaterial color={colors.primary} side={THREE.DoubleSide} />
            </mesh>
            {/* Spotlight cone effect */}
            <mesh position={[0, 2.5, 0]}>
              <coneGeometry args={[0.8, 2, 32, 1, true]} />
              <meshBasicMaterial color={colors.primary} transparent opacity={0.15} side={THREE.DoubleSide} />
            </mesh>
            {/* Spotlight ground glow */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.005, 0]}>
              <circleGeometry args={[0.6, 32]} />
              <meshBasicMaterial color={colors.primary} transparent opacity={0.3} />
            </mesh>
          </>
        )}

        {(isWalking || behaviorMode !== 'idle') && (
          <mesh position={[0, 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.25, 0.3, 32]} />
            <meshBasicMaterial color={getStatusColor()} transparent opacity={0.7} side={THREE.DoubleSide} />
          </mesh>
        )}

        {/* Working status rotating ring */}
        {agent.status === 'working' && (
          <mesh ref={workingRingRef} position={[0, 1.2, 0]}>
            <torusGeometry args={[0.15, 0.02, 8, 32]} />
            <meshBasicMaterial color="#3B82F6" transparent opacity={0.8} />
          </mesh>
        )}

        {/* Error status pulsing warning ring */}
        {agent.status === 'error' && (
          <>
            <mesh position={[0, 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <ringGeometry args={[0.35, 0.45, 32]} />
              <meshBasicMaterial color="#EF4444" transparent opacity={0.6} side={THREE.DoubleSide} />
            </mesh>
            <mesh position={[0, 1.3, 0]}>
              <octahedronGeometry args={[0.12]} />
              <meshBasicMaterial color="#EF4444" />
            </mesh>
          </>
        )}

        {behaviorMode === 'celebrating' && (
          <mesh position={[0, 1.5, 0]}>
            <octahedronGeometry args={[0.1]} />
            <meshBasicMaterial color="#FFD700" />
          </mesh>
        )}

        <Html position={[0, 1.5, 0]} center zIndexRange={[5, 0]} style={{ pointerEvents: 'none', whiteSpace: 'nowrap' }}>
          <div className={`px-3 py-1.5 rounded-lg text-sm text-white whitespace-nowrap shadow-lg backdrop-blur-sm border ${
            agent.status === 'error'
              ? 'bg-red-900/90 border-red-500/50 animate-pulse'
              : 'bg-gray-800/90 border-gray-700/50'
          }`}>
            {agent.name || 'Unknown'}
            <span className="ml-2 text-gray-400">({getAgentDisplayType(agent)})</span>
            {agent.status === 'error' && <span className="ml-2 text-red-400">⚠️</span>}
            {behaviorMode === 'meeting' && <span className="ml-2 text-purple-400">💬</span>}
            {behaviorMode === 'working' && <span className="ml-2 text-yellow-400">⚡</span>}
            {behaviorMode === 'celebrating' && <span className="ml-2">🎉</span>}
            {isWalking && behaviorMode === 'idle' && <span className="ml-2 text-green-400">•</span>}
          </div>
        </Html>

        {currentSpeech && behaviorMode === 'meeting' && (
          <Html position={[0, 2.2, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: 'none' }}>
            <div className="relative max-w-xs bg-white/95 px-4 py-2 rounded-xl text-xs text-gray-800 shadow-lg border border-gray-200">
              <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-white/95" />
              <p className="leading-relaxed">{currentSpeech}</p>
            </div>
          </Html>
        )}

        {behaviorMode === 'meeting' && agent.type === 'assistant' && (
          <Html position={[0, 2.8, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: 'none' }}>
            <div className="bg-purple-600/90 px-3 py-1 rounded-lg text-xs text-white shadow-lg">
              📋 正在制定计划...
            </div>
          </Html>
        )}

        {agent.status === 'working' && agent.current_task_id && (
          <>
            {/* Progress bar */}
            <Html position={[0, 1.8, 0]} center zIndexRange={[5, 0]}>
              <div className="w-20 h-2 bg-gray-700/80 rounded-full overflow-hidden shadow-lg">
                <div className="h-full bg-gradient-to-r from-yellow-500 to-orange-500 animate-pulse" style={{ width: '60%' }} />
              </div>
            </Html>
            {/* Thinking animation dots */}
            <Html position={[0, 2.1, 0]} center zIndexRange={[5, 0]} style={{ pointerEvents: 'none' }}>
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </Html>
          </>
        )}
      </group>
  );
}
