class Bullet(GameObject):
    """子弹类"""
    def __init__(self, x: float, y: float, is_enemy_bullet: bool = False):
        color = RED if is_enemy_bullet else YELLOW
        super().__init__(x, y, 4, 10, color)
        self.speed = GameConfig.bullet_speed
        self.is_enemy_bullet = is_enemy_bullet
    
    def update(self):
        """更新子弹位置"""
        if self.is_enemy_bullet:
            self.y += self.speed
        else:
            self.y -= self.speed
        
        # 如果子弹离开屏幕，标记为非活动状态
        if self.is_off_screen():
            self.active = False