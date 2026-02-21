import random
import math

class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0
        
    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.age += dt
        return self.age < self.lifetime
    
    def draw(self, screen):
        alpha = 1 - (self.age / self.lifetime)
        size = int(5 * alpha)
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, count=10, color=(255, 255, 0)):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.5, 1.5)
            self.particles.append(Particle(x, y, color, velocity, lifetime))
    
    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)