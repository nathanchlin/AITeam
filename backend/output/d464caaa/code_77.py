class PerformanceProfile:
    def __init__(self):
        self.profiles = {
            'high': {'particles': True, 'animations': True, 'fps_cap': 60},
            'medium': {'particles': False, 'animations': True, 'fps_cap': 30},
            'low': {'particles': False, 'animations': False, 'fps_cap': 20}
        }
    
    def get_profile(self):
        """根据设备性能自动选择配置"""
        if self.is_high_end_device():
            return self.profiles['high']
        elif self.is_mid_range_device():
            return self.profiles['medium']
        else:
            return self.profiles['low']