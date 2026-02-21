class GameObject:
    def __init__(self, x, y, width, height, speed=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.active = True
    
    def get_rect(self):
        """返回对象的矩形边界"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """绘制对象（子类应实现）"""
        pass
    
    def update(self):
        """更新对象状态（子类应实现）"""
        pass

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 30, 5)
        self.health = 100
        self.score = 0
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        elif direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        elif direction == "up" and self.y > 0:
            self.y -= self.speed
        elif direction == "down" and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed

class Enemy(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 25, 2)
        self.health = 30
        self.shoot_timer = 0
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False

class Bullet(GameObject):
    def __init__(self, x, y, direction, owner_type):
        super().__init__(x, y, 5, 15, 8)
        self.direction = direction  # "up" or "down"
        self.owner_type = owner_type  # "player" or "enemy"
    
    def update(self):
        if self.direction == "up":
            self.y -= self.speed
        else:
            self.y += self.speed
        
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False