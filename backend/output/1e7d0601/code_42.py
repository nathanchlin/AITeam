class GameSystem:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.game_state = "START"  # START, PLAYING, PAUSED, GAME_OVER
        self.combo_timer = 0
        self.combo_threshold = 60  # 1秒内击中下一个目标保持连击（假设60FPS）
        
        # 得分配置
        self.base_score = 100
        self.combo_multiplier = 1.0
        self.max_combo_multiplier = 5.0
        self.combo_increment = 0.5
        
        # 生命值配置
        self.max_lives = 3
        self.extra_life_at = 10000  # 每10000分额外生命
        self.last_extra_life_score = 0