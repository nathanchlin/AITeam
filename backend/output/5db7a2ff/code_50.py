class ResourceManager:
    def __init__(self):
        self.loaded_resources = {}
        self.loading_queue = []
        self.unload_threshold = 0.8  # 80%内存使用时触发卸载
    
    def preload_resources(self, resources):
        for resource in resources:
            if resource not in self.loaded_resources:
                self.loading_queue.append(resource)
    
    def update(self):
        # 处理加载队列
        while self.loading_queue:
            resource = self.loading_queue.pop(0)
            self.loaded_resources[resource] = load_resource(resource)
        
        # 检查内存使用情况
        if self.get_memory_usage() > self.unload_threshold:
            self.unload_unused_resources()
    
    def unload_unused_resources(self):
        # 卸载最近未使用的资源
        unused_resources = self.get_unused_resources()
        for resource in unused_resources:
            del self.loaded_resources[resource]