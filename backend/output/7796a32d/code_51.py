import pygame.mixer

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.load_sounds()
    
    def load_sounds(self):
        """加载所有音效"""
        try:
            # 跳跃音效
            self.sounds['jump'] = pygame.mixer.Sound('sounds/jump.wav')
            self.sounds['jump'].set_volume(self.sound_volume)
            
            # 落地音效
            self.sounds['land'] = pygame.mixer.Sound('sounds/land.wav')
            self.sounds['land'].set_volume(self.sound_volume)
            
            # 平台破碎音效
            self.sounds['break'] = pygame.mixer.Sound('sounds/break.wav')
            self.sounds['break'].set_volume(self.sound_volume)
            
            # 收集道具音效
            self.sounds['collect'] = pygame.mixer.Sound('sounds/collect.wav')
            self.sounds['collect'].set_volume(self.sound_volume)
            
            # 游戏结束音效
            self.sounds['game_over'] = pygame.mixer.Sound('sounds/game_over.wav')
            self.sounds['game_over'].set_volume(self.sound_volume)
            
            # 背景音乐
            pygame.mixer.music.load('sounds/background.mp3')
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # 循环播放
            
        except pygame.error as e:
            print(f"无法加载音效: {e}")
            self.sounds = {}
    
    def play_sound(self, sound_name):
        """播放指定音效"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def stop_music(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
    
    def resume_music(self):
        """恢复背景音乐"""
        pygame.mixer.music.play(-1)
    
    def set_music_volume(self, volume):
        """设置音乐音量"""
        self.music_volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        """设置音效音量"""
        self.sound_volume = max(0, min(1, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)