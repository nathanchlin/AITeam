def play_sound(sounds, sound_name):
    """播放指定音效"""
    if sounds and sound_name in sounds:
        sounds[sound_name].play()