# 创建并开始游戏
game = SheepSheepGame(difficulty=3)
cards = game.start_game()

# 打印卡片布局
for layer in range(3):
    layer_cards = [c for c in cards if c.layer == layer]
    print(f"\n层级 {layer}:")
    for card in layer_cards:
        print(f"  卡片ID: {card.id}, 类型: {card.type}, 位置: {card.position}")

# 模拟游戏过程
print("\n游戏开始:")
# 选择两张卡片
result, message = game.select_card(0)
print(message)
result, message = game.select_card(1)
print(message)

# 查看游戏状态
print(f"\n移动次数: {game.moves}, 得分: {game.score}")