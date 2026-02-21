class Profiler:
    def __init__(self):
        self.timings = {}
        self.frame_times = []
    
    def start(self, section):
        self.timings[section] = {'start': time.time(), 'end': None}
    
    def end(self, section):
        if section in self.timings:
            self.timings[section]['end'] = time.time()
    
    def get_frame_time(self):
        frame_time = sum(
            timing['end'] - timing['start'] 
            for timing in self.timings.values() 
            if timing['end'] is not None
        )
        self.frame_times.append(frame_time)
        return frame_time
    
    def get_average_frame_time(self, window=60):
        if len(self.frame_times) < window:
            window = len(self.frame_times)
        return sum(self.frame_times[-window:]) / window