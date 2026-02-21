def update(self, dt):
    if self.game_over:
        return
    
    # 处理方块下落
    self.fall_time += dt
    fall_interval = 50 if self.fall_fast else self.fall_speed
    
    if self.fall_time >= fall_interval:
        if self.valid_move(self.current_piece, dy=1):
            self.current_piece.y += 1
        else:
            self.lock_piece()
        self.fall_time = 0