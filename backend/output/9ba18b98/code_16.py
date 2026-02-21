class TetrisGame:
    def __init__(self):
        self.board_width = 10
        self.board_height = 20
        self.board = np.zeros((self.board_height, self.board_width), dtype=int)
        self.collision_detector = CollisionDetector(self.board_width, self.board_height)
        self.current_piece = self.generate_new_piece()
        self.current_x = self.board_width // 2 - 1
        self.current_y = 0
        self.game_over = False
    
    def generate_new_piece(self):
        """生成新方块"""
        # 这里简化处理，实际应该从方块池中随机选择
        return T_SHAPE
    
    def update_collision_board(self):
        """更新碰撞检测器的游戏板状态"""
        self.collision_detector.update_board(self.board)
    
    def move_piece(self, dx, dy):
        """移动当前方块"""
        if self.collision_detector.check_valid_move(self.current_piece, self.current_x, self.current_y, dx, dy):
            self.current_x += dx
            self.current_y += dy
            return True
        return False
    
    def rotate_piece(self):
        """旋转当前方块"""
        rotated = rotate_piece(self.current_piece)
        if self.collision_detector.check_valid_rotation(self.current_piece, self.current_x, self.current_y, rotated):
            self.current_piece = rotated
            return True
        return False
    
    def drop_piece(self):
        """方块下落直到着陆"""
        while self.move_piece(0, 1):
            pass
    
    def lock_piece(self):
        """将当前方块锁定到游戏板上"""
        for py, row in enumerate(self.current_piece):
            for px, cell in enumerate(row):
                if cell:
                    board_x = self.current_x + px
                    board_y = self.current_y + py
                    if 0 <= board_x < self.board_width and 0 <= board_y < self.board_height:
                        self.board[board_y, board_x] = 1
        
        # 检查游戏是否结束
        if self.current_y <= 0:
            self.game_over = True
        
        # 生成新方块
        self.current_piece = self.generate_new_piece()
        self.current_x = self.board_width // 2 - 1
        self.current_y = 0
        self.update_collision_board()
    
    def game_loop(self):
        """游戏主循环"""
        while not self.game_over:
            # 处理输入
            # ...
            
            # 移动方块
            if not self.move_piece(0, 1):  # 自动下落
                self.lock_piece()
            
            # 渲染游戏
            # ...