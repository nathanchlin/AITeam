class ScoreSystem:
    def __init__(self, game_system):
        self.game_system = game_system
        
    def add_score(self, points, is_combo=False):
        """添加得分到总分"""
        if self.game_system.game_state != "PLAYING":
            return
            
        # 计算连击加成
        multiplier = self.game_system.combo_multiplier
        final_points = int(points * multiplier)
        
        self.game_system.score += final_points
        
        # 检查是否获得额外生命
        self._check_extra_life()
        
        # 更新连击系统
        if is_combo:
            self._update_combo()
            
    def _update_combo(self):
        """更新连击系统"""
        self.game_system.combo += 1
        self.game_system.combo_timer = self.game_system.combo_threshold
        
        # 更新最大连击记录
        if self.game_system.combo > self.game_system.max_combo:
            self.game_system.max_combo = self.game_system.combo
            
        # 更新连击倍数
        new_multiplier = min(
            self.game_system.combo * self.game_system.combo_increment,
            self.game_system.max_combo_multiplier
        )
        self.game_system.combo_multiplier = new_multiplier
        
    def _check_extra_life(self):
        """检查是否获得额外生命"""
        if (self.game_system.score >= self.game_system.last_extra_life_score + 
            self.game_system.extra_life_at):
            self.game_system.lives += 1
            self.game_system.last_extra_life_score = self.game_system.score
            
    def update_combo_timer(self):
        """更新连击计时器"""
        if self.game_system.combo_timer > 0:
            self.game_system.combo_timer -= 1
            if self.game_system.combo_timer == 0:
                # 重置连击
                self.game_system.combo = 0
                self.game_system.combo_multiplier = 1.0