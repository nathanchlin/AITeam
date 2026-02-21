class Game:
    def __init__(self):
        self.scoring_system = ScoringSystem()
        self.player_name = "Player1"  # 可以从输入获取
    
    def start_game(self):
        """开始游戏"""
        self.scoring_system.start_new_game()
        print("游戏开始！")
        print(self.scoring_system.get_floor_progress())
        
        # 游戏主循环
        while self.scoring_system.current_floor < 100:
            # 这里应该是游戏逻辑，检测玩家是否成功着陆
            # 示例代码:
            success = self._simulate_player_action()
            
            if success:
                perfect = self._check_perfect_landing()
                score_gained = self.scoring_system.floor_cleared(perfect)
                print(f"成功通过第 {self.scoring_system.current_floor} 层! 得分: {score_gained}")
            else:
                score_gained = self.scoring_system.fall_occurred()
                print(f"掉落了! 连击重置")
            
            print(f"总分: {self.scoring_system.get_current_score()}")
            print(f"连击: {self.scoring_system.combo_count}")
            print("--------------------")
        
        # 游戏结束
        self.end_game()
    
    def _simulate_player_action(self):
        """模拟玩家动作 (实际游戏中应替换为真实逻辑)"""
        # 这里只是示例，实际应根据玩家操作判断
        import random
        return random.random() > 0.2  # 80%成功率
    
    def _check_perfect_landing(self):
        """检查是否完美着陆 (实际游戏中应替换为真实逻辑)"""
        import random
        return random.random() > 0.3  # 30%完美着陆率
    
    def end_game(self):
        """游戏结束"""
        print("\n游戏结束!")
        print(f"最终得分: {self.scoring_system.get_current_score()}")
        print(f"到达楼层: {self.scoring_system.current_floor}")
        print(f"最大连击: {self.scoring_system.max_combo}")
        print(f"完美着陆: {self.scoring_system.perfect_lands} 次")
        
        # 更新最高分
        self.scoring_system.update_high_scores(self.player_name)
        
        # 显示最高分
        print("\n最高分记录:")
        for i, score in enumerate(self.scoring_system.get_high_scores(), 1):
            print(f"{i}. {score['name']}: {score['score']} 分 (楼层: {score['floor']})")

# 启动游戏
if __name__ == "__main__":
    game = Game()
    game.start_game()