class PlatformManager {
  constructor(scene, player) {
    this.scene = scene;
    this.player = player;
    this.platforms = this.physics.add.group();
    this.platformSpeed = 2;
    this.platformGap = 100;
    this.lastPlatformY = 0;
    this.platformTypes = {
      normal: { color: 0x00ff00, bounce: 0 },
      bouncy: { color: 0xff00ff, bounce: 0.5 },
      moving: { color: 0x0000ff, bounce: 0, moveX: true }
    };
  }
  
  generateInitialPlatforms() {
    // 生成初始平台
    for (let i = 0; i < 10; i++) {
      this.createPlatform(300 - i * this.platformGap);
    }
  }
  
  createPlatform(y) {
    const type = Phaser.Math.RND.pick(Object.keys(this.platformTypes));
    const platformData = this.platformTypes[type];
    
    const platform = this.physics.add.staticSprite(
      Phaser.Math.RND.between(50, 350),
      y,
      'platform'
    );
    
    platform.setTint(platformData.color);
    platform.setData('type', type);
    platform.setData('bounce', platformData.bounce);
    
    if (platformData.moveX) {
      platform.setData('moveX', true);
      platform.setData('moveRange', Phaser.Math.RND.between(50, 150));
      platform.setData('moveSpeed', Phaser.Math.RND.between(50, 150));
      platform.setData('originalX', platform.x);
    }
    
    this.platforms.add(platform);
    this.lastPlatformY = y;
  }
  
  update() {
    // 移动所有平台
    this.platforms.children.entries.forEach(platform => {
      if (platform.data.get('moveX')) {
        const moveX = platform.data.get('moveX');
        const originalX = platform.data.get('originalX');
        const moveRange = platform.data.get('moveRange');
        const moveSpeed = platform.data.get('moveSpeed');
        
        platform.x = originalX + Math.sin(this.scene.time.now * moveSpeed / 1000) * moveRange;
      }
    });
    
    // 检查是否需要生成新平台
    if (this.player.y > this.lastPlatformY - this.scene.cameras.main.height) {
      this.generateNewPlatforms();
    }
    
    // 检查是否需要移除旧平台
    this.platforms.children.entries.forEach(platform => {
      if (platform.y > this.player.y + this.scene.cameras.main.height) {
        platform.destroy();
      }
    });
  }
  
  generateNewPlatforms() {
    const platformsToGenerate = 5;
    for (let i = 0; i < platformsToGenerate; i++) {
      this.createPlatform(this.lastPlatformY - this.platformGap);
    }
  }
}