class Game:
    def __init__(self):
        self.board = GameBoard()
        self.input_handler = InputHandler(self.board)
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
    def run(self):
        """
        游戏主循环
        """
        while self.running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # 键盘事件
                elif event.type == pygame.KEYDOWN:
                    self.input_handler.handle_keyboard(event.key)
                
                # 触摸/鼠标事件
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        self.input_handler.handle_touch_start(event.pos)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # 左键
                        self.input_handler.handle_touch_end(event.pos)
            
            # 更新游戏状态
            if not self.paused:
                self.board.update()
            
            # 渲染
            self.render()
            
            # 控制帧率
            self.clock.tick(60)
    
    def render(self):
        """
        渲染游戏画面
        """
        # 清屏
        self.screen.fill((250, 248, 239))
        
        # 绘制游戏板
        self.board.draw(self.screen)
        
        # 如果暂停，显示暂停信息
        if self.paused:
            self.draw_pause_screen()
        
        # 更新显示
        pygame.display.flip()