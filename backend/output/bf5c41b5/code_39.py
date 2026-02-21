class PowerUp:
       def __init__(self, type, position):
           self.type = type  # 'extra_life', 'multiball', 'slow_ball', 'wide_paddle'
           self.position = position
           self.active = True
           
   def apply_powerup(self, powerup_type):
       if powerup_type == 'extra_life':
           self.life_system.gain_life()
       elif powerup_type == 'wide_paddle':
           # 增加挡板宽度
           pass
       # 其他道具效果...