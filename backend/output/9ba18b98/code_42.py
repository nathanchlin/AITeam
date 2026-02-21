def draw_next_piece(screen, next_piece, x, y):
    """绘制下一个方块预览"""
    # 预览区背景
    preview_bg = pygame.Rect(x, y, 120, 120)
    pygame.draw.rect(screen, (30, 30, 50), preview_bg)
    pygame.draw.rect(screen, (100, 100, 150), preview_bg, 2)
    
    # 预览标题
    font = pygame.font.SysFont('Arial', 20, bold=True)
    title = font.render("Next", True, (255, 255, 255))
    screen.blit(title, (x + 40, y + 5))
    
    # 绘制下一个方块
    if next_piece:
        # 居中显示
        block_size = 25
        offset_x = (120 - len(next_piece.shape[0]) * block_size) // 2
        offset_y = (120 - len(next_piece.shape) * block_size) // 2 + 30
        
        for i, row in enumerate(next_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        x + offset_x + j * block_size,
                        y + offset_y + i * block_size,
                        block_size,
                        block_size
                    )
                    color1, color2 = TETROMINO_COLORS[next_piece.shape_type]
                    color = tuple(int((color1[k] + color2[k]) / 2) for k in range(3))
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 1)