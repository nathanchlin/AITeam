// 屏幕震动效果
class ScreenShake {
  constructor(game) {
    this.game = game;
    this.intensity = 0;
    this.duration = 0;
    this.x = 0;
    this.y = 0;
  }
  
  shake(intensity, duration) {
    this.intensity = intensity;
    this.duration = duration;
  }
  
  update() {
    if (this.duration > 0) {
      this.duration--;
      
      // 随机偏移
      this.x = (Math.random() - 0.5) * this.intensity;
      this.y = (Math.random() - 0.5) * this.intensity;
      
      // 应用到游戏视图
      this.game.camera.x = this.x;
      this.game.camera.y = this.y;
    } else {
      // 重置位置
      this.game.camera.x = 0;
      this.game.camera.y = 0;
    }
  }
}