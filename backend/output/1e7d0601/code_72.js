// 预计算敌人路径
class PathOptimizer {
  constructor() {
    this.waypoints = [];
    this.pathCache = new Map();
  }
  
  precomputePaths() {
    // 预计算常见路径模式
    const patterns = [
      'straight',
      'sine',
      'zigzag',
      'circle'
    ];
    
    patterns.forEach(pattern => {
      this.pathCache.set(pattern, this.generatePath(pattern));
    });
  }
  
  generatePath(pattern) {
    switch(pattern) {
      case 'straight':
        return (t) => ({ x: t * 5, y: 0 });
      case 'sine':
        return (t) => ({ x: t * 3, y: Math.sin(t * 0.1) * 50 });
      case 'zigzag':
        return (t) => ({ 
          x: t * 4, 
          y: (t % 20 < 10 ? 1 : -1) * 30 
        });
      case 'circle':
        return (t) => ({
          x: Math.cos(t * 0.05) * 50,
          y: Math.sin(t * 0.05) * 50
        });
    }
  }
  
  getPathForEnemy(enemyType) {
    // 根据敌人类型返回预计算路径
    return this.pathCache.get(enemyType.pathPattern);
  }
}