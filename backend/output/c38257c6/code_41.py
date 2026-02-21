def show_game_tip(screen, tip, x, y):
    """显示游戏提示"""
    font = pygame.font.SysFont('Arial', 18)
    text = font.render(tip, True, (255, 255, 0))
    screen.blit(text, (x, y))