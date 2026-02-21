def valid_move(self, piece, dx=0, dy=0, rotation=None):
    # 检查移动是否有效
    test_shape = rotation if rotation is not None else piece.shape
    for y, row in enumerate(test_shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x + dx
                new_y = piece.y + y + dy
                
                # 检查边界
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return False
                
                # 检查碰撞
                if new_y >= 0 and self.grid[new_y][new_x]:
                    return False
    return True