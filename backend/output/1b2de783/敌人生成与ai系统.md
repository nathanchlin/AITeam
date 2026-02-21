# 敌人生成与AI系统

**Agent**: coder

**Time**: 2026-02-18T13:03:14.777012

---

# 敌人生成与AI系统实现

我将为太空射击游戏设计一个完整的敌人生成与AI系统，包括不同类型的敌人、生成机制、移动模式和AI行为。

## 系统设计概述

1. **敌人类型系统**：定义多种敌人类型，每种有独特属性和行为
2. **生成系统**：基于游戏进度和难度动态生成敌人
3. **移动模式**：多样化的移动轨迹和速度
4. **AI行为**：包括攻击模式、躲避行为和特殊能力

## 代码实现

### 1. 敌人基类和类型定义

```python
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
```

### 2. AI行为实现

```python
class BasicEnemyAI(EnemyAI):
    def update(self, enemy, player, game_state):
        # 基本敌人：直线向下移动，偶尔射击
        enemy.y += enemy.speed
        
        # 随机射击
        if random.random() < 0.01 and enemy.shoot_cooldown == 0:
            enemy.shoot_cooldown = 60  # 1秒冷却（假设60FPS）
            return "shoot"
        
        return None

class FastEnemyAI(EnemyAI):
    def update(self, enemy, player, game_state):
        # 快速敌人：Z字形移动，频繁射击
        enemy.y += enemy.speed * 0.7
        enemy.x += math.sin(enemy.y * 0.05) * 3
        
        # 频繁射击
        if random.random() < 0.03 and enemy.shoot_cooldown == 0:
            enemy.shoot_cooldown = 30
            return "shoot"
        
        return None

class HeavyEnemyAI(EnemyAI):
    def update(self, enemy, player, game_state):
        # 重型敌人：缓慢移动，发射多发子弹
        enemy.y += enemy.speed * 0.5
        
        # 发射扇形子弹
        if random.random() < 0.02 and enemy.shoot_cooldown == 0:
            enemy.shoot_cooldown = 90
            return "spread_shoot"
        
        return None

class EliteEnemyAI(EnemyAI):
    def update(self, enemy, player, game_state):
        # 精英敌人：追踪玩家，发射追踪弹
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            enemy.x += (dx / distance) * enemy.speed * 0.7
            enemy.y += (dy / distance) * enemy.speed * 0.7
        
        # 发射追踪弹
        if random.random() < 0.02 and enemy.shoot_cooldown == 0:
            enemy.shoot_cooldown = 45
            return "homing_shoot"
        
        # 特殊能力：短暂加速
        if enemy.special_ability_cooldown == 0 and random.random() < 0.01:
            enemy.special_ability_cooldown = 300  # 5秒冷却
            enemy.speed *= 2
            return "boost"
        elif enemy.special_ability_cooldown == 0 and enemy.speed > enemy._get_speed():
            enemy.speed = enemy._get_speed()
        
        return None

class BossEnemyAI(EnemyAI):
    def update(self, enemy, player, game_state):
        # Boss敌人：复杂移动模式，多种攻击方式
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # 圆形运动
        angle = math.atan2(dy, dx) + 0.02
        target_x = player.x - math.cos(angle) * 200
        target_y = player.y - math.sin(angle) * 200
        
        enemy.x += (target_x - enemy.x) * 0.02
        enemy.y += (target_y - enemy.y) * 0.02
        
        # 多种攻击模式
        attack_choice = random.random()
        
        if attack_choice < 0.3 and enemy.shoot_cooldown == 0:
            # 扇形射击
            enemy.shoot_cooldown = 60
            return "spread_shoot"
        elif attack_choice < 0.6 and enemy.shoot_cooldown == 0:
            # 环形射击
            enemy.shoot_cooldown = 90
            return "ring_shoot"
        elif attack_choice < 0.8 and enemy.shoot_cooldown == 0:
            # 追踪弹
            enemy.shoot_cooldown = 45
            return "homing_shoot"
        elif attack_choice < 0.9 and enemy.special_ability_cooldown == 0:
            # 召唤小敌人
            enemy.special_ability_cooldown = 300
            return "summon"
        
        return None
```

### 3. 敌人生成系统

