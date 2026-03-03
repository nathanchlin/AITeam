import { useMemo } from 'react';
import * as THREE from 'three';

// Low-poly office desk
export function OfficeDesk({ position = [0, 0, 0] as [number, number, number] }) {
  const woodMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#8B7355',
    roughness: 0.7,
    metalness: 0.1,
  }), []);

  const metalMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#4A4A4A',
    roughness: 0.4,
    metalness: 0.8,
  }), []);

  return (
    <group position={position}>
      {/* Desktop */}
      <mesh position={[0, 0.75, 0]} castShadow receiveShadow>
        <boxGeometry args={[1.4, 0.05, 0.7]} />
        <primitive object={woodMaterial} attach="material" />
      </mesh>

      {/* Left leg */}
      <mesh position={[-0.6, 0.35, 0]} castShadow>
        <boxGeometry args={[0.05, 0.7, 0.05]} />
        <primitive object={metalMaterial} attach="material" />
      </mesh>

      {/* Right leg */}
      <mesh position={[0.6, 0.35, 0]} castShadow>
        <boxGeometry args={[0.05, 0.7, 0.05]} />
        <primitive object={metalMaterial} attach="material" />
      </mesh>

      {/* Back leg left */}
      <mesh position={[-0.6, 0.35, 0.3]} castShadow>
        <boxGeometry args={[0.05, 0.7, 0.05]} />
        <primitive object={metalMaterial} attach="material" />
      </mesh>

      {/* Back leg right */}
      <mesh position={[0.6, 0.35, 0.3]} castShadow>
        <boxGeometry args={[0.05, 0.7, 0.05]} />
        <primitive object={metalMaterial} attach="material" />
      </mesh>

      {/* Drawer unit */}
      <mesh position={[0.45, 0.4, -0.1]} castShadow>
        <boxGeometry args={[0.35, 0.35, 0.5]} />
        <primitive object={woodMaterial} attach="material" />
      </mesh>
    </group>
  );
}

// Low-poly office chair
export function OfficeChair({ position = [0, 0, 0] as [number, number, number], color = '#2C3E50' }) {
  const seatMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.6,
    metalness: 0.1,
  }), [color]);

  const metalMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#1A1A1A',
    roughness: 0.3,
    metalness: 0.9,
  }), []);

  return (
    <group position={position}>
      {/* Seat */}
      <mesh position={[0, 0.45, 0]} castShadow>
        <boxGeometry args={[0.4, 0.08, 0.4]} />
        <primitive object={seatMaterial} attach="material" />
      </mesh>

      {/* Seat cushion */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <boxGeometry args={[0.38, 0.06, 0.38]} />
        <primitive object={seatMaterial} attach="material" />
      </mesh>

      {/* Backrest */}
      <mesh position={[0, 0.7, -0.17]} rotation={[0.1, 0, 0]} castShadow>
        <boxGeometry args={[0.38, 0.45, 0.06]} />
        <primitive object={seatMaterial} attach="material" />
      </mesh>

      {/* Center pole */}
      <mesh position={[0, 0.25, 0]} castShadow>
        <cylinderGeometry args={[0.03, 0.03, 0.3, 8]} />
        <primitive object={metalMaterial} attach="material" />
      </mesh>

      {/* Star base */}
      {[0, 72, 144, 216, 288].map((angle, i) => (
        <mesh
          key={i}
          position={[
            Math.sin((angle * Math.PI) / 180) * 0.18,
            0.05,
            Math.cos((angle * Math.PI) / 180) * 0.18,
          ]}
          rotation={[0, (angle * Math.PI) / 180, 0]}
          castShadow
        >
          <boxGeometry args={[0.25, 0.03, 0.04]} />
          <primitive object={metalMaterial} attach="material" />
        </mesh>
      ))}

      {/* Wheels */}
      {[0, 72, 144, 216, 288].map((angle, i) => (
        <mesh
          key={`wheel-${i}`}
          position={[
            Math.sin((angle * Math.PI) / 180) * 0.28,
            0.03,
            Math.cos((angle * Math.PI) / 180) * 0.28,
          ]}
          castShadow
        >
          <sphereGeometry args={[0.03, 8, 8]} />
          <primitive object={metalMaterial} attach="material" />
        </mesh>
      ))}
    </group>
  );
}

