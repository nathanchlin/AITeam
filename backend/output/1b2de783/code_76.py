class Enemy(GameObject):
    """敌人类"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 30, 30, RED)
        self.speed = GameConfig.enemy_speed
        self.shoot_cooldown = 0
        self.shoot_delay = random.randint(60, 120)  # 随机射击间隔
        self.health = 30
        self.score_value = 10
    
    def update(self):
        """更新敌人状态"""
        # 向下移动
        self.y += self.speed
        
        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # 如果敌人离开屏幕，标记为非活动状态
        if self.is_off_screen():
            self.active = False
    
    def shoot(self) -> Optional[Bullet]:
        """发射子弹"""
        if self.shoot_cooldown <= 0 and random.random() < 0.01:  # 1%的概率每帧射击
            self.shoot_cooldown = self.shoot_delay
            return Bullet(self.x + self.width // 2 - 2, self.y + self.height, is_enemy_bullet=True)
        return None
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
        if self.health <= 0:
            self.active = False