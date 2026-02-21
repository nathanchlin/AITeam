class BulletManager:
    def __init__(self):
        self.player_bullets: List[Bullet] = []
        self.enemy_bullets: List[Bullet] = []
        self.bullet_effects = []  # 存储子弹特效
    
    def add_player_bullet(self, x: float, y: float, bullet_type: BulletType):
        """添加玩家子弹"""
        if bullet_type == BulletType.PLAYER_NORMAL:
            bullet = Bullet(x, y, bullet_type, damage=1, speed=8, 
                          direction=(0, -1), color=(0, 255, 255), size=4)
            self.player_bullets.append(bullet)
            
        elif bullet_type == BulletType.PLAYER_DOUBLE:
            # 双发子弹
            left_bullet = Bullet(x - 10, y, bullet_type, damage=1, speed=8, 
                               direction=(-0.2, -1), color=(0, 255, 255), size=4)
            right_bullet = Bullet(x + 10, y, bullet_type, damage=1, speed=8, 
                                direction=(0.2, -1), color=(0, 255, 255), size=4)
            self.player_bullets.extend([left_bullet, right_bullet])
            
        elif bullet_type == BulletType.PLAYER_SPREAD:
            # 扇形子弹
            angles = [-30, -15, 0, 15, 30]  # 度数
            for angle in angles:
                rad = pygame.math.Vector2(0, -1).rotate(angle)
                bullet = Bullet(x, y, bullet_type, damage=1, speed=7, 
                              direction=(rad.x, rad.y), color=(255, 200, 0), size=3)
                self.player_bullets.append(bullet)
    
    def add_enemy_bullet(self, x: float, y: float, bullet_type: BulletType):
        """添加敌人子弹"""
        if bullet_type == BulletType.ENEMY_NORMAL:
            bullet = Bullet(x, y, bullet_type, damage=1, speed=4, 
                          direction=(0, 1), color=(255, 50, 50), size=3)
            self.enemy_bullets.append(bullet)
            
        elif bullet_type == BulletType.ENEMY_FAST:
            bullet = Bullet(x, y, bullet_type, damage=1, speed=7, 
                          direction=(0, 1), color=(255, 100, 0), size=2)
            self.enemy_bullets.append(bullet)
            
        elif bullet_type == BulletType.ENEMY_HEAVY:
            bullet = Bullet(x, y, bullet_type, damage=3, speed=3, 
                          direction=(0, 1), color=(200, 0, 200), size=6)
            self.enemy_bullets.append(bullet)
    
    def update(self):
        """更新所有子弹"""
        # 更新玩家子弹
        for bullet in self.player_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.player_bullets.remove(bullet)
        
        # 更新敌人子弹
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)
    
    def draw(self, screen):
        """绘制所有子弹"""
        for bullet in self.player_bullets:
            bullet.draw(screen)
        
        for bullet in self.enemy_bullets:
            bullet.draw(screen)
    
    def check_collisions(self, player_rect, enemies):
        """检查子弹碰撞"""
        # 检查玩家子弹与敌人的碰撞
        for bullet in self.player_bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in enemies[:]:
                if bullet_rect.colliderect(enemy.get_rect()):
                    enemy.take_damage(bullet.damage)
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                    break
        
        # 检查敌人子弹与玩家的碰撞
        for bullet in self.enemy_bullets[:]:
            bullet_rect = bullet.get_rect()
            if bullet_rect.colliderect(player_rect):
                # 玩家受到伤害
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
    
    def clear_all(self):
        """清除所有子弹"""
        self.player_bullets.clear()
        self.enemy_bullets.clear()