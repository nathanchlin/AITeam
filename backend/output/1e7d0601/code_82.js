// 根据游戏状态调整音效
class DynamicAudioAdjuster {
  constructor(soundManager) {
    this.soundManager = soundManager;
    this.enginePitch = 1.0;
    this.explosionVolume = 1.0;
  }
  
  update(playerSpeed) {
    // 根据玩家速度调整引擎音调
    this.enginePitch = 0.8 + (playerSpeed / planeControls.maxSpeed) * 0.5;
    this.soundManager.sounds.engine.playbackRate = this.enginePitch;
  }
  
  playExplosionSound(distance) {
    // 根据距离调整爆炸音量
    this.explosionVolume = Math.max(0.3, 1 - distance / 500);
    const explosion = this.soundManager.sounds.explosion.cloneNode();
    explosion.volume = this.explosionVolume * this.soundManager.volume;
    explosion.play();
  }
}