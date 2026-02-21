// 音效管理器
class SoundManager {
  constructor() {
    this.sounds = {
      shoot: this.loadSound('assets/sounds/shoot.wav'),
      explosion: this.loadSound('assets/sounds/explosion.wav'),
      powerup: this.loadSound('assets/sounds/powerup.wav'),
      background: this.loadSound('assets/sounds/background.mp3'),
      engine: this.loadSound('assets/sounds/engine.wav')
    };
    this.muted = false;
    this.volume = 0.7;
  }
  
  loadSound(src) {
    const sound = new Audio(src);
    sound.volume = this.volume;
    return sound;
  }
  
  play(soundName) {
    if (!this.muted && this.sounds[soundName]) {
      // 重置音频时间以实现连续播放
      this.sounds[soundName].currentTime = 0;
      this.sounds[soundName].play();
    }
  }
  
  toggleMute() {
    this.muted = !this.muted;
    Object.values(this.sounds).forEach(sound => {
      sound.muted = this.muted;
    });
  }
  
  setVolume(value) {
    this.volume = value;
    Object.values(this.sounds).forEach(sound => {
      sound.volume = value;
    });
  }
}