// Low-poly computer monitor
export function ComputerMonitor({ position = [0, 0, 0] as [number, number, number] }) {
  const plasticMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#2D2D2D',
    roughness: 0.5,
    metalness: 0.3,
  }), []);

  const screenMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#1E3A5F',
    roughness: 0.1,
    metalness: 0.5,
    emissive: '#1E3A5F',
    emissiveIntensity: 0.3,
  }), []);

  return (
    <group position={position}>
      {/* Screen */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <boxGeometry args={[0.5, 0.35, 0.03]} />
        <primitive object={plasticMaterial} attach="material" />
      </mesh>

      {/* Display area */}
      <mesh position={[0, 0.2, 0.016]}>
        <boxGeometry args={[0.45, 0.3, 0.01]} />
        <primitive object={screenMaterial} attach="material" />
      </mesh>

      {/* Stand neck */}
      <mesh position={[0, 0, 0]} castShadow>
        <boxGeometry args={[0.06, 0.08, 0.04]} />
        <primitive object={plasticMaterial} attach="material" />
      </mesh>

      {/* Stand base */}
      <mesh position={[0, -0.02, 0.02]} castShadow>
        <boxGeometry args={[0.2, 0.02, 0.1]} />
        <primitive object={plasticMaterial} attach="material" />
      </mesh>
    </group>
  );
}

// Low-poly keyboard
export function Keyboard({ position = [0, 0, 0] as [number, number, number] }) {
  return (
    <group position={position}>
      <mesh castShadow>
        <boxGeometry args={[0.35, 0.02, 0.12]} />
        <meshStandardMaterial color="#2D2D2D" roughness={0.5} />
      </mesh>
      {/* Key area */}
      <mesh position={[0, 0.012, 0]}>
        <boxGeometry args={[0.32, 0.005, 0.1]} />
        <meshStandardMaterial color="#3D3D3D" roughness={0.7} />
      </mesh>
    </group>
  );
}

// Low-poly plant
export function OfficePlant({ position = [0, 0, 0] as [number, number, number] }) {
  return (
    <group position={position}>
      {/* Pot */}
      <mesh position={[0, 0.08, 0]} castShadow>
        <cylinderGeometry args={[0.08, 0.06, 0.15, 8]} />
        <meshStandardMaterial color="#C4A484" roughness={0.8} />
      </mesh>

      {/* Soil */}
      <mesh position={[0, 0.15, 0]}>
        <cylinderGeometry args={[0.07, 0.07, 0.02, 8]} />
        <meshStandardMaterial color="#3D2314" roughness={0.9} />
      </mesh>

      {/* Leaves - simple low-poly spheres */}
      <mesh position={[0, 0.28, 0]} castShadow>
        <dodecahedronGeometry args={[0.12]} />
        <meshStandardMaterial color="#228B22" roughness={0.8} />
      </mesh>
      <mesh position={[0.06, 0.32, 0.04]} castShadow>
        <dodecahedronGeometry args={[0.08]} />
        <meshStandardMaterial color="#2E8B2E" roughness={0.8} />
      </mesh>
      <mesh position={[-0.05, 0.3, -0.03]} castShadow>
        <dodecahedronGeometry args={[0.07]} />
        <meshStandardMaterial color="#32CD32" roughness={0.8} />
      </mesh>
    </group>
  );
}

