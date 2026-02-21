class SpecialEvent:
    def __init__(self, event_type, trigger_condition, duration):
        self.event_type = event_type
        self.trigger_condition = trigger_condition
        self.duration = duration
        self.active = False
        self.timer = 0
        
    def update(self, dt):
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.end_event()
                
    def start_event(self):
        self.active = True
        self.timer = 0
        # 实现事件开始逻辑
        
    def end_event(self):
        self.active = False
        # 实现事件结束逻辑

class ScoutEvent(SpecialEvent):
    def __init__(self, scout_count):
        super().__init__("scout_event", "level_midpoint", 30)
        self.scout_count = scout_count
        
    def start_event(self):
        super().start_event()
        # 生成侦察机
        for _ in range(self.scout_count):
            spawn_scout_plane()