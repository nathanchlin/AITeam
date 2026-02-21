class Game:
    def __init__(self):
        self.ui = GameUI(800, 600)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏对象初始化
        self.paddle = pygame.Rect(self.ui.screen_width // 2 - 50, self.ui.screen_height - 30, 100, 15)
        self.ball = Ball(self.ui.screen_width // 2, self.ui.screen_height - 50)
        self.bricks = self.create_bricks()
        
        # 按钮变量
        self.menu_buttons = None
        self.game_over_buttons = None
        self.pause_buttons = None
        
    def create_bricks(self):
        """创建砖块"""
        bricks = []
        rows = 5
        cols = 10
        brick_width = 70
        brick_height = 20
        padding = 5
        offset_x = (self.ui.screen_width - (cols * (brick_width + padding))) // 2
        offset_y = 60
        
        colors = [self.ui.RED, self.ui.ORANGE, self.ui.YELLOW, self.ui.GREEN, self.ui.BLUE]
        
        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (brick_width + padding)
                y = offset_y + row * (brick_height + padding)
                brick = pygame.Rect(x, y, brick_width, brick_height)
                color = colors[row % len(colors)]
                bricks.append(Brick(brick, color))
                
        return bricks
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.ui.game_state == "MENU":
                    start_button, quit_button = self.menu_buttons
                    if start_button.collidepoint(mouse_pos):
                        self.ui.game_state = "PLAYING"
                        self.ui.reset_game()
                    elif quit_button.collidepoint(mouse_pos):
                        self.running = False
                        
                elif self.ui.game_state == "PLAYING":
                    # 检查是否点击了暂停按钮（可以添加一个暂停按钮）
                    pass
                    
                elif self.ui.game_state == "PAUSED":
                    continue_button, restart_button, menu_button = self.pause_buttons
                    if continue_button.collidepoint(mouse_pos):
                        self.ui.game_state = "PLAYING"
                    elif restart_button.collidepoint(mouse_pos):
                        self.ui.game_state = "PLAYING"
                        self.ui.reset_game()
                        self.bricks = self.create_bricks()
                    elif menu_button.collidepoint(mouse_pos):
                        self.ui.game_state = "MENU"
                        
                elif self.ui.game_state == "GAME_OVER":
                    restart_button, menu_button = self.game_over_buttons
                    if restart_button.collidepoint(mouse_pos):
                        self.ui.game_state = "PLAYING"
                        self.ui.reset_game()
                        self.bricks = self.create_bricks()
                    elif menu_button.collidepoint(mouse_pos):
                        self.ui.game_state = "MENU"
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.ui.game_state == "PLAYING":
                    self.ui.game_state = "PAUSED"
    
    def update(self):
        """更新游戏状态"""
        if self.ui.game_state == "PLAYING":
            # 更新挡板位置
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.paddle.left > 0:
                self.paddle.x -= 7
            if keys[pygame.K_RIGHT] and self.paddle.right < self.ui.screen_width:
                self.paddle.x += 7
                
            # 更新球位置
            self.ball.move()
            
            # 球与墙壁碰撞检测
            if self.ball.x <= self.ball.radius or self.ball.x >= self.ui.screen_width - self.ball.radius:
                self.ball.dx = -self.ball.dx
            if self.ball.y <= self.ball.radius:
                self.ball.dy = -self.ball.dy
                
            # 球与挡板碰撞检测
            if self.ball.dy > 0 and self.ball.rect.colliderect(self.paddle):
                self.ball.dy = -self.ball.dy
                # 根据击中挡板的位置调整反弹角度
                hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
                self.ball.dx = 8 * (hit_pos - 0.5)
                
            # 球与砖块碰撞检测
            for brick in self.bricks[:]:
                if self.ball.rect.colliderect(brick.rect):
                    self.bricks.remove(brick)
                    self.ball.dy = -self.ball.dy
                    self.ui.update_score(10)
                    
                    # 检查是否所有砖块都被消除
                    if not self.bricks:
                        self.ui.game_state = "GAME_OVER"
                    break
                    
            # 球掉落检测
            if self.ball.y > self.ui.screen_height:
                self.ui.update_lives(-1)
                if self.ui.lives <= 0:
                    self.ui.game_state = "GAME_OVER"
                else:
                    # 重置球的位置
                    self.ball = Ball(self.ui.screen_width // 2, self.ui.screen_height - 50)
    
    def draw(self):
        """绘制游戏画面"""
        if self.ui.game_state == "MENU":
            self.menu_buttons = self.ui.draw_menu()
            
        elif self.ui.game_state == "PLAYING":
            self.ui.draw_background()
            self.ui.draw_score()
            self.ui.draw_lives()
            self.ui.draw_game_elements(self.paddle, self.ball, self.bricks)
            
        elif self.ui.game_state == "PAUSED":
            # 先绘制游戏元素
            self.ui.draw_background()
            self.ui.draw_score()
            self.ui.draw_lives()
            self.ui.draw_game_elements(self.paddle, self.ball, self.bricks)
            
            # 再绘制暂停界面
            self.pause_buttons = self.ui.draw_pause()
            
        elif self.ui.game_state == "GAME_OVER":
            self.game_over_buttons = self.ui.draw_game_over()
            
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

# 辅助类
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.dx = 4
        self.dy = -4
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        
    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Brick:
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()