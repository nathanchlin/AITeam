class GameController:
    """游戏控制器"""
    def __init__(self, game_board):
        self.state_manager = GameStateManager()
        self.game_board = game_board
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 1000  # 方块下落速度(毫秒)
        
    def start_game(self):
        """开始游戏"""
        self.state_manager.reset_game()
        self.state_manager.change_state(GameState.STARTING)
        self.game_board.reset()
        self.state_manager.change_state(GameState.PLAYING)
        
    def pause_game(self):
        """暂停游戏"""
        if self.state_manager.is_playing():
            self.state_manager.change_state(GameState.PAUSED)
            
    def resume_game(self):
        """继续游戏"""
        if self.state_manager.is_paused():
            self.state_manager.change_state(GameState.PLAYING)
            
    def game_over(self):
        """游戏结束"""
        self.state_manager.change_state(GameState.GAME_OVER)
        
    def check_game_over_condition(self):
        """检查游戏结束条件"""
        # 检查是否有方块堆积到顶部
        if self.game_board.check_top_reached():
            self.game_over()
            return True
        return False
        
    def update(self, dt):
        """更新游戏逻辑"""
        if self.state_manager.is_playing():
            self.fall_time += dt
            if self.fall_time >= self.fall_speed:
                self.game_board.move_piece_down()
                self.fall_time = 0
                self.check_game_over_condition()
                
    def handle_input(self, event):
        """处理输入事件"""
        if self.state_manager.is_playing():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.game_board.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.game_board.move_piece(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.game_board.move_piece(0, 1)
                elif event.key == pygame.K_UP:
                    self.game_board.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.game_board.drop_piece()
                elif event.key == pygame.K_p:
                    self.pause_game()
                    
        elif self.state_manager.is_paused():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.resume_game()
                    
        elif self.state_manager.is_game_over():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.start_game()
                elif event.key == pygame.K_m:
                    self.state_manager.change_state(GameState.MENU)