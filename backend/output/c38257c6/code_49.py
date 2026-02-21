def draw_game_stats(screen, stats, font):
    """绘制游戏统计信息"""
    score_text = font.render(f"Score: {stats.score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {stats.lives}", True, (255, 255, 255))
    level_text = font.render(f"Level: {stats.level}", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {stats.high_score}", True, (255, 255, 255))
    
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(level_text, (10, 70))
    screen.blit(high_score_text, (screen.get_width() - 200, 10))