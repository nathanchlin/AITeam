class Bean:
    def __init__(self, x, y, bean_type="normal"):
        self.x = x
        self.y = y
        self.type = bean_type
        self.collected = False
        self.value = self._get_value()
        self.effect = self._get_effect()
    
    def _get_value(self):
        """根据豆子类型返回分值"""
        values = {
            "normal": 10,
            "power": 50,
            "speed": 30,
            "bonus": 100
        }
        return values.get(self.type, 10)
    
    def _get_effect(self):
        """根据豆子类型返回效果"""
        effects = {
            "normal": None,
            "power": "ghost_vulnerable",
            "speed": "speed_boost",
            "bonus": "score_multiplier"
        }
        return effects.get(self.type, None)

class BeanCollectionSystem:
    def __init__(self):
        self.beans = []
        self.score = 0
        self.power_mode = False
        self.speed_boost = False
        self.score_multiplier = 1
        self.power_mode_timer = 0
        self.speed_boost_timer = 0
        self.score_multiplier_timer = 0
    
    def generate_beans(self, level_width, level_height, bean_count=50):
        """生成豆子"""
        self.beans = []
        for _ in range(bean_count):
            x = random.randint(1, level_width - 1)
            y = random.randint(1, level_height - 1)
            
            # 10%概率生成特殊豆子
            bean_type = "normal"
            rand = random.random()
            if rand < 0.05:
                bean_type = "power"
            elif rand < 0.1:
                bean_type = "speed"
            elif rand < 0.15:
                bean_type = "bonus"
                
            self.beans.append(Bean(x, y, bean_type))
    
    def check_collection(self, player_x, player_y, player_radius):
        """检查玩家是否收集豆子"""
        collected_beans = []
        for bean in self.beans:
            if not bean.collected:
                distance = math.sqrt((player_x - bean.x)**2 + (player_y - bean.y)**2)
                if distance < player_radius + 5:  # 5是豆子的半径
                    bean.collected = True
                    collected_beans.append(bean)
                    self.apply_bean_effect(bean)
        
        return collected_beans
    
    def apply_bean_effect(self, bean):
        """应用豆子效果"""
        self.score += bean.value * self.score_multiplier
        
        if bean.effect == "ghost_vulnerable":
            self.power_mode = True
            self.power_mode_timer = 300  # 5秒（假设60帧/秒）
        elif bean.effect == "speed_boost":
            self.speed_boost = True
            self.speed_boost_timer = 180  # 3秒
        elif bean.effect == "score_multiplier":
            self.score_multiplier = 2
            self.score_multiplier_timer = 240  # 4秒
    
    def update_timers(self):
        """更新各种效果的计时器"""
        if self.power_mode_timer > 0:
            self.power_mode_timer -= 1
            if self.power_mode_timer == 0:
                self.power_mode = False
                
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer == 0:
                self.speed_boost = False
                
        if self.score_multiplier_timer > 0:
            self.score_multiplier_timer -= 1
            if self.score_multiplier_timer == 0:
                self.score_multiplier = 1
    
    def get_remaining_beans(self):
        """获取剩余豆子数量"""
        return sum(1 for bean in self.beans if not bean.collected)