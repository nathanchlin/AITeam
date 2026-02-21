class GameObjectPool:
    def __init__(self, prefab, initial_size=10):
        self.prefab = prefab
        self.pool = []
        self.active_objects = []
        
        # 初始化对象池
        for _ in range(initial_size):
            obj = self.create_new_object()
            self.pool.append(obj)
    
    def create_new_object(self):
        obj = self.prefab.clone()  # 假设prefab有clone方法
        obj.set_active(False)
        return obj
    
    def get_object(self):
        if not self.pool:
            new_obj = self.create_new_object()
            self.pool.append(new_obj)
        
        obj = self.pool.pop()
        obj.set_active(True)
        self.active_objects.append(obj)
        return obj
    
    def return_object(self, obj):
        obj.set_active(False)
        self.active_objects.remove(obj)
        self.pool.append(obj)