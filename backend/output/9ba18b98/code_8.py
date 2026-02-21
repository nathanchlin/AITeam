# 加速下落
self.fall_fast = keys[pygame.K_DOWN]

# 硬降
if event.key == pygame.K_SPACE and not self.game_over:
    while self.valid_move(self.current_piece, dy=1):
        self.current_piece.y += 1
    self.lock_piece()