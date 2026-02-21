def show_start_screen(screen):
    """显示游戏开始界面"""
    screen.fill((0, 0, 0))
    font_large = pygame.font.SysFont('Arial', 48)
    font_medium = pygame.font.SysFont('Arial', 24)
    
    title = font_large.render("BREAKOUT GAME", True, (255, 255, 255))
    instructions = [
        "Use LEFT/RIGHT arrows to move the paddle",
        "Break all bricks to win!",
        "Don't let the ball fall!",
        "",
        "Press SPACE to start"
    ]
    
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
    
    y = 200
    for line in instructions:
        text = font_medium.render(line, True, (200, 200, 200))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, y))
        y += 30