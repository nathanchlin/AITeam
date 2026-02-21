# 在游戏特定事件中播放音效
def handle_ninja_action(self):
    if self.ninja.is_jumping:
        self.sound_system.play_sound(SoundType.JUMP)
    elif self.ninja.is_attacking:
        self.sound_system.play_sound(SoundType.SLASH)

def handle_collision(self, collision_type):
    if collision_type == "collect":
        self.sound_system.play_sound(SoundType.COLLECT)
    elif collision_type == "damage":
        self.sound_system.play_sound(SoundType.DAMAGE)
    elif collision_type == "game_over":
        self.sound_system.stop_background_music()
        self.sound_system.play_sound(SoundType.GAME_OVER)