# 在游戏初始化时
sound_manager = SoundManager()
sound_manager.load_background_music('sounds/background.mp3')
sound_manager.play_background_music()

# 在游戏事件处理中
def handle_jump():
    # 跳跃逻辑
    bird.jump()
    sound_manager.play_sound('jump')

def handle_collision():
    # 碰撞逻辑
    sound_manager.play_sound('collision')
    game_over()

def handle_score():
    # 得分逻辑
    score += 1
    sound_manager.play_sound('score')