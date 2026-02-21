class Ninja:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 50
        self.velocity_y = 0
        self.on_ground = False
        self.jumping = False
        self.attacking = False
        self.attack_timer = 0
        self.facing_right = True
        
    def jump(self):
        if self.on_ground:
            self.velocity_y = -300
            self.on_ground = False
            self.jumping = True
            
    def attack(self):
        self.attacking = True
        self.attack_timer = 0.3  # 攻击持续时间
        
    def update(self, dt):
        # 重力
        if not self.on_ground:
            self.velocity_y += 800 * dt  # 重力加速度
            
        # 更新位置
        self.y += self.velocity_y * dt
        
        # 攻击计时器
        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False
                
    def draw(self, screen):
        # 绘制忍者身体 (绿色)
        pygame.draw.rect(screen, (0, 200, 0), 
                        (self.x - self.width // 2, self.y - self.height, self.width, self.height))
        
        # 绘制忍者头部
        pygame.draw.circle(screen, (0, 150, 0), 
                          (self.x, int(self.y - self.height - 10)), 15)
        
        # 绘制眼睛
        eye_x = self.x + (5 if self.facing_right else -5)
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, int(self.y - self.height - 10)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, int(self.y - self.height - 10)), 1)
        
        # 绘制攻击效果
        if self.attacking:
            # 绘制剑/刀
            sword_length = 40
            sword_x = self.x + (sword_length if self.facing_right else -sword_length)
            pygame.draw.rect(screen, (200, 200, 200), 
                            (sword_x - 3, int(self.y - self.height // 2), 6, sword_length))