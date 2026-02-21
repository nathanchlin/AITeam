import json
import os

class GameStateSaver:
    def __init__(self, save_file="savegame.json"):
        self.save_file = save_file
    
    def save_game(self, game_data):
        """保存游戏状态"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(game_data, f)
            return True
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def load_game(self):
        """加载游戏状态"""
        if not os.path.exists(self.save_file):
            return None
        
        try:
            with open(self.save_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载游戏失败: {e}")
            return None
    
    def delete_save(self):
        """删除存档"""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
            return True
        return False