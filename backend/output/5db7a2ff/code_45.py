class BatchRenderer:
    def __init__(self):
        self.batches = {}
    
    def add_object(self, obj):
        material_key = obj.material.get_key()
        if material_key not in self.batches:
            self.batches[material_key] = []
        self.batches[material_key].append(obj)
    
    def render(self):
        for material_key, objects in self.batches.items():
            material = Material.get_from_key(material_key)
            material.bind()
            
            # 合并顶点数据并一次性渲染
            vertices = []
            indices = []
            
            for obj in objects:
                obj_data = obj.get_render_data()
                vertices.extend(obj_data['vertices'])
                indices.extend([i + len(vertices) for i in obj_data['indices']])
            
            # 使用VBO一次性渲染所有对象
            render_batch(vertices, indices)