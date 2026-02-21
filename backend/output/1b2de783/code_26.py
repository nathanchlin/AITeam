import random
import math
from enum import Enum
from abc import ABC, abstractmethod

class EnemyType(Enum):
    BASIC = "basic"
    FAST = "fast"
    HEAVY = "heavy"
    ELITE = "elite"
    BOSS = "boss"

class EnemyAI(ABC):
    @abstractmethod
    def update(self, enemy, player, game_state):
        pass

class Enemy:
    def __init__(self, x, y, enemy_type, game_settings):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.settings = game_settings
        self.health = self._get_health()
        self.max_health = self.health
        self.speed = self._get_speed()
        self.size = self._get_size()
        self.color = self._get_color()
        self.damage = self._get_damage()
        self.score_value = self._get_score_value()
        self.shoot_cooldown = 0
        self.ai = self._create_ai()
        self.special_ability_cooldown = 0
        self.alive = True
        
    def _get_health(self):
        health_map = {
            EnemyType.BASIC: 1,
            EnemyType.FAST: 1,
            EnemyType.HEAVY: 3,
            EnemyType.ELITE: 2,
            EnemyType.BOSS: 10
        }
        return health_map.get(self.type, 1)
    
    def _get_speed(self):
        speed_map = {
            EnemyType.BASIC: 2,
            EnemyType.FAST: 4,
            EnemyType.HEAVY: 1,
            EnemyType.ELITE: 2.5,
            EnemyType.BOSS: 1.5
        }
        return speed_map.get(self.type, 2)
    
    def _get_size(self):
        size_map = {
            EnemyType.BASIC: 20,
            EnemyType.FAST: 15,
            EnemyType.HEAVY: 30,
            EnemyType.ELITE: 25,
            EnemyType.BOSS: 50
        }
        return size_map.get(self.type, 20)
    
    def _get_color(self):
        color_map = {
            EnemyType.BASIC: (255, 100, 100),
            EnemyType.FAST: (100, 255, 100),
            EnemyType.HEAVY: (100, 100, 255),
            EnemyType.ELITE: (255, 255, 100),
            EnemyType.BOSS: (255, 0, 255)
        }
        return color_map.get(self.type, (255, 100, 100))
    
    def _get_damage(self):
        damage_map = {
            EnemyType.BASIC: 1,
            EnemyType.FAST: 1,
            EnemyType.HEAVY: 2,
            EnemyType.ELITE: 2,
            EnemyType.BOSS: 3
        }
        return damage_map.get(self.type, 1)
    
    def _get_score_value(self):
        score_map = {
            EnemyType.BASIC: 10,
            EnemyType.FAST: 20,
            EnemyType.HEAVY: 30,
            EnemyType.ELITE: 50,
            EnemyType.BOSS: 100
        }
        return score_map.get(self.type, 10)
    
    def _create_ai(self):
        ai_map = {
            EnemyType.BASIC: BasicEnemyAI(),
            EnemyType.FAST: FastEnemyAI(),
            EnemyType.HEAVY: HeavyEnemyAI(),
            EnemyType.ELITE: EliteEnemyAI(),
            EnemyType.BOSS: BossEnemyAI()
        }
        return ai_map.get(self.type, BasicEnemyAI())
    
    def update(self, player, game_state):
        if not self.alive:
            return
            
        # 更新AI行为
        self.ai.update(self, player, game_state)
        
        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # 更新特殊能力冷却
        if self.special_ability_cooldown > 0:
            self.special_ability_cooldown -= 1
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            # 绘制敌人飞船
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            
            # 绘制血条（对于有多个生命值的敌人）
            if self.max_health > 1:
                bar_width = self.size * 2
                bar_height = 5
                bar_x = self.x - bar_width // 2
                bar_y = self.y - self.size - 10
                
                pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                health_width = int(bar_width * (self.health / self.max_health))
                pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))