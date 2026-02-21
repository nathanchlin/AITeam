class CollisionHandler:
    def __init__(self, character, score_system):
        self.character = character
        self.score_system = score_system
    
    def handle_collisions(self, collisions, obstacles):
        """处理碰撞结果"""
        for collision_index in collisions:
            obstacle = obstacles[collision_index]
            
            # 根据障碍物类型处理碰撞
            if obstacle.type == "ground" and not self.character.is_sliding:
                self.character.health -= 20
                obstacle.active = False
            elif obstacle.type == "air" and not self.character.is_jumping:
                self.character.health -= 20
                obstacle.active = False
            elif obstacle.type == "slide" and not self.character.is_sliding:
                self.character.health -= 30
                obstacle.active = False
            
            # 检查游戏是否结束
            if self.character.health <= 0:
                EventSystem.emit("game_over")
    
    def check_score(self, obstacles):
        """检查得分"""
        for obstacle in obstacles:
            if not obstacle.passed and obstacle.position.x + obstacle.width < self.character.position.x:
                obstacle.passed = True
                self.score_system.add_score(10)