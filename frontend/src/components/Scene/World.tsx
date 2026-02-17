import { Ground } from './Ground';
import { AgentModel } from './Agent';
import type { Agent } from '../../types';

interface WorldProps {
  agents: Agent[];
}

export function World({ agents }: WorldProps) {
  return (
    <group>
      <Ground />

      {/* Render all agents */}
      {agents.map((agent) => (
        <AgentModel key={agent.id} agent={agent} />
      ))}

      {/* Environment elements */}
      <fog attach="fog" args={['#1a1a2e', 15, 30]} />
    </group>
  );
}
