class PerformanceMonitor {
  constructor() {
    this.metrics = {
      frameTime: [],
      objectCount: 0,
      memoryUsage: 0,
      drawCalls: 0
    };
    this.maxSamples = 60;
  }
  
  // 更新性能指标
  update(deltaTime, objectCount, drawCalls) {
    this.metrics.frameTime.push(deltaTime);
    if (this.metrics.frameTime.length > this.maxSamples) {
      this.metrics.frameTime.shift();
    }
    
    this.metrics.objectCount = objectCount;
    this.metrics.drawCalls = drawCalls;
    
    // 估算内存使用
    if (performance.memory) {
      this.metrics.memoryUsage = performance.memory.usedJSHeapSize;
    }
  }
  
  // 获取平均帧时间
  getAverageFrameTime() {
    if (this.metrics.frameTime.length === 0) return 0;
    const sum = this.metrics.frameTime.reduce((a, b) => a + b, 0);
    return sum / this.metrics.frameTime.length;
  }
  
  // 获取FPS
  getFPS() {
    const avgFrameTime = this.getAverageFrameTime();
    return avgFrameTime > 0 ? 1000 / avgFrameTime : 0;
  }
  
  // 获取性能报告
  getReport() {
    return {
      fps: this.getFPS(),
      avgFrameTime: this.getAverageFrameTime(),
      objectCount: this.metrics.objectCount,
      drawCalls: this.metrics.drawCalls,
      memoryUsage: this.metrics.memoryUsage
    };
  }
}

// 在游戏循环中使用性能监控
const perfMonitor = new PerformanceMonitor();

function gameLoop(currentTime) {
  // 游戏更新逻辑...
  
  // 更新性能监控
  perfMonitor.update(deltaTime, 
    bulletPool.activeObjects.length + explosionPool.activeObjects.length,
    1 // 简化的绘制调用计数
  );
  
  // 每秒输出一次性能报告
  if (currentTime - lastPerfReport >= 1000) {
    console.log('Performance Report:', perfMonitor.getReport());
    lastPerfReport = currentTime;
  }
  
  requestAnimationFrame(gameLoop);
}