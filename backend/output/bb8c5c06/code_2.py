# 创建游戏状态管理器
game_state = GameState(width=20, height=20)

# 游戏循环示例
def game_loop():
    while not game_state.game_over:
        # 处理用户输入
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_UP]:
        #     game_state.change_direction(Direction.UP)
        # elif keys[pygame.K_DOWN]:
        #     game_state.change_direction(Direction.DOWN)
        # elif keys[pygame.K_LEFT]:
        #     game_state.change_direction(Direction.LEFT)
        # elif keys[pygame.K_RIGHT]:
        #     game_state.change_direction(Direction.RIGHT)
        
        # 更新游戏状态
        game_state.update()
        
        # 获取当前网格状态用于渲染
        grid = game_state.get_grid()
        
        # 这里可以添加渲染代码
        # print_grid(grid)
        
        # 控制游戏速度
        # pygame.time.wait(game_state.speed)
    
    # 游戏结束
    print(f"Game Over! Final Score: {game_state.score}")

# 辅助函数：打印网格状态
def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))
    print()

# 重置游戏
def reset_game():
    game_state.reset()

# 测试代码
if __name__ == "__main__":
    # 模拟一些输入和状态更新
    game_state.change_direction(Direction.RIGHT)
    game_state.update()
    print("Initial state:")
    print_grid(game_state.get_grid())
    
    # 模拟吃到食物
    game_state.snake.appendleft(game_state.food)
    game_state.update()
    print("After eating food:")
    print_grid(game_state.get_grid())
    
    # 模拟游戏结束
    game_state.snake.append((0, 0))
    game_state.update()
    print(f"Game Over: {game_state.game_over}, Score: {game_state.score}")