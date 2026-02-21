class MenuState(StateCallback):
    def on_enter(self, previous_state, *args, **kwargs):
        print("进入主菜单")
        # 显示主菜单UI
        
    def on_exit(self):
        print("退出主菜单")
        # 隐藏主菜单UI

class PlayingState(StateCallback):
    def __init__(self, game):
        self.game = game
        
    def on_enter(self, previous_state, *args, **kwargs):
        print("进入游戏进行中状态")
        if previous_state == GameState.READY:
            self.game.start_new_game()
        # 恢复游戏逻辑和渲染
            
    def on_exit(self):
        print("退出游戏进行中状态")
        # 暂停游戏逻辑和渲染

class PausedState(StateCallback):
    def on_enter(self, previous_state, *args, **kwargs):
        print("进入暂停状态")
        # 显示暂停菜单
        
    def on_exit(self):
        print("退出暂停状态")
        # 隐藏暂停菜单

class GameOverState(StateCallback):
    def on_enter(self, previous_state, *args, **kwargs):
        print("进入游戏结束状态")
        # 显示游戏结束画面和分数
        
    def on_exit(self):
        print("退出游戏结束状态")
        # 隐藏游戏结束画面