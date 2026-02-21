# 游戏启动
game = Game()
game.start()

# 从菜单开始游戏
game.handle_input("start_game")  # 切换到READY状态
game.handle_input("begin")       # 切换到PLAYING状态

# 游戏中暂停
game.handle_input("pause")       # 切换到PAUSED状态

# 从暂停恢复
game.handle_input("resume")      # 切换回PLAYING状态

# 游戏结束
game.handle_input("fall")        # 切换到GAME_OVER状态

# 返回菜单
game.handle_input("menu")        # 切换回MENU状态