class GameController:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.game = SpaceShooterGame()  # 假设这是我们的太空射击游戏主类
        self.clock = pygame.time.Clock()
        self.running = True
        self.state_data = {}  # 用于存储状态相关的数据
        
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state_manager.is_state(GameState.MENU):
                self.handle_menu_events(event)
            elif self.state_manager.is_state(GameState.STARTING):
                self.handle_starting_events(event)
            elif self.state_manager.is_state(GameState.PLAYING):
                self.handle_playing_events(event)
            elif self.state_manager.is_state(GameState.PAUSED):
                self.handle_paused_events(event)
            elif self.state_manager.is_state(GameState.GAME_OVER):
                self.handle_game_over_events(event)
            elif self.state_manager.is_state(GameState.RESTARTING):
                self.handle_restarting_events(event)
    
    def handle_menu_events(self, event):
        """处理主菜单事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state_manager.change_state(GameState.STARTING)
            elif event.key == pygame.K_ESCAPE:
                self.running = False
    
    def handle_starting_events(self, event):
        """处理游戏开始事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # 初始化游戏
                self.game.reset()
                self.state_data["score"] = 0
                self.state_data["lives"] = 3
                self.state_data["level"] = 1
                self.state_manager.change_state(GameState.PLAYING)
    
    def handle_playing_events(self, event):
        """处理游戏进行中事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # 暂键
                self.state_manager.push_state(GameState.PAUSED)
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.push_state(GameState.PAUSED)
    
    def handle_paused_events(self, event):
        """处理游戏暂停事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # 继续键
                self.state_manager.pop_state()
            elif event.key == pygame.K_m:  # 返回菜单
                self.state_manager.change_state(GameState.MENU)
            elif event.key == pygame.K_r:  # 重新开始
                self.state_manager.change_state(GameState.RESTARTING)
    
    def handle_game_over_events(self, event):
        """处理游戏结束事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # 返回菜单
                self.state_manager.change_state(GameState.MENU)
            elif event.key == pygame.K_r:  # 重新开始
                self.state_manager.change_state(GameState.RESTARTING)
    
    def handle_restarting_events(self, event):
        """处理游戏重新开始事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.reset()
                self.state_data["score"] = 0
                self.state_data["lives"] = 3
                self.state_data["level"] = 1
                self.state_manager.change_state(GameState.PLAYING)
    
    def update(self):
        """更新游戏逻辑"""
        if self.state_manager.is_state(GameState.PLAYING):
            # 更新游戏状态
            self.game.update()
            
            # 检查游戏结束条件
            if self.game.player.is_dead():
                self.state_manager.change_state(GameState.GAME_OVER)
            
            # 更新分数和难度
            self.state_data["score"] = self.game.score
            if self.state_data["score"] > self.state_data["level"] * 1000:
                self.state_data["level"] += 1
                self.game.increase_difficulty()
    
    def render(self):
        """渲染游戏画面"""
        if self.state_manager.is_state(GameState.MENU):
            self.render_menu()
        elif self.state_manager.is_state(GameState.STARTING):
            self.render_starting()
        elif self.state_manager.is_state(GameState.PLAYING):
            self.game.render()
            self.render_hud()
        elif self.state_manager.is_state(GameState.PAUSED):
            self.game.render()  # 继续渲染游戏画面，但添加暂停覆盖层
            self.render_pause_overlay()
        elif self.state_manager.is_state(GameState.GAME_OVER):
            self.render_game_over()
        elif self.state_manager.is_state(GameState.RESTARTING):
            self.render_restarting()
    
    def render_menu(self):
        """渲染主菜单"""
        # 绘制菜单背景和选项
        pass
    
    def render_starting(self):
        """渲染游戏开始画面"""
        # 绘制游戏开始画面
        pass
    
    def render_hud(self):
        """渲染游戏HUD（ heads-up display）"""
        # 绘制分数、生命值、等级等信息
        pass
    
    def render_pause_overlay(self):
        """渲染暂停覆盖层"""
        # 绘制半透明覆盖层和暂停文本
        pass
    
    def render_game_over(self):
        """渲染游戏结束画面"""
        # 绘制游戏结束画面和最终分数
        pass
    
    def render_restarting(self):
        """渲染重新开始画面"""
        # 绘制重新开始提示
        pass
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()