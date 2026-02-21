import threading

class PhysicsThreadManager:
    def __init__(self, num_threads=4):
        self.num_threads = num_threads
        self.threads = []
        self.tasks = []
        self.lock = threading.Lock()
    
    def add_task(self, task):
        with self.lock:
            self.tasks.append(task)
    
    def process_tasks(self):
        # 将任务分配到各个线程
        chunk_size = len(self.tasks) // self.num_threads
        for i in range(self.num_threads):
            start = i * chunk_size
            end = start + chunk_size if i < self.num_threads - 1 else len(self.tasks)
            
            thread = threading.Thread(
                target=self.process_chunk,
                args=(self.tasks[start:end],)
            )
            self.threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in self.threads:
            thread.join()
        
        self.threads = []
        self.tasks = []
    
    def process_chunk(self, tasks):
        for task in tasks:
            task.execute()