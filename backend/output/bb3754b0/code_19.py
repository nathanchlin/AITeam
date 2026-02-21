class Animation:
    def __init__(self, frames, frame_duration, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time = 0
        self.loop = loop
        self.finished = False
    
    def update(self, dt):
        if self.finished:
            return
            
        self.time += dt
        while self.time >= self.frame_duration:
            self.time -= self.frame_duration
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self):
        return self.frames[self.current_frame]
    
    def reset(self):
        self.current_frame = 0
        self.time = 0
        self.finished = False