# 初始化食物生成器
food_generator = OptimizedFoodGenerator(game_width=800, game_height=600, cell_size=20)

# 示例蛇身(像素坐标)
snake_body = [(100, 100), (120, 100), (140, 100)]

# 生成食物
food_position = food_generator.generate_food(snake_body)
print(f"生成的食物位置: {food_position}")

# 游戏循环示例
while True:
    # 游戏逻辑...
    
    # 当蛇吃到食物时
    if snake_head == food_position:
        # 蛇变长...
        # 生成新食物
        food_position = food_generator.generate_food(snake_body)