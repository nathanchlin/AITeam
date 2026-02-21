import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()
        self.background_music = None
        self.music_playing = False
        
    def load_sounds(self):
        """加载所有音效文件"""
        sound_files = {
            'jump': 'sounds/jump.wav',
            'collision': 'sounds/collision.wav',
            'score': 'sounds/score.wav'
        }
        
        for sound_name, sound_path in sound_files.items():
            try:
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                else:
                    print(f"警告: 音效文件 {sound_path} 未找到")
            except pygame.error as e:
                print(f"加载音效 {sound_name} 失败: {e}")
    
    def play_sound(self, sound_name, volume=0.7):
        """播放指定音效"""
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
    
    def load_background_music(self, music_path):
        """加载背景音乐"""
        if os.path.exists(music_path):
            self.background_music = music_path
        else:
            print(f"警告: 背景音乐文件 {music_path} 未找到")
    
    def play_background_music(self, loop=True):
        """播放背景音乐"""
        if self.background_music and not self.music_playing:
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1 if loop else 0)
                self.music_playing = True
            except pygame.error as e:
                print(f"播放背景音乐失败: {e}")
    
    def stop_background_music(self):
        """停止背景音乐"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def set_music_volume(self, volume):
        """设置背景音乐音量"""
        pygame.mixer.music.set_volume(volume)
    
    def set_sound_volume(self, volume):
        """设置所有音效音量"""
        for sound in self.sounds.values():
            sound.set_volume(volume)