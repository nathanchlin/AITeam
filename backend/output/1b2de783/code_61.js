// 内存监控和清理
class MemoryManager {
  constructor() {
    this.objectCounts = new Map();
    this.lastCleanup = Date.now();
    this.cleanupInterval = 30000; // 30秒清理一次
  }
  
  trackObject(type) {
    if (!this.objectCounts.has(type)) {
      this.objectCounts.set(type, 0);
    }
    this.objectCounts.set(type, this.objectCounts.get(type) + 1);
  }
  
  untrackObject(type) {
    if (this.objectCounts.has(type)) {
      this.objectCounts.set(type, this.objectCounts.get(type) - 1);
    }
  }
  
  cleanup() {
    const now = Date.now();
    if (now - this.lastCleanup > this.cleanupInterval) {
      // 清理未使用的资源
      this.cleanupTextures();
      this.cleanupAudio();
      this.cleanupObjects();
      
      this.lastCleanup = now;
    }
  }
  
  cleanupTextures() {
    // 实现纹理缓存管理
    if (textureCache.size > 100) {
      // 删除最久未使用的纹理
      const keysToDelete = Array.from(textureCache.keys())
        .sort((a, b) => textureCache.get(a).lastUsed - textureCache.get(b).lastUsed)
        .slice(0, 20);
      
      for (let key of keysToDelete) {
        const texture = textureCache.get(key);
        texture.dispose();
        textureCache.delete(key);
      }
    }
  }
  
  getMemoryUsage() {
    return {
      objects: Object.fromEntries(this.objectCounts),
      textures: textureCache.size,
      audio: audioCache.size
    };
  }
}