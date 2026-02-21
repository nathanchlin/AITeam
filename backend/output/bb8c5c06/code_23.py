def draw_game_over(screen, score):
    """绘制游戏结束画面"""
    # 创建半透明覆盖层
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)  # 透明度
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 设置字体
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 36)
    
    # 游戏结束文本
    game_over_text = font_large.render("游戏结束", True, (255, 255, 255))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)
    
    # 分数文本
    score_text = font_medium.render(f"得分: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(score_text, score_rect)
    
    # 重新开始提示
    restart_text = font_medium.render("按空格键重新开始", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(restart_text, restart_rect)
    
    # 更新显示
    pygame.display.flip()