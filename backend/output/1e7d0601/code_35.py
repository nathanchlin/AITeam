class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.fire_rate = 10  # 射击间隔（帧数）
        self.fire_cooldown = 0
        self.bullet_type = BulletType.PLAYER_NORMAL
        self.power_level = 1  # 武器等级
    
    def update(self, keys):
        """更新玩家状态"""
        # 移动
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < pygame.display.get_surface().get_width() - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < pygame.display.get_surface().get_height() - self.height:
            self.y += self.speed
        
        # 更新射击冷却
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
    
    def fire(self, bullet_manager):
        """发射子弹"""
        if self.fire_cooldown <= 0:
            center_x = self.x + self.width // 2
            top_y = self.y
            
            if self.power_level == 1:
                bullet_manager.add_player_bullet(center_x, top_y, BulletType.PLAYER_NORMAL)
            elif self.power_level == 2:
                bullet_manager.add_player_bullet(center_x, top_y, BulletType.PLAYER_DOUBLE)
            elif self.power_level >= 3:
                bullet_manager.add_player_bullet(center_x, top_y, BulletType.PLAYER_SPREAD)
            
            self.fire_cooldown = self.fire_rate
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """绘制玩家飞机"""
        # 简单的三角形表示飞机
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, (0, 255, 0), points)
        
        # 绘制驾驶舱
        pygame.draw.circle(screen, (100, 200, 255), 
                         (self.x + self.width // 2, self.y + self.height // 2), 5)

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 2
        self.health = 1
        self.enemy_type = enemy_type
        self.fire_rate = 60  # 射击间隔
        self.fire_cooldown = 0
        self.move_pattern = 0  # 移动模式
        self.move_timer = 0
    
    def update(self, player_x, player_y):
        """更新敌人状态"""
        # 移动模式
        self.move_timer += 1
        
        if self.enemy_type == "normal":
            # 直线移动
            self.y += self.speed
        elif self.enemy_type == "zigzag":
            # 之字形移动
            self.y += self.speed
            self.x += math.sin(self.move_timer * 0.1) * 2
        elif self.enemy_type == "diving":
            # 俯冲移动
            if self.move_timer < 60:
                self.y += self.speed
            else:
                # 向玩家位置移动
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.x += (dx / dist) * self.speed
                    self.y += (dy / dist) * self.speed
        
        # 更新射击冷却
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
    
    def fire(self, bullet_manager):
        """发射子弹"""
        if self.fire_cooldown <= 0:
            center_x = self.x + self.width // 2
            bottom_y = self.y + self.height
            
            if self.enemy_type == "normal":
                bullet_manager.add_enemy_bullet(center_x, bottom_y, BulletType.ENEMY_NORMAL)
            elif self.enemy_type == "fast":
                bullet_manager.add_enemy_bullet(center_x, bottom_y, BulletType.ENEMY_FAST)
            elif self.enemy_type == "heavy":
                bullet_manager.add_enemy_bullet(center_x, bottom_y, BulletType.ENEMY_HEAVY)
            
            self.fire_cooldown = self.fire_rate
    
    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """绘制敌机"""
        if self.enemy_type == "normal":
            color = (255, 0, 0)
        elif self.enemy_type == "fast":
            color = (255, 100, 0)
        else:  # heavy
            color = (200, 0, 200)
        
        # 简单的倒三角形表示敌机
        points = [
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y),
            (self.x + self.width, self.y)
        ]
        pygame.draw.polygon(screen, color, points)