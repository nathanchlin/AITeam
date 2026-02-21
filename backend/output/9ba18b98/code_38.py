def draw_shadow(screen, board, current_piece, x, y):
    """绘制方块下落位置的阴影"""
    shadow_y = y
    while is_valid_position(board, current_piece.shape, current_piece.x, shadow_y + 1):
        shadow_y += 1
    
    for i, row in enumerate(current_piece.shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    x + (current_piece.x + j) * BLOCK_SIZE,
                    y + (shadow_y + i) * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                # 绘制半透明阴影
                s = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                s.set_alpha(64)
                s.fill((100, 100, 100))
                screen.blit(s, rect)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)