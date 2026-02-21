class PerformanceMonitor {
  constructor() {
    this.fps = 0;
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.metrics = {
      drawCalls: 0,
      objects: 0,
      collisions: 0,
      memoryUsage: 0
    };
    this.history = [];
    this.maxHistoryLength = 100;
  }
  
  update() {
    this.frameCount++;
    const now = performance.now();
    const delta = now - this.lastTime;
    
    if (delta >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / delta);
      this.frameCount = 0;
      this.lastTime = now;
      
      // 记录历史数据
      this.history.push({
        fps: this.fps,
        memory: performance.memory ? 
          performance.memory.usedJSHeapSize : 0,
        timestamp: now
      });
      
      if (this.history.length > this.maxHistoryLength) {
        this.history.shift();
      }
    }
  }
  
  getMetrics() {
    return {
      fps: this.fps,
      ...this.metrics,
      memory: performance.memory ? 
        performance.memory.usedJSHeapSize : 0
    };
  }
  
  getPerformanceGraph() {
    return {
      fps: this.history.map(h => h.fps),
      memory: this.history.map(h => h.memory / (1024 * 1024)) // 转换为MB
    };
  }
  
  resetMetrics() {
    this.metrics = {
      drawCalls: 0,
      objects: 0,
      collisions: 0,
      memoryUsage: 0
    };
  }
}