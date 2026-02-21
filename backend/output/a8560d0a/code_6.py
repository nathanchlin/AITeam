class GameObjectPool:
    def __init__(self, prefab, initial_size=10):
        self.prefab = prefab
        self.available_objects = []
        self.in_use_objects = []
        
        for _ in range(initial_size):
            obj = self.create_object()
            self.available_objects.append(obj)
    
    def get_object(self):
        if not self.available_objects:
            obj = self.create_object()
        else:
            obj = self.available_objects.pop()
        self.in_use_objects.append(obj)
        return obj
    
    def return_object(self, obj):
        self.in_use_objects.remove(obj)
        self.available_objects.append(obj)
        obj.reset()