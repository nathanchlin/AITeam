class OptimizedInputHandler(InputHandler):
    def __init__(self, game_board):
        super().__init__(game_board)
        self.key_repeat_delay = 200  # 毫秒
        self.key_repeat_interval = 100  # 毫秒
        self.last_key_time = {}
        self.pressed_keys = set()
        
    def handle_keyboard(self, key, event_type):
        """
        增强的键盘处理，支持按键重复
        
        参数:
            key: 按下的键
            event_type: 事件类型 (KEYDOWN 或 KEYUP)
        """
        if event_type == pygame.KEYDOWN:
            self.pressed_keys.add(key)
            
            # 检查是否是第一次按下或重复按下
            current_time = pygame.time.get_ticks()
            if key not in self.last_key_time or \
               current_time - self.last_key_time[key] > self.key_repeat_delay:
                
                # 处理按键
                if key == pygame.K_UP or key == pygame.K_w:
                    self.game_board.move('up')
                elif key == pygame.K_DOWN or key == pygame.K_s:
                    self.game_board.move('down')
                elif key == pygame.K_LEFT or key == pygame.K_a:
                    self.game_board.move('left')
                elif key == pygame.K_RIGHT or key == pygame.K_d:
                    self.game_board.move('right')
                elif key == pygame.K_ESCAPE:
                    self.game_board.toggle_pause()
                elif key == pygame.K_r:
                    self.game_board.reset_game()
                
                self.last_key_time[key] = current_time
        
        elif event_type == pygame.KEYUP:
            self.pressed_keys.discard(key)
    
    def update(self):
        """
        定期更新，处理按键重复
        """
        current_time = pygame.time.get_ticks()
        
        # 检查需要重复处理的按键
        for key in self.pressed_keys:
            if key in self.last_key_time and \
               current_time - self.last_key_time[key] > self.key_repeat_interval:
                
                # 处理重复按键
                if key == pygame.K_UP or key == pygame.K_w:
                    self.game_board.move('up')
                elif key == pygame.K_DOWN or key == pygame.K_s:
                    self.game_board.move('down')
                elif key == pygame.K_LEFT or key == pygame.K_a:
                    self.game_board.move('left')
                elif key == pygame.K_RIGHT or key == pygame.K_d:
                    self.game_board.move('right')
                
                self.last_key_time[key] = current_time