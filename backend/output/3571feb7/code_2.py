class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 3
        self.collected = False
        
    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius)
    
    def check_collision(self, player):
        if not self.collected:
            distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
            if distance < player.radius + self.radius:
                self.collected = True
                return True
        return False