def lock_piece(self):
    # 将当前方块固定到网格中
    for x, y in self.current_piece.get_cells():
        if y >= 0:
            self.grid[y][x] = self.current_piece.shape_index + 1
    
    # 检查是否有完整的行
    self.clear_lines()
    
    # 生成新方块
    self.current_piece = self.next_piece
    self.next_piece = self.new_piece()
    
    # 检查游戏是否结束
    if not self.valid_move(self.current_piece):
        self.game_over = True