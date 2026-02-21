class GameStateManager:
    def __init__(self):
        self.state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER
        self.score_system = ScoreSystem()
        self.ninja = None
        self.obstacle_generator = None
        self.collision_system = None
        
    def start_game(self):
        self.state = "PLAYING"
        self.ninja = Ninja()
        self.obstacle_generator = ObstacleGenerator()
        self.collision_system = CollisionSystem()
        self.score_system = ScoreSystem()
        
    def update(self):
        if self.state == "PLAYING":
            self.ninja.update()
            self.obstacle_generator.update()
            self.collision_system.update(self.ninja, self.obstacle_generator.obstacles)
            self.score_system.update(self.ninja, self.obstacle_generator.obstacles)
            
            # 检查游戏结束条件
            if self.ninja.health <= 0:
                self.state = "GAME_OVER"
                
    def pause_game(self):
        if self.state == "PLAYING":
            self.state = "PAUSED"
            
    def resume_game(self):
        if self.state == "PAUSED":
            self.state = "PLAYING"