```python
class EnemySpawner:
    def __init__(self, game_settings):
        self.game_settings = game_settings
        self.spawn_timer = 0
        self.difficulty_level = 1
        self.enemies_to_spawn = []
        self.boss_spawned = False
        
    def update(self, player, enemies, game_state):
        # 根据分数调整难度
        self.difficulty_level = 1 + player.score // 100
        
        # 更新生成计时器
        self.spawn_timer += 1
        
        # 根据难度调整生成间隔
        spawn_interval = max(30, 120 - self.difficulty_level * 5)
        
        # 生成敌人
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            self._decide_spawn(player, enemies, game_state)
    
    def _decide_spawn(self, player, enemies, game_state):
        # 根据游戏状态决定生成什么敌人
        if not self.boss_spawned and player.score >= 500 and len(enemies) < 3:
            # 生成Boss
            self._spawn_boss(player)
            self.boss_spawned = True
        else:
            # 根据难度和随机性决定生成普通敌人
            spawn_roll = random.random()
            
            # 根据难度增加高级敌人的概率
            elite_chance = min(0.2, self.difficulty_level * 0.02)
            heavy_chance = min(0.3, self.difficulty_level * 0.03)
            fast_chance = min(0.4, self.difficulty_level * 0.04)
            
            if spawn_roll < elite_chance:
                self._spawn_elite(player)
            elif spawn_roll < elite_chance + heavy_chance:
                self._spawn_heavy(player)
            elif spawn_roll < elite_chance + heavy_chance + fast_chance:
                self._spawn_fast(player)
            else:
                self._spawn_basic(player)
    
    def _spawn_basic(self, player):
        # 在屏幕上方随机位置生成基础敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.BASIC, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_fast(self, player):
        # 在屏幕上方随机位置生成快速敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.FAST, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_heavy(self, player):
        # 在屏幕上方随机位置生成重型敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.HEAVY, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_elite(self, player):
        # 在屏幕上方随机位置生成精英敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.ELITE, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_boss(self, player):
        # 在屏幕上方中间位置生成Boss
        x = self.game_settings["screen_width"] // 2
        y = -100
        enemy = Enemy(x, y, EnemyType.BOSS, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def get_enemies_to_spawn(self):
        return self.enemies_to_spawn
    
    def clear_spawned_enemies(self):
        self.enemies_to_spawn = []
```

### 4. 敌人子弹系统

```python
class EnemyBullet:
    def __init__(self, x, y, bullet_type, target=None):
        self.x = x
        self.y = y
        self.type = bullet_type
        self.target = target
        self.speed = self._get_speed()
        self.damage = self._get_damage()
        self.size = self._get_size()
        self.color = self._get_color()
        self.alive = True
        
    def _get_speed(self):
        speed_map = {
            "basic": 5,
            "fast": 7,
            "heavy": 3,
            "homing": 4,
            "spread": 5
        }
        return speed_map.get(self.type, 5)
    
    def _get_damage(self):
        damage_map = {
            "basic": 1,
            "fast": 1,
            "heavy": 2,
            "homing": 1,
            "spread": 1
        }
        return damage_map.get(self.type, 1)
    
    def _get_size(self):
        size_map = {
            "basic": 5,
            "fast": 4,
            "heavy": 8,
            "homing": 6,
            "spread": 5
        }
        return size_map.get(self.type, 5)
    
    def _get_color(self):
        color_map = {
            "basic": (255, 100, 100),
            "fast": (100, 255, 100),
            "heavy": (100, 100, 255),
            "homing": (255, 255, 100),
            "spread": (255, 150, 150)
        }
        return color_map.get(self.type, (255, 100, 100))
    
    def update(self):
        if not self.alive:
            return
            
        if self.type == "homing" and self.target and self.target.alive:
            # 追踪弹逻辑
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        else:
            # 直线移动
            self.y += self.speed
        
        # 检查是否超出屏幕
        if self.y > 800 or self.y < 0 or self.x > 800 or self.x < 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
```

### 5. 游戏主系统集成

```python
class Game:
    def __init__(self):
        self.settings = {
            "screen_width": 800,
            "screen_height": 600,
            "fps": 60
        }
        self.player = Player(self.settings)
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.enemy_spawner = EnemySpawner(self.settings)
        self.score = 0
        self.game_state = "playing"
        
    def update(self):
        if self.game_state != "playing":
            return
            
        # 更新玩家
        self.player.update()
        
        # 更新敌人生成器
        self.enemy_spawner.update(self.player, self.enemies, self)
        
        # 生成新敌人
        new_enemies = self.enemy_spawner.get_enemies_to_spawn()
        for enemy in new_enemies:
            self.enemies.append(enemy)
        self.enemy_spawner.clear_spawned_enemies()
        
        # 更新敌人
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.score += enemy.score_value
                continue
                
            enemy_action = enemy.update(self.player, self)
            
            # 处理敌人行动
            if enemy_action == "shoot":
                # 发射普通子弹
                bullet = EnemyBullet(enemy.x, enemy.y + enemy.size, "basic")
                self.enemy_bullets.append(bullet)
            elif enemy_action == "spread_shoot":
                # 发射扇形子弹
                for angle in [-30, 0, 30]:
                    rad = math.radians(angle)
                    dx = math.sin(rad) * 5
                    dy = math.cos(rad) * 5
                    bullet = EnemyBullet(enemy.x + dx, enemy.y + enemy.size, "spread")
                    self.enemy_bullets.append(bullet)
            elif enemy_action == "homing_shoot":
                # 发射追踪弹
                bullet = EnemyBullet(enemy.x, enemy.y + enemy.size, "homing", self.player)
                self.enemy_bullets.append(bullet)
            elif enemy_action == "ring_shoot":
                # Boss环形射击
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    dx = math.sin(rad) * 5
                    dy = math.cos(rad) * 5
                    bullet = EnemyBullet(enemy.x + dx, enemy.y + enemy.size, "basic")
                    self.enemy_bullets.append(bullet)
            elif enemy_action == "summon":
                # Boss召唤