class GameStateUpdater:
    def __init__(self, num_threads=4):
        self.num_threads = num_threads
        self.lock = threading.Lock()
        self.game_objects = []
    
    def add_game_object(self, obj):
        with self.lock:
            self.game_objects.append(obj)
    
    def update(self, dt):
        # 将游戏对象分组到不同线程
        chunks = np.array_split(self.game_objects, self.num_threads)
        
        threads = []
        for chunk in chunks:
            thread = threading.Thread(
                target=self.update_chunk,
                args=(chunk, dt)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    
    def update_chunk(self, objects, dt):
        for obj in objects:
            obj.update(dt)