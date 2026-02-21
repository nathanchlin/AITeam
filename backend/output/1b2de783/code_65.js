// 音效管理器
class AudioManager {
  constructor() {
    this.sounds = new Map();
    this.maxConcurrentSounds = 5;
    this.activeSounds = [];
    this.soundPool = new GameObjectPool(
      () => new Audio(),
      (audio) => {
        audio.pause();
        audio.currentTime = 0;
      },
      this.maxConcurrentSounds
    );
  }
  
  loadSound(name, src) {
    const audio = new Audio(src);
    this.sounds.set(name, audio);
  }
  
  playSound(name, volume = 1) {
    if (!this.sounds.has(name)) return;
    
    // 从池中获取或创建音频元素
    const audio = this.soundPool.acquire();
    audio.src = this.sounds.get(name).src;
    audio.volume = volume;
    
    // 处理播放结束事件
    const onEnded = () => {
      this.soundPool.release(audio);
      this.activeSounds = this.activeSounds.filter(a => a !== audio);
      audio.removeEventListener('ended', onEnded);
    };
    
    audio.addEventListener('ended', onEnded);
    this.activeSounds.push(audio);
    
    // 如果超过最大并发数，停止最旧的音效
    if (this.activeSounds.length > this.maxConcurrentSounds) {
      const oldest = this.activeSounds.shift();
      oldest.pause();
      this.soundPool.release(oldest);
    }
    
    audio.play().catch(e => console.error('Audio play error:', e));
  }
}