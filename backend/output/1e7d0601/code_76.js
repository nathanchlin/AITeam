// 性能监控工具
class PerformanceMonitor {
  constructor() {
    this.fps = 0;
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.fpsHistory = [];
    this.memoryUsage = {
      used: 0,
      total: 0
    };
  }
  
  update() {
    this.frameCount++;
    const currentTime = performance.now();
    
    if (currentTime >= this.lastTime + 1000) {
      this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
      this.fpsHistory.push(this.fps);
      
      if (this.fpsHistory.length > 60) {
        this.fpsHistory.shift();
      }
      
      this.frameCount = 0;
      this.lastTime = currentTime;
      
      // 更新内存使用情况
      if (performance.memory) {
        this.memoryUsage = {
          used: Math.round(performance.memory.usedJSHeapSize / 1048576),
          total: Math.round(performance.memory.totalJSHeapSize / 1048576)
        };
      }
    }
  }
  
  getAverageFPS() {
    if (this.fpsHistory.length === 0) return 0;
    const sum = this.fpsHistory.reduce((a, b) => a + b, 0);
    return Math.round(sum / this.fpsHistory.length);
  }
  
  render(ctx) {
    ctx.fillStyle = 'white';
    ctx.font = '14px Arial';
    ctx.fillText(`FPS: ${this.fps}`, 10, 20);
    ctx.fillText(`Avg FPS: ${this.getAverageFPS()}`, 10, 40);
    ctx.fillText(`Memory: ${this.memoryUsage.used}MB / ${this.memoryUsage.total}MB`, 10, 60);
  }
}

// 在游戏循环中使用
const perfMonitor = new PerformanceMonitor();

function gameLoop() {
  // 游戏逻辑...
  
  perfMonitor.update();
  perfMonitor.render(ctx);
  
  requestAnimationFrame(gameLoop);
}