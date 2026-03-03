import { useRef, useMemo } from 'react';
import * as THREE from 'three';

export function Ground() {
  const meshRef = useRef<THREE.Mesh>(null);

  // Create a wood floor texture procedurally
  const floorTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d')!;

    // Base wood color
    ctx.fillStyle = '#C4A574';
    ctx.fillRect(0, 0, 512, 512);

    // Wood grain lines
    ctx.strokeStyle = '#A08050';
    ctx.lineWidth = 1;

    // Horizontal planks
    const plankHeight = 64;
    for (let y = 0; y < 512; y += plankHeight) {
      // Plank separator line
      ctx.strokeStyle = '#8B7355';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(512, y);
      ctx.stroke();

      // Wood grain within plank
      ctx.strokeStyle = '#B09060';
      ctx.lineWidth = 0.5;
      for (let i = 0; i < 20; i++) {
        const yOffset = y + Math.random() * plankHeight;
        ctx.beginPath();
        ctx.moveTo(0, yOffset);
        // Wavy grain line
        for (let x = 0; x < 512; x += 20) {
          ctx.lineTo(x, yOffset + Math.sin(x * 0.05) * 3);
        }
        ctx.stroke();
      }

      // Add some variation
      ctx.fillStyle = `rgba(139, 115, 85, ${Math.random() * 0.1})`;
      ctx.fillRect(0, y, 512, plankHeight);
    }

    // Vertical plank separators (staggered)
    ctx.strokeStyle = '#8B7355';
    ctx.lineWidth = 2;
    for (let y = 0; y < 512; y += plankHeight * 2) {
      // First column of planks
      ctx.beginPath();
      ctx.moveTo(256, y);
      ctx.lineTo(256, y + plankHeight);
      ctx.stroke();

      // Second column offset
      ctx.beginPath();
      ctx.moveTo(128, y + plankHeight);
      ctx.lineTo(128, y + plankHeight * 2);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(384, y + plankHeight);
      ctx.lineTo(384, y + plankHeight * 2);
      ctx.stroke();
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(6, 6);

    return texture;
  }, []);

  // Create subtle normal map for wood grain depth
  const normalTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d')!;

    // Neutral normal color
    ctx.fillStyle = '#8080FF';
    ctx.fillRect(0, 0, 256, 256);

    // Add subtle grain detail
    for (let i = 0; i < 100; i++) {
      const x = Math.random() * 256;
      const y = Math.random() * 256;
      ctx.fillStyle = `rgba(128, 128, ${Math.floor(128 + Math.random() * 40)}, 0.3)`;
      ctx.fillRect(x, y, 2 + Math.random() * 4, 1);
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(12, 12);

    return texture;
  }, []);

  return (
    <group>
      {/* Main floor */}
      <mesh
        ref={meshRef}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial
          map={floorTexture}
          normalMap={normalTexture}
          normalScale={new THREE.Vector2(0.3, 0.3)}
          roughness={0.6}
          metalness={0.1}
        />
      </mesh>

      {/* Office carpet/rug area in center */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.01, 0]}
        receiveShadow
      >
        <planeGeometry args={[12, 12]} />
        <meshStandardMaterial
          color="#4A5568"
          roughness={0.9}
          metalness={0}
        />
      </mesh>

      {/* Carpet border */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.015, 0]}
      >
        <ringGeometry args={[5.8, 6, 64]} />
        <meshStandardMaterial
          color="#2D3748"
          roughness={0.8}
        />
      </mesh>
    </group>
  );
}
