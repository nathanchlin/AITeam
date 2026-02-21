def draw_paddle_with_effect(screen, paddle):
    """绘制带有视觉效果的挡板"""
    # 绘制阴影
    shadow_rect = pygame.Rect(paddle.x + 3, paddle.y + 3, paddle.width, paddle.height)
    pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=5)
    
    # 绘制挡板主体
    pygame.draw.rect(screen, paddle.color, paddle.rect, border_radius=5)
    
    # 绘制高光
    highlight_rect = pygame.Rect(paddle.x + 2, paddle.y + 2, paddle.width - 4, 3)
    pygame.draw.rect(screen, (255, 255, 255), highlight_rect, border_radius=2)