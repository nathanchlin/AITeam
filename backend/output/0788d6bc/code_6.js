class QualityManager {
  constructor() {
    this.currentLevel = 2; // 默认中等质量
    this.levels = {
      low: {
        particleEffects: false,
        shadows: false,
        maxEnemies: 3,
        maxBullets: 10,
        fpsCap: 30
      },
      medium: {
        particleEffects: true,
        shadows: false,
        maxEnemies: 5,
        maxBullets: 20,
        fpsCap: 45
      },
      high: {
        particleEffects: true,
        shadows: true,
        maxEnemies: 8,
        maxBullets: 50,
        fpsCap: 60
      }
    };
    
    // 检测设备性能
    this.detectDevicePerformance();
  }
  
  // 检测设备性能
  detectDevicePerformance() {
    // 简单的设备性能检测
    const isLowEnd = 
      navigator.hardwareConcurrency < 4 || 
      navigator.deviceMemory < 4 ||
      /mobile|android/i.test(navigator.userAgent);
    
    this.currentLevel = isLowEnd ? 'low' : 'medium';
    
    // 允许用户手动调整
    window.addEventListener('resize', () => {
      if (window.innerWidth < 768) {
        this.currentLevel = 'low';
      } else {
        this.currentLevel = 'medium';
      }
    });
  }
  
  // 获取当前质量设置
  getCurrentSettings() {
    return this.levels[this.currentLevel];
  }
  
  // 调整游戏质量
  adjustGameQuality(game) {
    const settings = this.getCurrentSettings();
    
    // 调整敌人数量
    game.maxEnemies = settings.maxEnemies;
    
    // 调整子弹数量
    game.maxBullets = settings.maxBullets;
    
    // 调整特效
    game.enableParticleEffects = settings.particleEffects;
    game.enableShadows = settings.shadows;
    
    // 限制FPS
    game.fpsCap = settings.fpsCap;
  }
}

// 使用质量管理器
const qualityManager = new QualityManager();
qualityManager.adjustGameQuality(game);