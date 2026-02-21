def draw_game_over(screen, score, width, height):
    """绘制游戏结束画面"""
    # 半透明覆盖层
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 游戏结束文本
    font_large = pygame.font.SysFont('Arial', 48, bold=True)
    font_medium = pygame.font.SysFont('Arial', 24)
    
    game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
    score_text = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
    restart_text = font_medium.render("Press SPACE to restart", True, (255, 255, 255))
    
    # 居中显示
    screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 60))
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
    screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2 + 40))