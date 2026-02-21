class EnemyBullet:
    def __init__(self, x, y, bullet_type, target=None):
        self.x = x
        self.y = y
        self.type = bullet_type
        self.target = target
        self.speed = self._get_speed()
        self.damage = self._get_damage()
        self.size = self._get_size()
        self.color = self._get_color()
        self.alive = True
        
    def _get_speed(self):
        speed_map = {
            "basic": 5,
            "fast": 7,
            "heavy": 3,
            "homing": 4,
            "spread": 5
        }
        return speed_map.get(self.type, 5)
    
    def _get_damage(self):
        damage_map = {
            "basic": 1,
            "fast": 1,
            "heavy": 2,
            "homing": 1,
            "spread": 1
        }
        return damage_map.get(self.type, 1)
    
    def _get_size(self):
        size_map = {
            "basic": 5,
            "fast": 4,
            "heavy": 8,
            "homing": 6,
            "spread": 5
        }
        return size_map.get(self.type, 5)
    
    def _get_color(self):
        color_map = {
            "basic": (255, 100, 100),
            "fast": (100, 255, 100),
            "heavy": (100, 100, 255),
            "homing": (255, 255, 100),
            "spread": (255, 150, 150)
        }
        return color_map.get(self.type, (255, 100, 100))
    
    def update(self):
        if not self.alive:
            return
            
        if self.type == "homing" and self.target and self.target.alive:
            # 追踪弹逻辑
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        else:
            # 直线移动
            self.y += self.speed
        
        # 检查是否超出屏幕
        if self.y > 800 or self.y < 0 or self.x > 800 or self.x < 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)