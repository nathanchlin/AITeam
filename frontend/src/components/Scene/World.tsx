import { Ground } from './Ground';
import { AgentModel } from './Agent';
import {
  Workstation,
  OfficePlant,
  TV,
  Sofa,
  CoffeeTable,
  WaterCooler,
  Bookshelf,
  MeetingRoom,
} from './OfficeFurniture';
import type { Agent } from '../../types';

interface WorldProps {
  agents: Agent[];
}

export function World({ agents }: WorldProps) {
  // Filter out invalid agents (missing id, name, or position)
  const validAgents = agents.filter(agent =>
    agent && agent.id && agent.name && agent.position
  );

  // Calculate desk positions based on number of agents
  const getDeskPosition = (index: number, total: number): [number, number, number] => {
    const cols = Math.min(Math.ceil(Math.sqrt(total)), 4);
    const rows = Math.ceil(total / cols);
    const spacingX = 4;
    const spacingZ = 5;

    const col = index % cols;
    const row = Math.floor(index / cols);

    const offsetX = -((cols - 1) * spacingX) / 2;
    const offsetZ = -((rows - 1) * spacingZ) / 2 - 2;

    return [offsetX + col * spacingX, 0, offsetZ + row * spacingZ];
  };

  return (
    <group>
      <Ground />

      {/* Main work area with cubicles for each agent */}
      {validAgents.map((agent, index) => (
        <Workstation key={agent.id} position={getDeskPosition(index, validAgents.length)} />
      ))}

      {/* Render all agents */}
      {validAgents.map((agent) => (
        <AgentModel key={agent.id} agent={agent} />
      ))}

      {/* Meeting Room - Left side */}
      <MeetingRoom position={[-12, 0, 5]} />

      {/* Second Meeting Room - Right side */}
      <MeetingRoom position={[12, 0, 5]} />

      {/* Lounge/Relax area - back of office */}
      <group position={[0, 0, -15]}>
        <TV position={[0, 0.5, -3]} size="large" />
        <Sofa position={[-2.5, 0, 0]} color="#6366F1" />
        <Sofa position={[2.5, 0, 0]} color="#6366F1" />
        <CoffeeTable position={[-2.5, 0, 1.2]} />
        <CoffeeTable position={[2.5, 0, 1.2]} />
        <OfficePlant position={[-5, 0, -1]} />
        <OfficePlant position={[5, 0, -1]} />
      </group>

      {/* Side amenities - left */}
      <group position={[-16, 0, -6]}>
        <WaterCooler position={[0, 0, 2]} />
        <Bookshelf position={[0, 0, -1]} />
        <OfficePlant position={[0, 0, -4]} />
      </group>

      {/* Side amenities - right */}
      <group position={[16, 0, -6]}>
        <WaterCooler position={[0, 0, 2]} />
        <Bookshelf position={[0, 0, -1]} />
        <OfficePlant position={[0, 0, -4]} />
      </group>

      {/* Entry/Reception area */}
      <group position={[0, 0, 10]}>
        <Sofa position={[-4, 0, 0]} color="#10B981" />
        <Sofa position={[4, 0, 0]} color="#10B981" />
        <CoffeeTable position={[-4, 0, 1.5]} />
        <CoffeeTable position={[4, 0, 1.5]} />
        <group position={[-7, 0, 0]} scale={1.5}>
          <OfficePlant position={[0, 0, 0]} />
        </group>
        <group position={[7, 0, 0]} scale={1.5}>
          <OfficePlant position={[0, 0, 0]} />
        </group>
      </group>

      {/* Corner decorations */}
      <group position={[-18, 0, -15]} scale={1.8}>
        <OfficePlant position={[0, 0, 0]} />
      </group>
      <group position={[18, 0, -15]} scale={1.8}>
        <OfficePlant position={[0, 0, 0]} />
      </group>
      <group position={[-18, 0, 12]} scale={1.8}>
        <OfficePlant position={[0, 0, 0]} />
      </group>
      <group position={[18, 0, 12]} scale={1.8}>
        <OfficePlant position={[0, 0, 0]} />
      </group>

      {/* Small display screens */}
      <TV position={[-10, 0.5, 4]} size="small" />
      <TV position={[10, 0.5, 4]} size="small" />

      {/* Ceiling lights */}
      <mesh position={[0, 8, -5]} rotation={[0, 0, 0]}>
        <planeGeometry args={[6, 1]} />
        <meshStandardMaterial
          color="#FFFFFF"
          emissive="#FFF8E7"
          emissiveIntensity={0.6}
          transparent
          opacity={0.9}
        />
      </mesh>
      <mesh position={[-10, 8, -5]} rotation={[0, 0, 0]}>
        <planeGeometry args={[4, 1]} />
        <meshStandardMaterial
          color="#FFFFFF"
          emissive="#FFF8E7"
          emissiveIntensity={0.5}
          transparent
          opacity={0.8}
        />
      </mesh>
      <mesh position={[10, 8, -5]} rotation={[0, 0, 0]}>
        <planeGeometry args={[4, 1]} />
        <meshStandardMaterial
          color="#FFFFFF"
          emissive="#FFF8E7"
          emissiveIntensity={0.5}
          transparent
          opacity={0.8}
        />
      </mesh>
      <mesh position={[0, 8, 6]} rotation={[0, 0, 0]}>
        <planeGeometry args={[10, 1]} />
        <meshStandardMaterial
          color="#FFFFFF"
          emissive="#FFF8E7"
          emissiveIntensity={0.5}
          transparent
          opacity={0.8}
        />
      </mesh>

      <fog attach="fog" args={['#E8E0D5', 30, 70]} />
    </group>
  );
}