// Low-poly coffee mug
export function CoffeeMug({ position = [0, 0, 0] as [number, number, number], color = '#FFFFFF' }) {
  return (
    <group position={position}>
      {/* Mug body */}
      <mesh position={[0, 0.05, 0]} castShadow>
        <cylinderGeometry args={[0.03, 0.025, 0.08, 8]} />
        <meshStandardMaterial color={color} roughness={0.3} />
      </mesh>

      {/* Handle */}
      <mesh position={[0.04, 0.05, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
        <torusGeometry args={[0.02, 0.005, 8, 16, Math.PI]} />
        <meshStandardMaterial color={color} roughness={0.3} />
      </mesh>

      {/* Coffee inside */}
      <mesh position={[0, 0.08, 0]}>
        <cylinderGeometry args={[0.025, 0.025, 0.01, 8]} />
        <meshStandardMaterial color="#3D2314" roughness={0.2} />
      </mesh>
    </group>
  );
}

// Complete desk setup
export function DeskSetup({ position = [0, 0, 0] as [number, number, number] }) {
  return (
    <group position={position}>
      <OfficeDesk position={[0, 0, 0]} />
      <OfficeChair position={[0, 0, 0.6]} />
      <ComputerMonitor position={[0, 0.95, -0.15]} />
      <Keyboard position={[0, 0.8, 0.1]} />
      <OfficePlant position={[0.5, 0.8, -0.2]} />
      <CoffeeMug position={[-0.5, 0.82, 0.1]} color="#FFFFFF" />
    </group>
  );
}

// Office cubicle/partition walls
export function Cubicle({ position = [0, 0, 0] as [number, number, number] }) {
  const wallMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#E8E0D5',
    roughness: 0.9,
    metalness: 0,
  }), []);

  const frameMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#4A4A4A',
    roughness: 0.5,
    metalness: 0.5,
  }), []);

  return (
    <group position={position}>
      {/* Back wall */}
      <mesh position={[0, 0.75, -0.75]} castShadow receiveShadow>
        <boxGeometry args={[2.2, 1.5, 0.05]} />
        <primitive object={wallMaterial} attach="material" />
      </mesh>
      {/* Back wall frame */}
      <mesh position={[0, 0.75, -0.78]}>
        <boxGeometry args={[2.25, 1.55, 0.02]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* Left wall */}
      <mesh position={[-1.1, 0.75, 0]} rotation={[0, Math.PI / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[1.5, 1.5, 0.05]} />
        <primitive object={wallMaterial} attach="material" />
      </mesh>
      {/* Left wall frame */}
      <mesh position={[-1.13, 0.75, 0]} rotation={[0, Math.PI / 2, 0]}>
        <boxGeometry args={[1.55, 1.55, 0.02]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* Right wall */}
      <mesh position={[1.1, 0.75, 0]} rotation={[0, Math.PI / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[1.5, 1.5, 0.05]} />
        <primitive object={wallMaterial} attach="material" />
      </mesh>
      {/* Right wall frame */}
      <mesh position={[1.13, 0.75, 0]} rotation={[0, Math.PI / 2, 0]}>
        <boxGeometry args={[1.55, 1.55, 0.02]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>
    </group>
  );
}

// Office sofa
export function Sofa({ position = [0, 0, 0] as [number, number, number], color = '#4A5568' }) {
  const fabricMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: color,
    roughness: 0.8,
    metalness: 0,
  }), [color]);

  const legMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#2D2D2D',
    roughness: 0.3,
    metalness: 0.5,
  }), []);

  return (
    <group position={position}>
      {/* Base/seat */}
      <mesh position={[0, 0.25, 0]} castShadow receiveShadow>
        <boxGeometry args={[2, 0.3, 0.8]} />
        <primitive object={fabricMaterial} attach="material" />
      </mesh>

      {/* Seat cushion */}
      <mesh position={[0, 0.42, 0.05]} castShadow>
        <boxGeometry args={[1.9, 0.12, 0.65]} />
        <primitive object={fabricMaterial} attach="material" />
      </mesh>

      {/* Backrest */}
      <mesh position={[0, 0.6, -0.32]} castShadow>
        <boxGeometry args={[2, 0.6, 0.15]} />
        <primitive object={fabricMaterial} attach="material" />
      </mesh>

      {/* Left armrest */}
      <mesh position={[-0.95, 0.45, 0]} castShadow>
        <boxGeometry args={[0.12, 0.35, 0.75]} />
        <primitive object={fabricMaterial} attach="material" />
      </mesh>

      {/* Right armrest */}
      <mesh position={[0.95, 0.45, 0]} castShadow>
        <boxGeometry args={[0.12, 0.35, 0.75]} />
        <primitive object={fabricMaterial} attach="material" />
      </mesh>

      {/* Legs */}
      {[[-0.85, 0.05, 0.3], [0.85, 0.05, 0.3], [-0.85, 0.05, -0.3], [0.85, 0.05, -0.3]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} castShadow>
          <cylinderGeometry args={[0.03, 0.03, 0.1, 8]} />
          <primitive object={legMaterial} attach="material" />
        </mesh>
      ))}
    </group>
  );
}

