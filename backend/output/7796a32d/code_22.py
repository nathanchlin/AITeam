import pygame
import math

class PhysicsEngine:
    def __init__(self):
        # 物理常量
        self.gravity = 0.8  # 重力加速度
        self.max_fall_speed = 15  # 最大下落速度
        self.damping = 0.9  # 碰撞后的速度衰减
        
    def apply_gravity(self, player):
        """应用重力效果"""
        player.velocity_y += self.gravity
        # 限制最大下落速度
        if player.velocity_y > self.max_fall_speed:
            player.velocity_y = self.max_fall_speed
    
    def update_position(self, player, platforms):
        """更新角色位置并处理碰撞"""
        # 应用重力
        self.apply_gravity(player)
        
        # 更新垂直位置
        player.y += player.velocity_y
        
        # 碰撞检测
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        # 检查与平台的碰撞
        on_platform = False
        for platform in platforms:
            platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            
            # 垂直碰撞检测
            if player_rect.colliderect(platform_rect):
                # 从上方落到平台上
                if player.velocity_y > 0 and player.y < platform.y:
                    player.y = platform.y - player.height
                    player.velocity_y = 0
                    player.on_ground = True
                    on_platform = True
                # 从下方撞到平台
                elif player.velocity_y < 0 and player.y > platform.y:
                    player.y = platform.y + platform.height
                    player.velocity_y = 0
                # 从侧面碰撞
                else:
                    # 简单处理：反弹
                    player.velocity_y *= -self.damping
        
        # 如果没有站在平台上，则不在地面上
        if not on_platform:
            player.on_ground = False

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 50
        self.velocity_y = 0
        self.on_ground = False
        self.color = (255, 0, 0)  # 红色角色
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (0, 0, 255)  # 蓝色平台
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("是男人就下100层")
        self.clock = pygame.time.Clock()
        
        # 初始化游戏对象
        self.player = Player(self.width // 2 - 15, 100)
        self.physics = PhysicsEngine()
        
        # 创建平台
        self.platforms = []
        self.generate_platforms()
        
        self.running = True
        
    def generate_platforms(self):
        """生成随机平台"""
        import random
        
        # 起始平台
        self.platforms.append(Platform(self.width // 2 - 50, 150, 100, 20))
        
        # 生成后续平台
        for i in range(1, 100):
            x = random.randint(0, self.width - 100)
            y = 150 + i * 60  # 每60像素一个平台
            width = random.randint(80, 150)
            self.platforms.append(Platform(x, y, width, 20))
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player.on_ground:
                    # 跳跃
                    self.player.velocity_y = -15
    
    def update(self):
        """更新游戏状态"""
        # 处理左右移动
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.x -= 5
        if keys[pygame.K_RIGHT]:
            self.player.x += 5
            
        # 限制玩家在屏幕范围内
        self.player.x = max(0, min(self.width - self.player.width, self.player.x))
        
        # 更新物理
        self.physics.update_position(self.player, self.platforms)
        
        # 如果玩家掉出屏幕底部，游戏结束
        if self.player.y > self.height:
            self.running = False
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill((255, 255, 255))  # 白色背景
        
        # 绘制平台
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # 绘制玩家
        self.player.draw(self.screen)
        
        # 显示楼层信息
        font = pygame.font.SysFont(None, 36)
        floor_text = font.render(f"Floor: {int((self.player.y - 150) / 60) + 1}", True, (0, 0, 0))
        self.screen.blit(floor_text, (10, 10))
        
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()