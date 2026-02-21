# 方块颜色定义
TETROMINO_COLORS = {
    'I': [(0, 255, 255), (0, 200, 200)],    # 青色
    'O': [(255, 255, 0), (200, 200, 0)],    # 黄色
    'T': [(128, 0, 128), (100, 0, 100)],    # 紫色
    'S': [(0, 255, 0), (0, 200, 0)],        # 绿色
    'Z': [(255, 0, 0), (200, 0, 0)],        # 红色
    'J': [(0, 0, 255), (0, 0, 200)],        # 蓝色
    'L': [(255, 165, 0), (200, 130, 0)]     # 橙色
}

def draw_tetromino(screen, x, y, shape, offset_x=0, offset_y=0):
    """绘制带渐变效果的方块"""
    color1, color2 = TETROMINO_COLORS[shape]
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                # 绘制方块主体
                rect = pygame.Rect(
                    x + (j + offset_x) * BLOCK_SIZE,
                    y + (i + offset_y) * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                # 创建渐变效果
                gradient_factor = 0.7 + 0.3 * (i + j) / (len(shape) + len(row))
                color = tuple(int(color1[k] * gradient_factor + color2[k] * (1 - gradient_factor)) for k in range(3))
                pygame.draw.rect(screen, color, rect)
                # 绘制高光效果
                highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, BLOCK_SIZE // 3, BLOCK_SIZE // 3)
                pygame.draw.rect(screen, (255, 255, 255, 128), highlight_rect)
                # 绘制边框
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)