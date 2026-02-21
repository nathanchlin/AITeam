def draw_score_info(screen, score, level, lines, x, y):
    """绘制分数信息"""
    font = pygame.font.SysFont('Arial', 24, bold=True)
    
    # 分数背景
    score_bg = pygame.Rect(x, y, 200, 120)
    pygame.draw.rect(screen, (30, 30, 50), score_bg)
    pygame.draw.rect(screen, (100, 100, 150), score_bg, 2)
    
    # 分数文本
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    lines_text = font.render(f"Lines: {lines}", True, (255, 255, 255))
    
    screen.blit(score_text, (x + 10, y + 10))
    screen.blit(level_text, (x + 10, y + 45))
    screen.blit(lines_text, (x + 10, y + 80))