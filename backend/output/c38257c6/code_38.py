import pygame
import sys

class GameUI:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("打砖块游戏")
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        
        # 字体初始化
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)
        
        # 游戏状态
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER
        self.score = 0
        self.lives = 3
        self.max_lives = 3
        
    def draw_background(self):
        """绘制游戏背景"""
        self.screen.fill(self.BLACK)
        
    def draw_score(self):
        """绘制得分显示"""
        score_text = self.font_medium.render(f"得分: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
    def draw_lives(self):
        """绘制生命值显示"""
        lives_text = self.font_medium.render(f"生命: {self.lives}", True, self.WHITE)
        self.screen.blit(lives_text, (self.screen_width - 150, 10))
        
        # 绘制生命值图标
        for i in range(self.lives):
            pygame.draw.circle(self.screen, self.RED, 
                             (self.screen_width - 100 + i * 30, 40), 10)
    
    def draw_menu(self):
        """绘制开始菜单"""
        self.draw_background()
        
        # 游戏标题
        title = self.font_large.render("打砖块游戏", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        self.screen.blit(title, title_rect)
        
        # 开始游戏按钮
        start_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2, 200, 50)
        pygame.draw.rect(self.screen, self.GREEN, start_button)
        start_text = self.font_small.render("开始游戏", True, self.BLACK)
        start_text_rect = start_text.get_rect(center=start_button.center)
        self.screen.blit(start_text, start_text_rect)
        
        # 退出按钮
        quit_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 70, 200, 50)
        pygame.draw.rect(self.screen, self.RED, quit_button)
        quit_text = self.font_small.render("退出游戏", True, self.BLACK)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        return start_button, quit_button
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        self.draw_background()
        
        # 游戏结束文本
        game_over_text = self.font_large.render("游戏结束", True, self.RED)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        self.screen.blit(game_over_text, game_over_rect)
        
        # 最终得分
        score_text = self.font_medium.render(f"最终得分: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(score_text, score_rect)
        
        # 重新开始按钮
        restart_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 50, 200, 50)
        pygame.draw.rect(self.screen, self.GREEN, restart_button)
        restart_text = self.font_small.render("重新开始", True, self.BLACK)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # 返回菜单按钮
        menu_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 120, 200, 50)
        pygame.draw.rect(self.screen, self.BLUE, menu_button)
        menu_text = self.font_small.render("返回菜单", True, self.WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_button.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        return restart_button, menu_button
    
    def draw_pause(self):
        """绘制暂停界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        pause_text = self.font_large.render("游戏暂停", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        self.screen.blit(pause_text, pause_rect)
        
        # 继续按钮
        continue_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2, 200, 50)
        pygame.draw.rect(self.screen, self.GREEN, continue_button)
        continue_text = self.font_small.render("继续游戏", True, self.BLACK)
        continue_text_rect = continue_text.get_rect(center=continue_button.center)
        self.screen.blit(continue_text, continue_text_rect)
        
        # 重新开始按钮
        restart_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 70, 200, 50)
        pygame.draw.rect(self.screen, self.BLUE, restart_button)
        restart_text = self.font_small.render("重新开始", True, self.WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # 返回菜单按钮
        menu_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 140, 200, 50)
        pygame.draw.rect(self.screen, self.RED, menu_button)
        menu_text = self.font_small.render("返回菜单", True, self.WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_button.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        return continue_button, restart_button, menu_button
    
    def draw_game_elements(self, paddle, ball, bricks):
        """绘制游戏元素（挡板、球、砖块）"""
        # 绘制挡板
        pygame.draw.rect(self.screen, self.WHITE, paddle)
        
        # 绘制球
        pygame.draw.circle(self.screen, self.WHITE, (ball.x, ball.y), ball.radius)
        
        # 绘制砖块
        for brick in bricks:
            pygame.draw.rect(self.screen, brick.color, brick.rect)
            pygame.draw.rect(self.screen, self.WHITE, brick.rect, 2)  # 砖块边框
    
    def update_score(self, points):
        """更新得分"""
        self.score += points
        
    def update_lives(self, change):
        """更新生命值"""
        self.lives = max(0, min(self.max_lives, self.lives + change))
        
    def reset_game(self):
        """重置游戏状态"""
        self.score = 0
        self.lives = self.max_lives