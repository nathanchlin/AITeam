class SpaceShooterGame:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("太空射击游戏")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏对象
        self.player = PlayerShip(width // 2, height // 2, width, height)
        self.bullets = []
        self.input_handler = InputHandler()
        
        # 游戏状态
        self.score = 0
        self.font = pygame.font.SysFont('Arial', 24)
        
    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.input_handler.handle_keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.input_handler.handle_keyup(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 处理触摸/鼠标输入
                    touch_input = self.input_handler.handle_touch(
                        'begin', pygame.mouse.get_pos(), self.width, self.height)
                    for key, value in touch_input.items():
                        self.player.touch_controls[key] = value
                elif event.type == pygame.MOUSEBUTTONUP:
                    # 释放所有触摸控制
                    self.player.touch_controls = {
                        'left': False,
                        'right': False,
                        'up': False,
                        'fire': False
                    }
                    
            # 更新玩家控制状态
            self.player.keys_pressed = self.input_handler.keys_pressed
            
            # 更新玩家
            self.player.update(current_time)
            
            # 射击
            if 'fire' in self.player.keys_pressed or self.player.touch_controls['fire']:
                bullet = self.player.shoot(current_time)
                if bullet:
                    self.bullets.append(bullet)
                    
            # 更新子弹
            self.bullets = [bullet for bullet in self.bullets if bullet.is_alive()]
            for bullet in self.bullets:
                bullet.update()
                
            # 绘制
            self.screen.fill((0, 0, 20))  # 深蓝色背景
            
            # 绘制星星背景
            for _ in range(50):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 1)
                
            # 绘制游戏对象
            self.player.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            # 绘制分数
            score_text = self.font.render(f"分数: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            
            # 绘制控制说明（PC）
            if not hasattr(self, 'touch_mode') or not self.touch_mode:
                controls_text = self.font.render("方向键移动，空格射击", True, (200, 200, 200))
                self.screen.blit(controls_text, (10, self.height - 30))
                
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()