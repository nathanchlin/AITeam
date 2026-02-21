class BrickManager:
    def __init__(self):
        self.score = 0
        
    def handle_brick_collision(self, ball, bricks):
        """处理球与砖块的碰撞"""
        for brick in bricks:
            if CollisionDetector.check_ball_brick_collision(ball, brick):
                points = brick.hit()
                self.score += points
                return True
        return False
    
    def get_score(self):
        """获取当前得分"""
        return self.score