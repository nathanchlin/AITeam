import pygame
import os
from collections import OrderedDict

class ResourceManager:
    def __init__(self):
        self.images = OrderedDict()
        self.sounds = OrderedDict()
        self.loading_queue = []
        self.loaded_resources = 0
        self.total_resources = 0
        
    def add_image(self, name, path):
        self.loading_queue.append(('image', name, path))
        self.total_resources += 1
        
    def add_sound(self, name, path):
        self.loading_queue.append(('sound', name, path))
        self.total_resources += 1
        
    def load_next(self):
        if not self.loading_queue:
            return False
            
        resource_type, name, path = self.loading_queue.pop(0)
        
        try:
            if resource_type == 'image':
                self.images[name] = pygame.image.load(path).convert_alpha()
            elif resource_type == 'sound':
                self.sounds[name] = pygame.mixer.Sound(path)
                
            self.loaded_resources += 1
            return True
        except pygame.error as e:
            print(f"Error loading {resource_type} {name}: {e}")
            return False
            
    def get_progress(self):
        if self.total_resources == 0:
            return 0
        return self.loaded_resources / self.total_resources
    
    def get_image(self, name):
        return self.images.get(name)
    
    def get_sound(self, name):
        return self.sounds.get(name)