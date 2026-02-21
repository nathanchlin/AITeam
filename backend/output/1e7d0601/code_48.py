# 创建游戏实例
game = Game()

# 开始游戏
game.start()

# 玩家击中敌人
game.player_shoot_enemy("basic")  # 得分: 100 * 1.0 = 100
game.player_shoot_enemy("fast")   # 得分: 150 * 1.5 = 225 (连击x1.5)
game.player_shoot_enemy("basic")  # 得分: 100 * 2.0 = 200 (连击x2.0)

# 玩家受到伤害
game.player_take_damage()  # 生命值-1, 连击重置

# 暂停游戏
game.pause()

# 恢复游戏
game.resume()

# 游戏结束
game.game_over()