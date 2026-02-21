# 优化后的敌方AI行为模式
class EnemyTankAI:
    def __init__(self):
        self.aggression_level = 0.3  # 初始攻击性降低
        self.tactical_diversity = True  # 增加战术多样性
        self.retreat_threshold = 0.2  # 设置撤退阈值
        
    def update_behavior(self, game_progress):
        # 随游戏进度增加AI难度
        self.aggression_level = min(0.7, 0.3 + game_progress * 0.4)
        
    def make_decision(self, player_position, health):
        # 基于玩家位置和自身血量做出决策
        if health < self.retreat_threshold:
            return "retreat"
        elif distance_to_player(player_position) < 5:
            return "attack"
        else:
            return "patrol"