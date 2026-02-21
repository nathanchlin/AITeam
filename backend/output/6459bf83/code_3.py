class TankGame:
    def __init__(self, width=800, height=600):
        """
        初始化坦克游戏
        
        参数:
            width, height: 游戏窗口尺寸
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("坦克大战")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 创建物理引擎
        self.physics = PhysicsEngine(width, height)
        
        # 创建玩家坦克
        self.player_tank = Tank(width//2, height//2, color=(0, 128, 0))
        
        # 创建敌方坦克
        self.enemy_tanks = [
            Tank(100, 100, angle=45, color=(128, 0, 0)),
            Tank(width-100, height-100, angle=225, color=(128, 0, 0))
        ]
        
        # 所有坦克列表
        self.all_tanks = [self.player_tank] + self.enemy_tanks
    
    def handle_events(self):
        """处理游戏事件"""
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = self.player_tank.shoot(current_time)
                    if bullet:
                        bullet.owner = self.player_tank
                        self.physics.bullets.append(bullet)
        
        # 处理持续按键
        keys = pygame.key.get_pressed()
        
        # 玩家控制
        if keys[pygame.K_w]:
            self.player_tank.move('forward')
        if keys[pygame.K_s]:
            self.player_tank.move('backward')
        if keys[pygame.K_a]:
            self.player_tank.rotate('left')
        if keys[pygame.K_d]:
            self.player_tank.rotate('right')
        if keys[pygame.K_q]:
            self.player_tank.rotate_turret('left')
        if keys[pygame.K_e]:
            self.player_tank.rotate_turret('right')
    
    def update(self):
        """更新游戏状态"""
        # 更新物理引擎
        self.physics.update(self.all_tanks, pygame.time.get_ticks())
        
        # 检查边界碰撞
        for tank in self.all_tanks:
            self.physics.check_wall_collision(tank)
        
        # 简单的AI控制敌方坦克
        for enemy in self.enemy_tanks:
            # 随机移动
            if pygame.time.get_ticks() % 60 == 0:
                direction = 'forward' if pygame.time.get_ticks() % 120 < 60 else 'backward'
                enemy.move(direction)
            
            # 随机旋转
            if pygame.time.get_ticks() % 90 == 0:
                direction = 'left' if pygame.time.get_ticks() % 180 < 90 else 'right'
                enemy.rotate(direction)
            
            # 随机射击
            if pygame.time.get_ticks() % 120 == 0:
                bullet = enemy.shoot(pygame.time.get_ticks())
                if bullet:
                    bullet.owner = enemy
                    self.physics.bullets.append(bullet)
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill((240, 240, 240))  # 浅灰色背景
        
        # 绘制所有坦克
        for tank in self.all_tanks:
            tank.draw(self.screen)
        
        # 绘制所有子弹
        for bullet in self.physics.bullets:
            bullet.draw(self.screen)
        
        # 显示玩家坦克状态
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f"Health: {self.player_tank.health}", True, (0, 0, 0))
        ammo_text = font.render(f"Ammo: {self.player_tank.ammo}", True, (0, 0, 0))
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(ammo_text, (10, 40))
        
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()