import pygame
import os
from enum import Enum

class SoundType(Enum):
    BACKGROUND_MUSIC = "background_music"
    JUMP = "jump"
    SLASH = "slash"
    COLLECT = "collect"
    DAMAGE = "damage"
    GAME_OVER = "game_over"

class SoundSystem:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.current_music = None
        self.load_sounds()
    
    def load_sounds(self):
        """加载所有音效文件"""
        sound_files = {
            SoundType.JUMP: "sounds/jump.wav",
            SoundType.SLASH: "sounds/slash.wav",
            SoundType.COLLECT: "sounds/collect.wav",
            SoundType.DAMAGE: "sounds/damage.wav",
            SoundType.GAME_OVER: "sounds/game_over.wav",
        }
        
        for sound_type, file_path in sound_files.items():
            try:
                self.sounds[sound_type] = pygame.mixer.Sound(file_path)
                self.sounds[sound_type].set_volume(self.sound_volume)
            except pygame.error:
                print(f"无法加载音效文件: {file_path}")
    
    def play_sound(self, sound_type):
        """播放指定音效"""
        if sound_type in self.sounds:
            self.sounds[sound_type].play()
    
    def play_background_music(self, file_path):
        """播放背景音乐"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1 表示循环播放
            self.current_music = file_path
        except pygame.error:
            print(f"无法加载背景音乐文件: {file_path}")
    
    def stop_background_music(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def set_music_volume(self, volume):
        """设置背景音乐音量"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        """设置音效音量"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def pause_music(self):
        """暂停背景音乐"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """恢复背景音乐"""
        pygame.mixer.music.unpause()