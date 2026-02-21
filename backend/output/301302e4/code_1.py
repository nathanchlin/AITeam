import pygame
import sys
from enum import Enum

class UIController:
    def __init__(self, screen_width, screen_height):
        # 初始化Pygame
        pygame.init()
        
        # 屏幕设置
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("愤怒的小鸟")
        
        # 游戏状态
        self.current_state = GameState.MENU
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 颜色定义
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        
        # 字体设置
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 32)
        self.text_font = pygame.font.SysFont('Arial', 24)
        
        # 按钮
        self.buttons = {}
        self.init_buttons()
        
        # 关卡数据
        self.levels = [
            {"name": "Level 1", "unlocked": True, "score": 0},
            {"name": "Level 2", "unlocked": False, "score": 0},
            {"name": "Level 3", "unlocked": False, "score": 0},
            {"name": "Level 4", "unlocked": False, "score": 0},
            {"name": "Level 5", "unlocked": False, "score": 0}
        ]
        self.current_level = 0
        
    def init_buttons(self):
        """初始化所有按钮"""
        # 主菜单按钮
        self.buttons["start"] = pygame.Rect(self.screen_width//2 - 100, 250, 200, 50)
        self.buttons["level_select"] = pygame.Rect(self.screen_width//2 - 100, 320, 200, 50)
        self.buttons["quit"] = pygame.Rect(self.screen_width//2 - 100, 390, 200, 50)
        
        # 关卡选择按钮
        self.buttons["back"] = pygame.Rect(50, 50, 100, 40)
        for i in range(5):
            self.buttons[f"level_{i}"] = pygame.Rect(
                self.screen_width//2 - 100, 
                150 + i * 80, 
                200, 
                60
            )
        
        # 游戏控制按钮
        self.buttons["pause"] = pygame.Rect(self.screen_width - 120, 20, 100, 40)
        self.buttons["restart"] = pygame.Rect(20, 20, 100, 40)
        self.buttons["menu"] = pygame.Rect(self.screen_width//2 - 50, self.screen_height//2 + 50, 100, 40)
        
    def draw_button(self, button_rect, text, color=GREEN, text_color=WHITE):
        """绘制按钮"""
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        text_surface = self.button_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(self.WHITE)
        
        # 标题
        title = self.title_font.render("愤怒的小鸟", True, self.RED)
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title, title_rect)
        
        # 按钮
        self.draw_button(self.buttons["start"], "开始游戏")
        self.draw_button(self.buttons["level_select"], "选择关卡")
        self.draw_button(self.buttons["quit"], "退出游戏")
        
    def draw_level_select(self):
        """绘制关卡选择界面"""
        self.screen.fill(self.WHITE)
        
        # 标题
        title = self.title_font.render("选择关卡", True, self.RED)
        title_rect = title.get_rect(center=(self.screen_width//2, 50))
        self.screen.blit(title, title_rect)
        
        # 返回按钮
        self.draw_button(self.buttons["back"], "返回", self.BLUE)
        
        # 关卡按钮
        for i, level in enumerate(self.levels):
            if level["unlocked"]:
                color = self.GREEN
                text = f"{level['name']} - 最高分: {level['score']}"
            else:
                color = self.GRAY = (128, 128, 128)
                text = f"{level['name']} - 未解锁"
                
            self.draw_button(self.buttons[f"level_{i}"], text, color)
            
    def draw_game(self):
        """绘制游戏界面"""
        self.screen.fill(self.WHITE)
        
        # 绘制游戏元素（这里简化为背景色）
        pygame.draw.rect(self.screen, (135, 206, 235), (0, 0, self.screen_width, self.screen_height//2))
        pygame.draw.rect(self.screen, (34, 139, 34), (0, self.screen_height//2, self.screen_width, self.screen_height//2))
        
        # 绘制控制按钮
        self.draw_button(self.buttons["pause"], "暂停", self.BLUE)
        self.draw_button(self.buttons["restart"], "重新开始", self.YELLOW)
        
        # 显示当前关卡信息
        level_text = self.text_font.render(f"当前关卡: {self.levels[self.current_level]['name']}", True, self.BLACK)
        self.screen.blit(level_text, (20, 70))
        
    def draw_pause(self):
        """绘制暂停界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        pause_text = self.title_font.render("游戏暂停", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # 按钮
        self.draw_button(self.buttons["menu"], "返回主菜单", self.RED)
        self.draw_button(self.buttons["restart"], "重新开始", self.YELLOW)
        
    def handle_menu_events(self, event):
        """处理主菜单事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["start"].collidepoint(event.pos):
                self.current_state = GameState.PLAYING
                self.load_level(self.current_level)
            elif self.buttons["level_select"].collidepoint(event.pos):
                self.current_state = GameState.LEVEL_SELECT
            elif self.buttons["quit"].collidepoint(event.pos):
                self.running = False
                
    def handle_level_select_events(self, event):
        """处理关卡选择事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["back"].collidepoint(event.pos):
                self.current_state = GameState.MENU
            else:
                for i in range(5):
                    if self.buttons[f"level_{i}"].collidepoint(event.pos) and self.levels[i]["unlocked"]:
                        self.current_level = i
                        self.current_state = GameState.PLAYING
                        self.load_level(i)
                        
    def handle_game_events(self, event):
        """处理游戏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["pause"].collidepoint(event.pos):
                self.current_state = GameState.PAUSED
            elif self.buttons["restart"].collidepoint(event.pos):
                self.load_level(self.current_level)
                
    def handle_pause_events(self, event):
        """处理暂停事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["menu"].collidepoint(event.pos):
                self.current_state = GameState.MENU
            elif self.buttons["restart"].collidepoint(event.pos):
                self.load_level(self.current_level)
                self.current_state = GameState.PLAYING
                
    def load_level(self, level_index):
        """加载关卡"""
        # 这里应该是加载关卡数据的逻辑
        # 简化为解锁下一关
        if level_index < len(self.levels) - 1:
            self.levels[level_index + 1]["unlocked"] = True
            
    def update(self):
        """更新游戏状态"""
        # 这里可以添加游戏逻辑更新
        
    def draw(self):
        """根据当前状态绘制界面"""
        if self.current_state == GameState.MENU:
            self.draw_menu()
        elif self.current_state == GameState.LEVEL_SELECT:
            self.draw_level_select()
        elif self.current_state == GameState.PLAYING:
            self.draw_game()
        elif self.current_state == GameState.PAUSED:
            self.draw_game()  # 先绘制游戏画面
            self.draw_pause()  # 再绘制暂停覆盖层
            
    def run(self):
        """运行游戏主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.current_state == GameState.MENU:
                    self.handle_menu_events(event)
                elif self.current_state == GameState.LEVEL_SELECT:
                    self.handle_level_select_events(event)
                elif self.current_state == GameState.PLAYING:
                    self.handle_game_events(event)
                elif self.current_state == GameState.PAUSED:
                    self.handle_pause_events(event)
                    
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

# 使用示例
if __name__ == "__main__":
    game_ui = UIController(800, 600)
    game_ui.run()