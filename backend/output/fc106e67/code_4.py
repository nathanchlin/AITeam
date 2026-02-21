# 音效池实现示例
class SoundPool:
    def __init__(self, sound_file, pool_size=3):
        self.sounds = []
        for _ in range(pool_size):
            try:
                sound = pygame.mixer.Sound(sound_file)
                self.sounds.append(sound)
            except pygame.error:
                print(f"无法加载音效文件: {sound_file}")
    
    def play(self):
        for sound in self.sounds:
            if not sound.get_num_channels() or not sound.get_busy():
                sound.play()
                return
        # 如果所有音效都在播放，使用第一个
        self.sounds[0].play()