class Tetris:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.spawn_new_piece()
    
    def spawn_new_piece(self):
        """生成新方块"""
        # 在顶部中央生成新方块
        x = self.width // 2 - 1
        y = 0
        self.current_piece = Tetromino(x, y)
        
        # 检查游戏是否结束
        if self.check_collision():
            self.game_over = True
    
    def check_collision(self, dx=0, dy=0, shape=None):
        """检查碰撞"""
        if shape is None:
            shape = self.current_piece.get_shape()
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x + dx
                    new_y = self.current_piece.y + y + dy
                    
                    # 检查边界
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return True
                    
                    # 检查与已有方块的碰撞
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True
        
        return False
    
    def lock_piece(self):
        """将当前方块锁定到游戏板上"""
        shape = self.current_piece.get_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_piece.x + x
                    board_y = self.current_piece.y + y
                    if 0 <= board_x < self.width and 0 <= board_y < self.height:
                        self.board[board_y][board_x] = self.current_piece.shape_index + 1
        
        # 检查并清除完整的行
        self.clear_lines()
        
        # 生成新方块
        self.spawn_new_piece()
    
    def clear_lines(self):
        """清除完整的行"""
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            if all(self.board[y]):
                # 删除该行
                del self.board[y]
                # 在顶部添加新行
                self.board.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        
        # 更新分数
        self.score += lines_cleared * 100
    
    def move_piece(self, dx, dy):
        """移动当前方块"""
        if not self.check_collision(dx, dy):
            self.current_piece.move(dx, dy)
            return True
        return False
    
    def rotate_piece(self):
        """旋转当前方块"""
        # 保存当前形状
        original_shape = self.current_piece.shape
        
        # 尝试旋转
        self.current_piece.rotate()
        
        # 如果旋转后发生碰撞，恢复原状
        if self.check_collision():
            self.current_piece.shape = original_shape
            return False
        return True
    
    def update(self):
        """更新游戏状态"""
        if self.game_over:
            return
        
        # 方块自动下落
        if not self.move_piece(0, 1):
            self.lock_piece()
    
    def draw(self, screen):
        """绘制游戏画面"""
        # 绘制游戏板背景
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 
                        self.width * self.cell_size, 
                        self.height * self.cell_size))
        
        # 绘制已锁定的方块
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    color = COLORS[cell - 1]
                    pygame.draw.rect(screen, color, 
                                   (x * self.cell_size, y * self.cell_size,
                                    self.cell_size - 1, self.cell_size - 1))
        
        # 绘制当前方块
        if self.current_piece:
            shape = self.current_piece.get_shape()
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_piece.get_color(),
                                       ((self.current_piece.x + x) * self.cell_size,
                                        (self.current_piece.y + y) * self.cell_size,
                                        self.cell_size - 1, self.cell_size - 1))
        
        # 绘制游戏结束信息
        if self.game_over:
            font = pygame.font.SysFont(None, 36)
            text = font.render("Game Over!", True, (255, 255, 255))
            screen.blit(text, (self.width * self.cell_size // 2 - text.get_width() // 2,
                              self.height * self.cell_size // 2))