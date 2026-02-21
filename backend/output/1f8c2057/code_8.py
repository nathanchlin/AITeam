def main():
    # 配置游戏
    config = GameConfig(
        grid_width=20,
        grid_height=15,
        game_speed=8,
        score_per_food=10
    )
    
    # 选择渲染器
    use_pygame = True  # 设置为False可以使用控制台渲染器
    
    if use_pygame:
        renderer = PygameRenderer(config)
    else:
        renderer = ConsoleRenderer(config)
    
    # 创建并运行游戏
    game = GameEngine(config, renderer)
    game.run()

if __name__ == "__main__":
    main()