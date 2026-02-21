class EnemyConfig:
    def __init__(self):
        # 不同类型敌人的基础分值
        self.enemy_scores = {
            "basic": 100,
            "fast": 150,
            "heavy": 200,
            "boss": 1000
        }
        
        # 敌人生命值配置
        self.enemy_health = {
            "basic": 1,
            "fast": 1,
            "heavy": 3,
            "boss": 10
        }
        
        # 敌人分值倍数（根据关卡递增）
        self.score_multiplier_per_level = 1.2