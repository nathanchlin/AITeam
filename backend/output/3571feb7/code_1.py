class PacmanGame:
    def __init__(self):
        self.bean_system = BeanCollectionSystem()
        self.player = Player()
        self.ghosts = [Ghost() for _ in range(4)]
        self.level_width = 28
        self.level_height = 31
        self.bean_system.generate_beans(self.level_width, self.level_height)
    
    def update(self):
        # 更新玩家位置
        self.player.update()
        
        # 检查豆子收集
        collected = self.bean_system.check_collection(
            self.player.x, self.player.y, self.player.radius
        )
        
        # 更新效果计时器
        self.bean_system.update_timers()
        
        # 更新鬼魂状态（根据能量模式）
        for ghost in self.ghosts:
            ghost.update(self.bean_system.power_mode)
        
        # 检查是否完成关卡
        if self.bean_system.get_remaining_beans() == 0:
            self.next_level()
    
    def render(self):
        # 渲染豆子
        for bean in self.bean_system.beans:
            if not bean.collected:
                color = self.get_bean_color(bean.type)
                pygame.draw.circle(screen, color, (bean.x, bean.y), 5)
        
        # 渲染玩家
        self.player.render(screen)
        
        # 渲染鬼魂
        for ghost in self.ghosts:
            ghost.render(screen)
        
        # 渲染分数和状态
        self.render_ui()
    
    def get_bean_color(self, bean_type):
        """根据豆子类型返回颜色"""
        colors = {
            "normal": (255, 255, 255),  # 白色
            "power": (255, 255, 0),     # 黄色
            "speed": (0, 255, 255),     # 青色
            "bonus": (255, 0, 255)      # 紫色
        }
        return colors.get(bean_type, (255, 255, 255))