// Coffee table
export function CoffeeTable({ position = [0, 0, 0] as [number, number, number] }) {
  const glassMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#87CEEB',
    roughness: 0.1,
    metalness: 0.9,
    transparent: true,
    opacity: 0.5,
  }), []);

  const metalMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#4A4A4A',
    roughness: 0.3,
    metalness: 0.9,
  }), []);

  return (
    <group position={position}>
      {/* Glass top */}
      <mesh position={[0, 0.4, 0]} castShadow>
        <boxGeometry args={[1, 0.03, 0.5]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>

      {/* Metal frame */}
      <mesh position={[0, 0.38, 0]}>
        <boxGeometry args={[1.02, 0.02, 0.52]} />
        <primitive object={metalMaterial} attach="material" />
      </mesh>

      {/* Legs */}
      {[[-0.45, 0.2, 0.2], [0.45, 0.2, 0.2], [-0.45, 0.2, -0.2], [0.45, 0.2, -0.2]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} castShadow>
          <boxGeometry args={[0.03, 0.4, 0.03]} />
          <primitive object={metalMaterial} attach="material" />
        </mesh>
      ))}
    </group>
  );
}

// TV / Large display
export function TV({ position = [0, 0, 0] as [number, number, number], size = 'large' as 'small' | 'large' }) {
  const frameMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#1A1A1A',
    roughness: 0.3,
    metalness: 0.5,
  }), []);

  const screenMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#1E3A5F',
    roughness: 0.1,
    metalness: 0.3,
    emissive: '#1E3A5F',
    emissiveIntensity: 0.5,
  }), []);

  const dimensions = size === 'large' ? { w: 2.5, h: 1.5, d: 0.08 } : { w: 1.2, h: 0.7, d: 0.05 };

  return (
    <group position={position}>
      {/* Frame */}
      <mesh position={[0, dimensions.h / 2, 0]} castShadow>
        <boxGeometry args={[dimensions.w + 0.1, dimensions.h + 0.1, dimensions.d]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* Screen */}
      <mesh position={[0, dimensions.h / 2, dimensions.d / 2 + 0.01]}>
        <boxGeometry args={[dimensions.w, dimensions.h, 0.01]} />
        <primitive object={screenMaterial} attach="material" />
      </mesh>

      {/* Stand */}
      <mesh position={[0, 0.05, 0]} castShadow>
        <boxGeometry args={[0.3, 0.1, 0.2]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* Stand base */}
      <mesh position={[0, 0.02, 0.05]} castShadow>
        <boxGeometry args={[0.6, 0.04, 0.3]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>
    </group>
  );
}

