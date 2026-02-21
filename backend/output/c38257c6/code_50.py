def show_game_over_screen(screen, stats, win):
    """显示游戏结束或胜利画面"""
    screen.fill((0, 0, 0))
    font_large = pygame.font.SysFont('Arial', 48)
    font_medium = pygame.font.SysFont('Arial', 24)
    
    if win:
        title = font_large.render("YOU WIN!", True, (0, 255, 0))
    else:
        title = font_large.render("GAME OVER", True, (255, 0, 0))
    
    score_text = font_medium.render(f"Final Score: {stats.score}", True, (255, 255, 255))
    high_score_text = font_medium.render(f"High Score: {stats.high_score}", True, (255, 255, 255))
    restart_text = font_medium.render("Press SPACE to play again or ESC to quit", True, (200, 200, 200))
    
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
    screen.blit(score_text, (screen.get_width()//2 - score_text.get_width()//2, 250))
    screen.blit(high_score_text, (screen.get_width()//2 - high_score_text.get_width()//2, 300))
    screen.blit(restart_text, (screen.get_width()//2 - restart_text.get_width()//2, 400))