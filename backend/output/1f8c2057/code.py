from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass
class Position:
    x: int
    y: int
    
    def __add__(self, direction: Direction):
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)

@dataclass
class Snake:
    body: List[Position]
    direction: Direction
    next_direction: Optional[Direction] = None
    
    def move(self, grow: bool = False):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None
            
        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)
        
        if not grow:
            self.body.pop()

@dataclass
class Food:
    position: Position
    type: str = "normal"  # normal, super, etc.