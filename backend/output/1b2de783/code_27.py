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