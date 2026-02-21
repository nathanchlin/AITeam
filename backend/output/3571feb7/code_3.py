def main():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("吃豆子游戏")
    clock = pygame.time.Clock()
    
    # 初始化游戏对象
    maze = Maze(15, 11, 40)
    player = Player(2 * maze.cell_size + maze.cell_size // 2, 
                    2 * maze.cell_size + maze.cell_size // 2)
    
    # 创建豆子
    dots = []
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.maze[y][x] == 0:  # 只在通道上放置豆子
                dot_x = x * maze.cell_size + maze.cell_size // 2
                dot_y = y * maze.cell_size + maze.cell_size // 2
                dots.append(Dot(dot_x, dot_y))
    
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # 处理方向键输入
                if event.key == pygame.K_UP:
                    player.next_direction = 'up'
                elif event.key == pygame.K_DOWN:
                    player.next_direction = 'down'
                elif event.key == pygame.K_LEFT:
                    player.next_direction = 'left'
                elif event.key == pygame.K_RIGHT:
                    player.next_direction = 'right'
        
        # 更新游戏状态
        player.update(maze)
        
        # 检查豆子碰撞
        for dot in dots:
            dot.check_collision(player)
        
        # 绘制游戏画面
        screen.fill((0, 0, 0))  # 黑色背景
        maze.draw(screen)
        
        for dot in dots:
            dot.draw(screen)
        
        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()