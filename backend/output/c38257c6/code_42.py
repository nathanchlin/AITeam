def init_sounds():
    """初始化游戏音效"""
    try:
        # 使用pygame生成简单音效
        paddle_hit = generate_tone(440, 0.1)  # 440Hz，0.1秒
        brick_hit = generate_tone(880, 0.1)   # 880Hz，0.1秒
        wall_hit = generate_tone(220, 0.1)    # 220Hz，0.1秒
        game_over = generate_tone(110, 0.5)   # 110Hz，0.5秒
        win_sound = generate_tone(660, 0.5)   # 660Hz，0.5秒
        
        return {
            'paddle': paddle_hit,
            'brick': brick_hit,
            'wall': wall_hit,
            'game_over': game_over,
            'win': win_sound
        }
    except:
        # 如果音效加载失败，返回None
        return None

def generate_tone(frequency, duration):
    """生成指定频率和持续时间的音效"""
    sample_rate = 22050
    samples = int(sample_rate * duration)
    waves = np.sin(2 * np.pi * frequency * np.arange(samples) / sample_rate)
    waves = (waves * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(waves)
    return sound