class EnemyAI:
    def __init__(self, player_ref):
        self.player = player_ref
        
    def update(self, enemy):
        if not enemy.active:
            return None
            
        # 根据敌机类型决定是否射击
        if enemy.enemy_type in ["basic", "heavy", "boss"]:
            # 这些类型会定期射击
            if enemy.can_shoot() and random.random() < 0.02:
                return enemy.shoot()
        elif enemy.enemy_type == "fast":
            # 快速敌机射击频率更高
            if enemy.can_shoot() and random.random() < 0.04:
                return enemy.shoot()
        elif enemy.enemy_type == "zigzag":
            # 之字形敌机会在特定条件下射击
            if enemy.can_shoot() and abs(enemy.x - self.player.x) < 50:
                return enemy.shoot()
                
        return None
        
    def predict_player_position(self, enemy):
        # 预测玩家位置，用于高级敌机瞄准
        if enemy.enemy_type == "boss":
            # Boss会预测玩家移动方向
            player_speed_x = self.player.x - getattr(self.player, 'prev_x', self.player.x)
            player_speed_y = self.player.y - getattr(self.player, 'prev_y', self.player.y)
            
            # 预测玩家未来位置
            future_x = self.player.x + player_speed_x * 10
            future_y = self.player.y + player_speed_y * 10
            
            return future_x, future_y
        return None