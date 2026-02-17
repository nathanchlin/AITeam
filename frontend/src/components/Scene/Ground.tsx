import { useRef, useMemo } from 'react';
import * as THREE from 'three';

export function Ground() {
  const meshRef = useRef<THREE.Mesh>(null);

  // Create a grid texture procedurally
  const gridTexture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d')!;

    // Background
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, 512, 512);

    // Grid lines
    ctx.strokeStyle = '#2a2a4e';
    ctx.lineWidth = 2;

    // Vertical lines
    for (let i = 0; i <= 16; i++) {
      ctx.beginPath();
      ctx.moveTo(i * 32, 0);
      ctx.lineTo(i * 32, 512);
      ctx.stroke();
    }

    // Horizontal lines
    for (let i = 0; i <= 16; i++) {
      ctx.beginPath();
      ctx.moveTo(0, i * 32);
      ctx.lineTo(512, i * 32);
      ctx.stroke();
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(4, 4);

    return texture;
  }, []);

  return (
    <mesh
      ref={meshRef}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, 0, 0]}
      receiveShadow
    >
      <planeGeometry args={[40, 40]} />
      <meshStandardMaterial
        map={gridTexture}
        side={THREE.DoubleSide}
        roughness={0.8}
        metalness={0.2}
      />
    </mesh>
  );
}
