class AngryBirdsGame:
    def __init__(self, width=800, height=600):
        """初始化游戏"""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("愤怒的小鸟 - 物理引擎演示")
        self.clock = pygame.time.Clock()
        
        # 创建物理引擎
        self.physics = PhysicsEngine(gravity=500, air_resistance=0.02)
        
        # 创建地面
        self.ground = Ground(0, height - 50, width, 50)
        
        # 创建小鸟
        self.bird = Projectile(100, height - 100, 20, mass=1.0, color=(255, 0, 0))
        self.physics.add_object(self.bird)
        
        # 创建目标物体
        self.targets = []
        for i in range(3):
            x = 600 + i * 100
            y = height - 100 - i * 30
            target = PhysicsObject(x, y, 30, mass=0.5, color=(0, 255, 0))
            self.targets.append(target)
            self.physics.add_object(target)
            
        # 游戏状态
        self.launching = False
        self.launch_power = 0
        self.launch_angle = 0
        self.mouse_start = None
        
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.launching:  # 左键
                    self.launching = True
                    self.mouse_start = pygame.mouse.get_pos()
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.launching:  # 左键释放
                    mouse_end = pygame.mouse.get_pos()
                    dx = self.mouse_start[0] - mouse_end[0]
                    dy = self.mouse_start[1] - mouse_end[1]
                    
                    # 计算发射参数
                    power = math.sqrt(dx**2 + dy**2) * 2
                    angle = math.atan2(dy, dx)
                    
                    # 发射小鸟
                    self.bird.launch(power, angle)
                    
                    # 重置状态
                    self.launching = False
                    self.launch_power = 0
                    self.launch_angle = 0
                    self.mouse_start = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.launching and self.mouse_start:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = self.mouse_start[0] - mouse_pos[0]
                    dy = self.mouse_start[1] - mouse_pos[1]
                    self.launch_power = min(math.sqrt(dx**2 + dy**2) * 2, 1000)
                    self.launch_angle = math.atan2(dy, dx)
                    
        return True
        
    def update(self, dt):
        """更新游戏状态"""
        # 更新物理引擎
        self.physics.update(dt)
        
        # 检测地面碰撞
        self.ground.check_collision(self.bird)
        for target in self.targets:
            self.ground.check_collision(target)
            
        # 检测对象间碰撞
        self.physics.check_collisions()
        
        # 如果小鸟飞出屏幕或停止移动，重置它
        if (self.bird.x < -50 or self.bird.x > self.screen.get_width() + 50 or 
            self.bird.y > self.screen.get_height() + 50 or
            (abs(self.bird.velocity_x) < 1 and abs(self.bird.velocity_y) < 1 and self.bird.y > self.screen.get_height() - 100)):
            self.reset_bird()
            
    def reset_bird(self):
        """重置小鸟位置"""
        self.bird.x = 100
        self.bird.y = self.screen.get_height() - 100
        self.bird.velocity_x = 0
        self.bird.velocity_y = 0
        self.bird.trail = []
        
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill((135, 206, 235))  # 天蓝色背景
        
        # 绘制地面
        self.ground.draw(self.screen)
        
        # 绘制目标物体
        for target in self.targets:
            target.draw(self.screen)
            
        # 绘制小鸟
        self.bird.draw(self.screen)
        
        # 如果正在发射，绘制发射指示器
        if self.launching and self.mouse_start:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, (255, 255, 255), self.mouse_start, mouse_pos, 2)
            
            # 绘制力度指示器
            power_text = f"Power: {int(self.launch_power)}"
            font = pygame.font.SysFont(None, 24)
            text = font.render(power_text, True, (255, 255, 255))
            self.screen.blit(text, (mouse_pos[0] + 10, mouse_pos[1] - 20))
            
        pygame.display.flip()
        
    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # 转换为秒
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()

# 启动游戏
if __name__ == "__main__":
    game = AngryBirdsGame()
    game.run()