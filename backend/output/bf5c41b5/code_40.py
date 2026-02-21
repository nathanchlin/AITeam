class DifficultyManager:
       def __init__(self):
           self.level = 1
           self.ball_speed = 5
           self.paddle_speed = 8
           
       def increase_level(self):
           self.level += 1
           self.ball_speed += 0.5
           self.paddle_speed += 0.5
           # 可以添加更多难度变化