import time
from threading import Timer

class GameEngine:
    def __init__(self, config: GameConfig, renderer: Renderer):
        self.config = config
        self.renderer = renderer
        self.state_manager = GameStateManager(config)
        self.is_running = False
        self.last_update_time = time.time()
        
        # 设置键盘输入观察者
        self.input_handler = InputHandler(self.state_manager)
        self.state_manager.add_observer(self.renderer)
    
    def run(self):
        self.is_running = True
        self.renderer.render(self.state_manager.state)
        
        # 初始计时器
        self._schedule_update()
        
        # 主循环
        while self.is_running:
            # 处理输入
            self.input_handler.handle_input()
            
            # 渲染
            self.renderer.render(self.state_manager.state)
            
            # 检查游戏是否结束
            if self.state_manager.state.is_game_over:
                self.is_running = False
        
        self.renderer.clear()
        print("Game ended. Final score:", self.state_manager.state.score)
    
    def _schedule_update(self):
        if self.is_running:
            # 计算下次更新的时间
            current_time = time.time()
            elapsed = current_time - self.last_update_time
            update_interval = 1.0 / self.config.game_speed
            
            if elapsed >= update_interval:
                self.state_manager.update(elapsed)
                self.last_update_time = current_time
            else:
                # 如果更新间隔未到，等待剩余时间
                Timer(update_interval - elapsed, self._schedule_update).start()
    
    def stop(self):
        self.is_running = False