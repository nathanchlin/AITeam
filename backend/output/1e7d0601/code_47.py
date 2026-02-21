class Game:
    def __init__(self):
        self.game_system = GameSystem()
        self.score_system = ScoreSystem(self.game_system)
        self.health_system = HealthSystem(self.game_system)
        self.game_state_manager = GameStateManager(self.game_system)
        self.enemy_config = EnemyConfig()
        
    def update(self):
        """游戏主循环更新"""
        if self.game_system.game_state == "PLAYING":
            # 更新连击计时器
            self.score_system.update_combo_timer()
            
    def player_shoot_enemy(self, enemy_type):
        """玩家击中敌人"""
        if self.game_system.game_state != "PLAYING":
            return
            
        # 计算得分
        base_score = self.enemy_config.enemy_scores.get(enemy_type, 100)
        self.score_system.add_score(base_score, is_combo=True)
        
    def player_take_damage(self):
        """玩家受到伤害"""
        self.health_system.take_damage()
        
    def start(self):
        """开始游戏"""
        self.game_state_manager.start_game()
        
    def pause(self):
        """暂停游戏"""
        self.game_state_manager.pause_game()
        
    def resume(self):
        """恢复游戏"""
        self.game_state_manager.resume_game()
        
    def game_over(self):
        """游戏结束"""
        self.game_state_manager.game_over()