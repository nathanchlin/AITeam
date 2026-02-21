# 初始化游戏控制器
game = GameController()

# 模拟游戏进行
for i in range(20):
    # 模拟击中敌人
    enemy_types = ["basic", "fast", "tank", "boss"]
    enemy_type = enemy_types[i % 4]
    
    # 获取击中敌人获得的分数
    score_gained = game.on_enemy_destroyed(enemy_type)
    
    # 获取当前难度配置
    spawn_config = game.get_spawn_config()
    
    print(f"击中{enemy_type}敌人, 获得{score_gained}分")
    print(f"当前分数: {game.score_system.get_score()}, 连击: {game.score_system.get_combo()}")
    print(f"难度配置 - 敌人数量: {spawn_config['count']}, 速度: {spawn_config['speed']}, 生成间隔: {spawn_config['spawn_rate']}ms")
    print("-" * 50)