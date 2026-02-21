class Asteroid(GameObject):
    """陨石类"""
    def __init__(self, x: float, y: float):
        size = random.randint(20, 50)
        super().__init__(x, y, size, size, (150, 150, 150))
        self.speed = random.uniform(1, 3)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.health = size // 10
        self.score_value = size // 5
    
    def update(self):
        """更新陨石状态"""
        # 向下移动
        self.y += self.speed
        
        # 旋转
        self.rotation += self.rotation_speed
        
        # 如果陨石离开屏幕，标记为非活动状态
        if self.is_off_screen():
            self.active = False
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
        if self.health <= 0:
            self.active = False
    
    def draw(self, screen):
        """绘制陨石"""
        # 创建旋转的陨石形状
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (2 * math.pi * i / num_points) + math.radians(self.rotation)
            radius = self.width / 2 + random.uniform(-5, 5)
            x = self.x + self.width / 2 + radius * math.cos(angle)
            y = self.y + self.height / 2 + radius * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(screen, self.color, points)