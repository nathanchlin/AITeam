import pygame
import sys
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_SIZE = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 60
BRICK_OFFSET_LEFT = 35

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class GameUI:
    def __init__(self):
        # 设置游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("打砖块游戏")
        
        # 初始化游戏状态
        self.score = 0
        self.lives = 3
        self.game_state = "START"  # START, PLAYING, PAUSED, GAME_OVER
        
        # 字体初始化
        self.font_large = pygame.font.SysFont('Arial', 36)
        self.font_medium = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 18)
        
        # 游戏对象初始化
        self.paddle = pygame.Rect(
            (SCREEN_WIDTH - PADDLE_WIDTH) // 2,
            SCREEN_HEIGHT - PADDLE_HEIGHT - 10,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )
        
        self.ball = pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT - PADDLE_HEIGHT - BALL_SIZE - 10,
            BALL_SIZE,
            BALL_SIZE
        )
        
        # 球的速度
        self.ball_speed_x = 4
        self.ball_speed_y = -4
        
        # 初始化砖块
        self.bricks = []
        self.init_bricks()
    
    def init_bricks(self):
        """初始化砖块"""
        self.bricks = []
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        for row in range(BRICK_ROWS):
            brick_row = []
            for col in range(BRICK_COLS):
                brick = pygame.Rect(
                    col * (BRICK_WIDTH + BRICK_PADDING) + BRICK_OFFSET_LEFT,
                    row * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_OFFSET_TOP,
                    BRICK_WIDTH,
                    BRICK_HEIGHT
                )
                brick_row.append({
                    'rect': brick,
                    'color': colors[row],
                    'visible': True
                })
            self.bricks.append(brick_row)
    
    def draw(self):
        """绘制游戏界面"""
        # 清屏
        self.screen.fill(BLACK)
        
        # 绘制游戏元素
        if self.game_state == "START":
            self.draw_start_screen()
        elif self.game_state == "PLAYING" or self.game_state == "PAUSED":
            self.draw_game_elements()
            if self.game_state == "PAUSED":
                self.draw_pause_screen()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over_screen()
        
        # 更新显示
        pygame.display.flip()
    
    def draw_start_screen(self):
        """绘制开始界面"""
        title = self.font_large.render("打砖块游戏", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "按空格键开始游戏",
            "使用左右方向键控制挡板",
            "消除所有砖块获胜",
            "球掉落会失去一条生命"
        ]
        
        y = 250
        for line in instructions:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30
    
    def draw_game_elements(self):
        """绘制游戏元素"""
        # 绘制砖块
        for row in self.bricks:
            for brick in row:
                if brick['visible']:
                    pygame.draw.rect(self.screen, brick['color'], brick['rect'])
                    pygame.draw.rect(self.screen, WHITE, brick['rect'], 1)
        
        # 绘制挡板
        pygame.draw.rect(self.screen, WHITE, self.paddle)
        
        # 绘制球
        pygame.draw.ellipse(self.screen, WHITE, self.ball)
        
        # 绘制得分和生命值
        score_text = self.font_medium.render(f"得分: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font_medium.render(f"生命: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
    
    def draw_pause_screen(self):
        """绘制暂停界面"""
        pause_text = self.font_large.render("游戏暂停", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font_small.render("按P键继续游戏", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def draw_game_over_screen(self):
        """绘制游戏结束界面"""
        game_over_text = self.font_large.render("游戏结束", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font_medium.render(f"最终得分: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_small.render("按空格键重新开始", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def update(self):
        """更新游戏状态"""
        if self.game_state == "PLAYING":
            # 移动球
            self.ball.x += self.ball_speed_x
            self.ball.y += self.ball_speed_y
            
            # 球碰到左右墙壁
            if self.ball.left <= 0 or self.ball.right >= SCREEN_WIDTH:
                self.ball_speed_x = -self.ball_speed_x
            
            # 球碰到顶部墙壁
            if self.ball.top <= 0:
                self.ball_speed_y = -self.ball_speed_y
            
            # 球掉落
            if self.ball.bottom >= SCREEN_HEIGHT:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_state = "GAME_OVER"
                else:
                    # 重置球的位置
                    self.ball.centerx = SCREEN_WIDTH // 2
                    self.ball.bottom = SCREEN_HEIGHT - PADDLE_HEIGHT - BALL_SIZE - 10
                    self.ball_speed_y = -4
            
            # 球碰到挡板
            if self.ball.colliderect(self.paddle) and self.ball_speed_y > 0:
                # 根据球击中挡板的位置改变反弹角度
                hit_pos = (self.ball.centerx - self.paddle.left) / PADDLE_WIDTH
                self.ball_speed_x = 8 * (hit_pos - 0.5)
                self.ball_speed_y = -self.ball_speed_y
            
            # 球碰到砖块
            for row in self.bricks:
                for brick in row:
                    if brick['visible'] and self.ball.colliderect(brick['rect']):
                        brick['visible'] = False
                        self.ball_speed_y = -self.ball_speed_y
                        self.score += 10
                        
                        # 检查是否所有砖块都被消除
                        if all(not brick['visible'] for row in self.bricks for brick in row):
                            self.game_state = "GAME_OVER"
            
            # 移动挡板
            keys = pygame.key.get_pressed()
            if keys[K_LEFT] and self.paddle.left > 0:
                self.paddle.x -= 6
            if keys[K_RIGHT] and self.paddle.right < SCREEN_WIDTH:
                self.paddle.x += 6
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.game_state == "START" or self.game_state == "GAME_OVER":
                        # 重置游戏
                        self.score = 0
                        self.lives = 3
                        self.game_state = "PLAYING"
                        self.init_bricks()
                        self.ball.centerx = SCREEN_WIDTH // 2
                        self.ball.bottom = SCREEN_HEIGHT - PADDLE_HEIGHT - BALL_SIZE - 10
                        self.ball_speed_x = 4
                        self.ball_speed_y = -4
                    elif self.game_state == "PAUSED":
                        self.game_state = "PLAYING"
                
                if event.key == K_p and self.game_state == "PLAYING":
                    self.game_state = "PAUSED"
    
    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()
        
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)  # 限制帧率为60FPS

# 运行游戏
if __name__ == "__main__":
    game = GameUI()
    game.run()