// Water cooler
export function WaterCooler({ position = [0, 0, 0] as [number, number, number] }) {
  return (
    <group position={position}>
      {/* Body */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <boxGeometry args={[0.35, 1, 0.35]} />
        <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
      </mesh>

      {/* Water bottle */}
      <mesh position={[0, 1.15, 0]} castShadow>
        <cylinderGeometry args={[0.12, 0.12, 0.3, 8]} />
        <meshStandardMaterial color="#87CEEB" roughness={0.1} transparent opacity={0.7} />
      </mesh>

      {/* Tap area */}
      <mesh position={[0, 0.6, 0.18]} castShadow>
        <boxGeometry args={[0.1, 0.15, 0.05]} />
        <meshStandardMaterial color="#4A4A4A" roughness={0.3} metalness={0.5} />
      </mesh>

      {/* Base */}
      <mesh position={[0, 0.02, 0]} castShadow>
        <boxGeometry args={[0.38, 0.04, 0.38]} />
        <meshStandardMaterial color="#E0E0E0" roughness={0.5} />
      </mesh>
    </group>
  );
}

// Bookshelf
export function Bookshelf({ position = [0, 0, 0] as [number, number, number] }) {
  const woodMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#8B7355',
    roughness: 0.7,
    metalness: 0.1,
  }), []);

  return (
    <group position={position}>
      {/* Back panel */}
      <mesh position={[0, 0.6, -0.15]} castShadow>
        <boxGeometry args={[1.2, 1.2, 0.03]} />
        <primitive object={woodMaterial} attach="material" />
      </mesh>

      {/* Side panels */}
      <mesh position={[-0.6, 0.6, 0]} castShadow>
        <boxGeometry args={[0.03, 1.2, 0.3]} />
        <primitive object={woodMaterial} attach="material" />
      </mesh>
      <mesh position={[0.6, 0.6, 0]} castShadow>
        <boxGeometry args={[0.03, 1.2, 0.3]} />
        <primitive object={woodMaterial} attach="material" />
      </mesh>

      {/* Shelves */}
      {[0.1, 0.4, 0.7, 1.0].map((y, i) => (
        <mesh key={i} position={[0, y, 0]} castShadow>
          <boxGeometry args={[1.17, 0.03, 0.28]} />
          <primitive object={woodMaterial} attach="material" />
        </mesh>
      ))}

      {/* Books */}
      {[
        { pos: [-0.4, 0.55, 0], color: '#3B82F6', w: 0.08 },
        { pos: [-0.25, 0.55, 0], color: '#10B981', w: 0.1 },
        { pos: [-0.1, 0.55, 0], color: '#F59E0B', w: 0.07 },
        { pos: [0.1, 0.55, 0], color: '#EF4444', w: 0.09 },
        { pos: [0.3, 0.55, 0], color: '#8B5CF6', w: 0.08 },
        { pos: [-0.35, 0.85, 0], color: '#EC4899', w: 0.1 },
        { pos: [-0.15, 0.85, 0], color: '#06B6D4', w: 0.08 },
        { pos: [0.1, 0.85, 0], color: '#84CC16', w: 0.09 },
      ].map((book, i) => (
        <mesh key={`book-${i}`} position={book.pos as [number, number, number]} castShadow>
          <boxGeometry args={[book.w, 0.2, 0.2]} />
          <meshStandardMaterial color={book.color} roughness={0.8} />
        </mesh>
      ))}
    </group>
  );
}

// Complete workstation with cubicle
export function Workstation({ position = [0, 0, 0] as [number, number, number] }) {
  return (
    <group position={position}>
      <Cubicle position={[0, 0, 0]} />
      <DeskSetup position={[0, 0, 0]} />
    </group>
  );
}

// Lounge area
export function LoungeArea({ position = [0, 0, 0] as [number, number, number] }) {
  return (
    <group position={position}>
      {/* TV on wall */}
      <TV position={[0, 0, -2]} size="large" />

      {/* Sofas */}
      <Sofa position={[-2, 0, 0]} color="#4A5568" />
      <Sofa position={[2, 0, 0]} color="#4A5568" />

      {/* Coffee table */}
      <CoffeeTable position={[0, 0, 0.5]} />

      {/* Side plants */}
      <OfficePlant position={[-3.5, 0, -1]} />
      <OfficePlant position={[3.5, 0, -1]} />
    </group>
  );
}

