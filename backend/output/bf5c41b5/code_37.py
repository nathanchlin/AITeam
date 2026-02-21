class GameRenderer:
    def __init__(self, game):
        self.game = game
        
    def render_game(self):
        """渲染游戏界面"""
        status = self.game.get_game_status()
        
        # 渲染分数
        self._render_text(f"Score: {status['score']}", (10, 10))
        
        # 渲染生命值
        self._render_text(f"Lives: {'❤' * status['lives']}", (10, 40))
        
        # 渲染连击信息
        if status['combo'] > 0:
            combo_text = f"Combo: x{status['combo']} (Multiplier: x{status['combo_multiplier']})"
            self._render_text(combo_text, (10, 70))
            
        # 渲染游戏结束或胜利信息
        if status['game_over']:
            self._render_text("GAME OVER", (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2))
            self._render_text(f"Final Score: {status['score']}", (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 30))
        elif status['all_bricks_cleared']:
            self._render_text("YOU WIN!", (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))
            self._render_text(f"Final Score: {status['score']}", (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 30))
            
    def _render_text(self, text, position):
        """渲染文本到指定位置"""
        # 实现文本渲染逻辑
        pass