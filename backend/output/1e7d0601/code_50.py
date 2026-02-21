class LevelManager:
    def __init__(self):
        self.current_level = 0
        self.levels = self._create_levels()
        self.level_complete = False
        self.game_complete = False
        
    def _create_levels(self):
        levels = []
        
        # 创建关卡1
        level1 = Level(1, "太平洋初战", "battle_music_1", 1.0)
        level1.add_enemy_wave([BasicEnemy(3), BasicEnemy(5), BasicEnemy(7)])
        level1.add_objective("消灭所有敌机")
        levels.append(level1)
        
        # 创建关卡2
        level2 = Level(2, "敌军增援", "battle_music_2", 1.2)
        level2.add_enemy_wave([BasicEnemy(5), FastEnemy(2)])
        level2.add_enemy_wave([BasicEnemy(8)])
        level2.add_enemy_wave([BasicEnemy(10)])
        level2.add_special_event(ScoutEvent(3))
        level2.add_objective("消灭所有敌机，优先击毁侦察机")
        levels.append(level2)
        
        # 创建其他关卡...
        
        return levels
    
    def get_current_level(self):
        if self.current_level < len(self.levels):
            return self.levels[self.current_level]
        return None
    
    def next_level(self):
        self.current_level += 1
        if self.current_level >= len(self.levels):
            self.game_complete = True
    
    def restart_level(self):
        self.level_complete = False
        # 重置关卡状态