// Meeting room
export function MeetingRoom({ position = [0, 0, 0] as [number, number, number] }) {
  const wallMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#F5F5F5',
    roughness: 0.9,
    metalness: 0,
    transparent: true,
    opacity: 0.7,
  }), []);

  const glassMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#87CEEB',
    roughness: 0.1,
    metalness: 0.3,
    transparent: true,
    opacity: 0.3,
  }), []);

  const frameMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#4A4A4A',
    roughness: 0.3,
    metalness: 0.7,
  }), []);

  return (
    <group position={position}>
      {/* Floor carpet */}
      <mesh position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[6, 5]} />
        <meshStandardMaterial color="#374151" roughness={0.9} />
      </mesh>

      {/* Back wall */}
      <mesh position={[0, 1.5, -2.5]} castShadow receiveShadow>
        <boxGeometry args={[6, 3, 0.1]} />
        <primitive object={wallMaterial} attach="material" />
      </mesh>

      {/* Left wall with glass */}
      <mesh position={[-3, 1.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.1, 3, 5]} />
        <primitive object={wallMaterial} attach="material" />
      </mesh>

      {/* Right wall with glass window */}
      <mesh position={[3, 1.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.1, 3, 5]} />
        <primitive object={wallMaterial} attach="material" />
      </mesh>
      {/* Glass window on right */}
      <mesh position={[2.95, 1.5, 0]}>
        <boxGeometry args={[0.02, 2, 3]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>
      {/* Window frame */}
      <mesh position={[2.93, 1.5, 0]}>
        <boxGeometry args={[0.03, 2.1, 3.1]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* Meeting table */}
      <mesh position={[0, 0.4, 0]} castShadow receiveShadow>
        <boxGeometry args={[3, 0.05, 1.5]} />
        <meshStandardMaterial color="#5D4E37" roughness={0.6} />
      </mesh>
      {/* Table legs */}
      {[[-1.3, 0.2, 0.6], [1.3, 0.2, 0.6], [-1.3, 0.2, -0.6], [1.3, 0.2, -0.6]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} castShadow>
          <cylinderGeometry args={[0.05, 0.05, 0.4, 8]} />
          <meshStandardMaterial color="#4A4A4A" roughness={0.3} metalness={0.5} />
        </mesh>
      ))}

      {/* Meeting chairs - 6 chairs around table */}
      {[
        [-1, 0, 1.2], [0, 0, 1.2], [1, 0, 1.2],
        [-1, 0, -1.2], [0, 0, -1.2], [1, 0, -1.2],
      ].map((pos, i) => (
        <group key={i} position={pos as [number, number, number]} rotation={[0, i < 3 ? 0 : Math.PI, 0]}>
          {/* Chair seat */}
          <mesh position={[0, 0.45, 0]} castShadow>
            <boxGeometry args={[0.4, 0.05, 0.4]} />
            <meshStandardMaterial color="#1E3A5F" roughness={0.7} />
          </mesh>
          {/* Chair back */}
          <mesh position={[0, 0.7, -0.17]} castShadow>
            <boxGeometry args={[0.35, 0.45, 0.05]} />
            <meshStandardMaterial color="#1E3A5F" roughness={0.7} />
          </mesh>
          {/* Chair base */}
          <mesh position={[0, 0.22, 0]} castShadow>
            <cylinderGeometry args={[0.03, 0.03, 0.3, 8]} />
            <meshStandardMaterial color="#4A4A4A" roughness={0.3} metalness={0.5} />
          </mesh>
          {/* Chair wheels base */}
          <mesh position={[0, 0.05, 0]} castShadow>
            <cylinderGeometry args={[0.15, 0.15, 0.02, 5]} />
            <meshStandardMaterial color="#4A4A4A" roughness={0.3} metalness={0.5} />
          </mesh>
        </group>
      ))}

      {/* Whiteboard/Screen on back wall */}
      <mesh position={[0, 1.8, -2.45]} castShadow>
        <boxGeometry args={[2.5, 1.2, 0.05]} />
        <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
      </mesh>
      {/* Whiteboard frame */}
      <mesh position={[0, 1.8, -2.48]}>
        <boxGeometry args={[2.6, 1.3, 0.02]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* Ceiling light */}
      <mesh position={[0, 2.9, 0]}>
        <boxGeometry args={[2, 0.1, 1]} />
        <meshStandardMaterial
          color="#FFFFFF"
          emissive="#FFF8E7"
          emissiveIntensity={0.8}
        />
      </mesh>
    </group>
  );
}

// Waypoint markers for agent walking paths
export const OFFICE_WAYPOINTS = {
  // Work area positions
  desks: [
    { x: -6, z: -2 },
    { x: -2, z: -2 },
    { x: 2, z: -2 },
    { x: 6, z: -2 },
    { x: -6, z: -7 },
    { x: -2, z: -7 },
    { x: 2, z: -7 },
    { x: 6, z: -7 },
  ],
  // Lounge area
  lounge: [
    { x: -2.5, z: -12 },
    { x: 2.5, z: -12 },
    { x: 0, z: -11 },
  ],
  // Meeting room
  meetingRoom: [
    { x: -10, z: 5 },
    { x: -8, z: 5 },
    { x: -9, z: 3 },
  ],
  // Entry area
  entry: [
    { x: -3, z: 8 },
    { x: 3, z: 8 },
    { x: 0, z: 7 },
  ],
  // Water cooler areas
  amenities: [
    { x: -12, z: -4 },
    { x: 12, z: -4 },
  ],
};
