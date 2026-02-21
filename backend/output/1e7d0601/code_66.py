class ResourceMonitor:
    def __init__(self):
        self.memory_usage = {}
        self.load_times = {}
        
    def track_resource_load(self, resource_name, start_time, end_time):
        load_time = end_time - start_time
        self.load_times[resource_name] = load_time
        
    def get_average_load_time(self):
        if not self.load_times:
            return 0
        return sum(self.load_times.values()) / len(self.load_times)
    
    def get_memory_usage(self):
        # 获取当前进程的内存使用情况
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)  # MB