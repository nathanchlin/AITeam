import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Float, DragControls } from '@react-three/drei';
import * as THREE from 'three';
import { useAgentStore } from '../../stores/agentStore';
import type { Agent } from '../../types';
import { AGENT_COLORS, getAgentDisplayType } from '../../types';

interface AgentModelProps {
  agent: Agent;
}

export function AgentModel({ agent }: AgentModelProps) {
  const meshRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const { selectAgent, selectedAgentId, updateAgentPosition } = useAgentStore();

  const isSelected = selectedAgentId === agent.id;
  const colors = AGENT_COLORS[agent.type];

  // Animation based on status
  useFrame((state) => {
    if (!meshRef.current) return;

    // Skip position animation when dragging
    if (isDragging) return;

    // Idle animation - gentle floating
    if (agent.status === 'idle') {
      meshRef.current.position.y = agent.position.y + Math.sin(state.clock.elapsedTime * 2) * 0.1;
    }

    // Working animation - slight shake
    if (agent.status === 'working') {
      meshRef.current.position.y = agent.position.y;
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 10) * 0.05;
    }

    // Scale on hover
    const targetScale = hovered ? 1.1 : isSelected ? 1.05 : 1;
    meshRef.current.scale.lerp(
      new THREE.Vector3(targetScale, targetScale, targetScale),
      0.1
    );
  });

  const handleClick = () => {
    selectAgent(isSelected ? null : agent.id);
  };

  return (
    <DragControls
      onDragStart={() => setIsDragging(true)}
      onDragEnd={() => {
        setIsDragging(false);
        // Update position from mesh ref
        if (meshRef.current) {
          const newPosition = {
            x: meshRef.current.position.x,
            y: 0, // Keep on ground level
            z: meshRef.current.position.z,
          };
          updateAgentPosition(agent.id, newPosition);
        }
      }}
    >
      <group
        ref={meshRef}
        position={[agent.position.x, agent.position.y + 0.5, agent.position.z]}
        onClick={handleClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
      {/* Agent body - stylized robot/character */}
      <Float speed={agent.status === 'idle' && !isDragging ? 1.5 : 0} floatIntensity={0.3}>
        {/* Main body */}
        <mesh castShadow position={[0, 0.5, 0]}>
          <capsuleGeometry args={[0.4, 0.8, 8, 16]} />
          <meshStandardMaterial
            color={colors.primary}
            roughness={0.3}
            metalness={0.7}
            emissive={colors.primary}
            emissiveIntensity={hovered ? 0.3 : 0.1}
          />
        </mesh>

        {/* Head */}
        <mesh castShadow position={[0, 1.3, 0]}>
          <sphereGeometry args={[0.3, 16, 16]} />
          <meshStandardMaterial
            color={colors.secondary}
            roughness={0.2}
            metalness={0.8}
            emissive={colors.secondary}
            emissiveIntensity={0.2}
          />
        </mesh>

        {/* Eyes */}
        <group position={[0, 1.35, 0.2]}>
          <mesh position={[-0.1, 0, 0]}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshBasicMaterial color={agent.status === 'working' ? '#fbbf24' : '#ffffff'} />
          </mesh>
          <mesh position={[0.1, 0, 0]}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshBasicMaterial color={agent.status === 'working' ? '#fbbf24' : '#ffffff'} />
          </mesh>
        </group>

        {/* Status indicator */}
        {agent.status === 'working' && (
          <mesh position={[0, 1.8, 0]}>
            <torusGeometry args={[0.15, 0.03, 8, 16]} />
            <meshBasicMaterial color="#fbbf24" />
          </mesh>
        )}

        {agent.status === 'error' && (
          <mesh position={[0, 1.8, 0]}>
            <octahedronGeometry args={[0.2]} />
            <meshBasicMaterial color="#ef4444" />
          </mesh>
        )}

        {/* Base platform */}
        <mesh receiveShadow position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <circleGeometry args={[0.5, 32]} />
          <meshStandardMaterial
            color={colors.light}
            transparent
            opacity={0.5}
            roughness={0.1}
            metalness={0.9}
          />
        </mesh>
      </Float>

      {/* Selection ring */}
      {isSelected && (
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
          <ringGeometry args={[0.6, 0.7, 32]} />
          <meshBasicMaterial color={colors.primary} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Name label */}
      <Html
        position={[0, 2, 0]}
        center
        zIndexRange={[5, 0]}
        style={{
          pointerEvents: 'none',
          whiteSpace: 'nowrap',
        }}
      >
        <div className="bg-gray-800/80 px-2 py-1 rounded text-xs text-white whitespace-nowrap">
          {agent.name}
          <span className="ml-1 text-gray-400">({getAgentDisplayType(agent)})</span>
        </div>
      </Html>

      {/* Progress bar for working status */}
      {agent.status === 'working' && agent.current_task_id && (
        <Html position={[0, 2.3, 0]} center zIndexRange={[5, 0]}>
          <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-yellow-500 animate-pulse"
              style={{ width: '60%' }}
            />
          </div>
        </Html>
      )}
    </group>
    </DragControls>
  );
}
