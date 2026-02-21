from abc import ABC, abstractmethod

class Renderer(ABC):
    @abstractmethod
    def render(self, state: GameState):
        pass
    
    @abstractmethod
    def clear(self):
        pass