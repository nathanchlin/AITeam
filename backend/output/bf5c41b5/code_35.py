class BrickBreakerGame:
    def __init__(self):
        self.score_system = ScoreSystem()
        self.life_system = LifeSystem()
        self.bricks = self._create_bricks()
        
    def _create_bricks(self):
        """创建砖块网格，不同类型砖块"""
        brick_types = [
            ['normal', 'normal', 'strong', 'normal', 'normal'],
            ['normal', 'strong', 'super_strong', 'strong', 'normal'],
            ['special', 'normal', 'normal', 'normal', 'special'],
            ['normal', 'strong', 'super_strong', 'strong', 'normal'],
            ['normal', 'normal', 'strong', 'normal', 'normal']
        ]
        return brick_types
    
    def handle_ball_collision(self, ball_pos, ball_dir):
        """处理球与砖块/挡板的碰撞"""
        # 检查与砖块的碰撞
        for row in range(len(self.bricks)):
            for col in range(len(self.bricks[row])):
                if self._is_ball_hitting_brick(ball_pos, (row, col)):
                    brick_type = self.bricks[row][col]
                    self.score_system.add_score(0, brick_type)  # 0表示由碰撞处理函数计算实际分数
                    self.bricks[row][col] = None  # 移除砖块
                    self._update_ball_direction(ball_dir, (row, col))
                    return True
                    
        # 检查与挡板的碰撞
        if self._is_ball_hitting_paddle(ball_pos):
            self.score_system.reset_combo()  # 球碰到挡板重置连击
            return True
            
        return False
    
    def _is_ball_hitting_brick(self, ball_pos, brick_pos):
        """检查球是否击中砖块"""
        # 实现碰撞检测逻辑
        pass
    
    def _is_ball_hitting_paddle(self, ball_pos):
        """检查球是否击中挡板"""
        # 实现碰撞检测逻辑
        pass
    
    def _update_ball_direction(self, ball_dir, brick_pos):
        """根据碰撞位置更新球的方向"""
        # 实现方向更新逻辑
        pass
    
    def check_ball_fall(self):
        """检查球是否掉落"""
        if ball_fell:
            self.life_system.lose_life()
            return True
        return False
    
    def get_game_status(self):
        """获取游戏状态"""
        return {
            'score': self.score_system.score,
            'lives': self.life_system.lives,
            'combo': self.score_system.current_combo,
            'combo_multiplier': self.score_system.combo_multiplier,
            'game_over': self.life_system.game_over,
            'all_bricks_cleared': all(all(brick is None for brick in row) for row in self.bricks)
        }