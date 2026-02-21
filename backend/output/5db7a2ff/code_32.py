def main():
    renderer = GameRenderer()
    clock = pygame.time.Clock()
    running = True
    
    # 初始化游戏
    renderer.add_random_tile()
    renderer.add_random_tile()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if renderer.move_tiles(Direction.UP):
                        renderer.add_random_tile()
                elif event.key == pygame.K_DOWN:
                    if renderer.move_tiles(Direction.DOWN):
                        renderer.add_random_tile()
                elif event.key == pygame.K_LEFT:
                    if renderer.move_tiles(Direction.LEFT):
                        renderer.add_random_tile()
                elif event.key == pygame.K_RIGHT:
                    if renderer.move_tiles(Direction.RIGHT):
                        renderer.add_random_tile()
                elif event.key == pygame.K_r and renderer.game_over:
                    renderer.restart()
                elif event.key == pygame.K_c and renderer.game_won:
                    renderer.game_won = False
        
        # 更新和绘制
        renderer.update()
        renderer.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()