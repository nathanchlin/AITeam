class EnemyManager:
    def __init__(self, player):
        self.enemies = []
        self.enemy_factory = EnemyFactory()
        self.enemy_ai = EnemyAI(player)
        self.enemy_formation = EnemyFormation()
        self.bullets = []
        
    def update(self):
        # 更新敌机生成
        new_enemy = self.enemy_factory.update()
        if new_enemy:
            # 根据队形调整生成位置
            if len(self.enemies) < 5:  # 只有少量敌机时使用队形
                x, y = self.enemy_formation.get_spawn_position(
                    len(self.enemies), 
                    min(5, self.enemy_factory.enemies_spawned % 10 + 1)
                )
                new_enemy.x = x
                new_enemy.y = y
            self.enemies.append(new_enemy)
        
        # 更新队形
        self.enemy_formation.update()
        
        # 更新所有敌机
        for enemy in self.enemies[:]:
            if enemy.active:
                enemy.update()
                
                # AI控制射击
                bullet = self.enemy_ai.update(enemy)
                if bullet:
                    self.bullets.append(bullet)
            else:
                self.enemies.remove(enemy)
                
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                
    def draw(self, screen):
        # 绘制所有敌机
        for enemy in self.enemies:
            if enemy.active:
                # 这里应该有绘制敌机的代码
                # screen.blit(enemy.image, (enemy.x, enemy.y))
                pass
                
        # 绘制所有子弹
        for bullet in self.bullets:
            bullet.draw(screen)
            
    def get_all_enemies(self):
        return self.enemies
        
    def get_all_bullets(self):
        return self.bullets