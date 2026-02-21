class PerformanceManager:
    def __init__(self):
        self.current_quality = "medium"
        self.fps_history = []
        
    def update_quality(self):
        avg_fps = sum(self.fps_history[-30:]) / min(30, len(self.fps_history))
        
        if avg_fps < 25 and self.current_quality != "low":
            self.current_quality = "low"
            self.reduce_quality()
        elif avg_fps > 45 and self.current_quality != "high":
            self.current_quality = "high"
            self.increase_quality()
    
    def reduce_quality(self):
        # 降低图形质量的具体实现
        pass
    
    def increase_quality(self):
        # 提高图形质量的具体实现
        pass