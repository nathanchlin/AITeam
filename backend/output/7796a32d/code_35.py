class ScoringSystem:
    def __init__(self):
        self.current_floor = 0  # 当前所在楼层
        self.total_score = 0    # 总得分
        self.combo_count = 0    # 连续成功下落次数
        self.max_combo = 0      # 最大连击数
        self.perfect_lands = 0  # 完美着陆次数
        self.falls = 0          # 失败次数
        self.high_scores = []    # 最高分记录
        
        # 奖励倍数设置
        self.combo_multipliers = {
            5: 1.2,   # 5连击: 1.2倍
            10: 1.5,  # 10连击: 1.5倍
            20: 2.0,  # 20连击: 2.0倍
            50: 3.0   # 50连击: 3.0倍
        }
    
    def start_new_game(self):
        """开始新游戏时重置分数"""
        self.current_floor = 0
        self.total_score = 0
        self.combo_count = 0
        self.perfect_lands = 0
        self.falls = 0
    
    def floor_cleared(self, perfect=False):
        """成功通过一层"""
        self.current_floor += 1
        base_score = self._calculate_floor_score()
        
        if perfect:
            base_score *= 1.5  # 完美着陆额外50%分数
            self.perfect_lands += 1
        
        # 应用连击奖励
        combo_bonus = self._get_combo_bonus()
        floor_score = int(base_score * combo_bonus)
        
        self.total_score += floor_score
        self.combo_count += 1
        
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
        
        return floor_score
    
    def fall_occurred(self):
        """玩家掉落"""
        self.falls += 1
        self.combo_count = 0  # 重置连击
        return 0  # 掉落不加分
    
    def _calculate_floor_score(self):
        """计算基础楼层分数"""
        # 楼层越高，基础分数越高
        return 10 + (self.current_floor * 2)
    
    def _get_combo_bonus(self):
        """获取连击奖励倍数"""
        for threshold, multiplier in sorted(self.combo_multipliers.items(), reverse=True):
            if self.combo_count >= threshold:
                return multiplier
        return 1.0
    
    def get_current_score(self):
        """获取当前总分"""
        return self.total_score
    
    def get_floor_progress(self):
        """获取楼层进度"""
        return f"当前楼层: {self.current_floor}/100"
    
    def update_high_scores(self, player_name):
        """更新最高分记录"""
        score_entry = {
            "name": player_name,
            "score": self.total_score,
            "floor": self.current_floor,
            "date": self._get_current_date()
        }
        
        self.high_scores.append(score_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:10]  # 只保留前10名
    
    def get_high_scores(self, limit=5):
        """获取前N名最高分"""
        return self.high_scores[:limit]
    
    def _get_current_date(self):
        """获取当前日期字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def get_stats(self):
        """获取游戏统计信息"""
        return {
            "current_floor": self.current_floor,
            "total_score": self.total_score,
            "combo_count": self.combo_count,
            "max_combo": self.max_combo,
            "perfect_lands": self.perfect_lands,
            "falls": self.falls
        }