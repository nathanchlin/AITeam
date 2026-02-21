class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.age += 1
        return self.age < self.lifetime
        
    def draw(self, screen):
        alpha = 1 - (self.age / self.lifetime)
        size = int(3 * alpha)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, count, color, velocity_range, lifetime_range):
        for _ in range(count):
            velocity = (
                random.uniform(velocity_range[0], velocity_range[1]),
                random.uniform(velocity_range[0], velocity_range[1])
            )
            lifetime = random.randint(lifetime_range[0], lifetime_range[1])
            self.particles.append(Particle(x, y, color, velocity, lifetime))
            
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)