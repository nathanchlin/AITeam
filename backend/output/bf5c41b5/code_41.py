class AchievementSystem:
       def __init__(self):
           self.achievements = {
               'first_brick': {'name': 'First Blood', 'description': 'Break your first brick', 'unlocked': False},
               'combo_master': {'name': 'Combo Master', 'description': 'Achieve a 10x combo', 'unlocked': False},
               'perfect_game': {'name': 'Perfect Game', 'description': 'Complete a game without losing a life', 'unlocked': False}
           }
           
       def check_achievements(self, game_stats):
           # 检查并解锁成就
           pass