class Player(GameObject):
    """玩家飞船类"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 40, BLUE)
        self.speed = GameConfig.player_speed
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # 射击冷却时间（帧数）
    
    def update(self):
        """更新玩家状态"""
        # 获取键盘输入
        keys = pygame.key.get_pressed()
        
        # 移动控制
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # 限制玩家在屏幕范围内
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def shoot(self) -> 'Bullet':
        """发射子弹"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_delay
            return Bullet(self.x + self.width // 2 - 2, self.y)
        return None
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
        if self.health <= 0:
            self.active = False
    
    def draw(self, screen):
        """绘制玩家飞船"""
        # 绘制飞船主体
        pygame.draw.polygon(screen, self.color, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        
        # 绘制生命值条
        bar_width = 40
        bar_height = 5
        bar_x = self.x
        bar_y = self.y - 10
        
        # 背景
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        # 当前生命值
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))