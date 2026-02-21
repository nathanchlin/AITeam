class ResourceManager:
    # ... 之前的代码 ...
    
    def release_unused_resources(self, current_scene_resources):
        # 释放当前场景不使用的图像资源
        unused_images = set(self.images.keys()) - set(current_scene_resources)
        for name in unused_images:
            del self.images[name]
            
        # 释放当前场景不使用的音频资源
        unused_sounds = set(self.sounds.keys()) - set(current_scene_resources)
        for name in unused_sounds:
            del self.sounds[name]
    
    def clear_all(self):
        self.images.clear()
        self.sounds.clear()
        self.loading_queue.clear()
        self.loaded_resources = 0
        self.total_resources = 0