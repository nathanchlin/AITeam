def draw_game_background(screen, width, height):
    """绘制游戏背景"""
    # 渐变背景
    for y in range(height):
        color_value = int(20 + (y / height) * 30)
        pygame.draw.line(screen, (color_value, color_value, color_value + 10), (0, y), (width, y))
    
    # 游戏区域边框
    pygame.draw.rect(screen, (100, 100, 150), (0, 0, GAME_WIDTH, GAME_HEIGHT), 3)
    
    # 网格线
    for i in range(1, BOARD_WIDTH):
        pygame.draw.line(screen, (40, 40, 60), (i * BLOCK_SIZE, 0), (i * BLOCK_SIZE, GAME_HEIGHT), 1)
    for i in range(1, BOARD_HEIGHT):
        pygame.draw.line(screen, (40, 40, 60), (0, i * BLOCK_SIZE), (GAME_WIDTH, i * BLOCK_SIZE), 1)