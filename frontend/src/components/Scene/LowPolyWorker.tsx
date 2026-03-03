import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

interface LowPolyWorkerProps {
  color: string;
  secondaryColor: string;
  status: 'idle' | 'working' | 'waiting' | 'error';
}

// Procedural low-poly office worker character
export function LowPolyWorker({ color, secondaryColor, status }: LowPolyWorkerProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Animation for working state
  useFrame((state) => {
    if (!groupRef.current) return;
    if (status === 'working') {
      // Subtle typing animation
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 3) * 0.02;
    }
  });

  // Create materials
  const skinMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#E8BEAC',
    roughness: 0.8,
    metalness: 0,
  }), []);

  const hairMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#3D2314',
    roughness: 0.9,
    metalness: 0,
  }), []);

  const shirtMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: secondaryColor,
    roughness: 0.6,
    metalness: 0.1,
    emissive: secondaryColor,
    emissiveIntensity: 0.1,
  }), [secondaryColor]);

  const tieMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.5,
    metalness: 0.2,
    emissive: color,
    emissiveIntensity: 0.15,
  }), [color]);

  return (
    <group ref={groupRef} scale={[1.2, 1.2, 1.2]}>
      {/* Legs */}
      <mesh position={[-0.12, 0, 0]} castShadow>
        <boxGeometry args={[0.1, 0.4, 0.1]} />
        <meshStandardMaterial color="#2C3E50" roughness={0.8} />
      </mesh>
      <mesh position={[0.12, 0, 0]} castShadow>
        <boxGeometry args={[0.1, 0.4, 0.1]} />
        <meshStandardMaterial color="#2C3E50" roughness={0.8} />
      </mesh>

      {/* Feet */}
      <mesh position={[-0.12, -0.18, 0.03]} castShadow>
        <boxGeometry args={[0.1, 0.06, 0.16]} />
        <meshStandardMaterial color="#1A1A1A" roughness={0.9} />
      </mesh>
      <mesh position={[0.12, -0.18, 0.03]} castShadow>
        <boxGeometry args={[0.1, 0.06, 0.16]} />
        <meshStandardMaterial color="#1A1A1A" roughness={0.9} />
      </mesh>

      {/* Torso / Shirt */}
      <mesh position={[0, 0.45, 0]} castShadow>
        <boxGeometry args={[0.28, 0.35, 0.18]} />
        <primitive object={shirtMaterial} attach="material" />
      </mesh>

      {/* Tie */}
      <mesh position={[0, 0.4, 0.1]} castShadow>
        <boxGeometry args={[0.06, 0.2, 0.02]} />
        <primitive object={tieMaterial} attach="material" />
      </mesh>

      {/* Arms */}
      <group position={[-0.2, 0.5, 0]}>
        {/* Left arm */}
        <mesh position={[0, -0.1, 0]} rotation={[0, 0, 0.2]} castShadow>
          <boxGeometry args={[0.08, 0.25, 0.08]} />
          <primitive object={shirtMaterial} attach="material" />
        </mesh>
        {/* Left hand */}
        <mesh position={[-0.05, -0.25, 0.1]} castShadow>
          <boxGeometry args={[0.06, 0.08, 0.06]} />
          <primitive object={skinMaterial} attach="material" />
        </mesh>
      </group>

      <group position={[0.2, 0.5, 0]}>
        {/* Right arm */}
        <mesh position={[0, -0.1, 0]} rotation={[0, 0, -0.2]} castShadow>
          <boxGeometry args={[0.08, 0.25, 0.08]} />
          <primitive object={shirtMaterial} attach="material" />
        </mesh>
        {/* Right hand */}
        <mesh position={[0.05, -0.25, 0.1]} castShadow>
          <boxGeometry args={[0.06, 0.08, 0.06]} />
          <primitive object={skinMaterial} attach="material" />
        </mesh>
      </group>

      {/* Neck */}
      <mesh position={[0, 0.68, 0]} castShadow>
        <boxGeometry args={[0.08, 0.08, 0.08]} />
        <primitive object={skinMaterial} attach="material" />
      </mesh>

      {/* Head */}
      <mesh position={[0, 0.85, 0]} castShadow>
        <boxGeometry args={[0.22, 0.26, 0.2]} />
        <primitive object={skinMaterial} attach="material" />
      </mesh>

      {/* Hair */}
      <mesh position={[0, 0.98, -0.02]} castShadow>
        <boxGeometry args={[0.24, 0.12, 0.22]} />
        <primitive object={hairMaterial} attach="material" />
      </mesh>

      {/* Eyes */}
      <mesh position={[-0.06, 0.85, 0.1]}>
        <boxGeometry args={[0.04, 0.04, 0.01]} />
        <meshBasicMaterial color={status === 'working' ? '#FBBF24' : '#FFFFFF'} />
      </mesh>
      <mesh position={[0.06, 0.85, 0.1]}>
        <boxGeometry args={[0.04, 0.04, 0.01]} />
        <meshBasicMaterial color={status === 'working' ? '#FBBF24' : '#FFFFFF'} />
      </mesh>

      {/* Eyebrows */}
      <mesh position={[-0.06, 0.9, 0.1]} rotation={[0, 0, 0.1]}>
        <boxGeometry args={[0.05, 0.015, 0.01]} />
        <primitive object={hairMaterial} attach="material" />
      </mesh>
      <mesh position={[0.06, 0.9, 0.1]} rotation={[0, 0, -0.1]}>
        <boxGeometry args={[0.05, 0.015, 0.01]} />
        <primitive object={hairMaterial} attach="material" />
      </mesh>

      {/* Mouth */}
      <mesh position={[0, 0.78, 0.1]}>
        <boxGeometry args={[0.06, 0.015, 0.01]} />
        <meshStandardMaterial color="#C9846B" roughness={0.9} />
      </mesh>

      {/* Ears */}
      <mesh position={[-0.13, 0.85, 0]} castShadow>
        <boxGeometry args={[0.04, 0.08, 0.04]} />
        <primitive object={skinMaterial} attach="material" />
      </mesh>
      <mesh position={[0.13, 0.85, 0]} castShadow>
        <boxGeometry args={[0.04, 0.08, 0.04]} />
        <primitive object={skinMaterial} attach="material" />
      </mesh>

      {/* Status indicator - floating above head */}
      {status === 'working' && (
        <mesh position={[0, 1.3, 0]}>
          <octahedronGeometry args={[0.08]} />
          <meshBasicMaterial color="#FBBF24" />
        </mesh>
      )}

      {status === 'error' && (
        <mesh position={[0, 1.3, 0]}>
          <octahedronGeometry args={[0.08]} />
          <meshBasicMaterial color="#EF4444" />
        </mesh>
      )}
    </group>
  );
}
