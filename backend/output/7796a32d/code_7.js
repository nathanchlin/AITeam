class PhysicsSystem {
  constructor(scene) {
    this.scene = scene;
    this.setupPhysics();
  }
  
  setupPhysics() {
    // 配置物理引擎
    this.scene.physics.world.gravity.y = 1500;
    
    // 玩家与平台碰撞
    this.scene.physics.add.collider(
      this.scene.player,
      this.scene.platformManager.platforms,
      this.handlePlayerPlatformCollision,
      null,
      this.scene
    );
  }
  
  handlePlayerPlatformCollision(player, platform) {
    const platformType = platform.data.get('type');
    const bounce = platform.data.get('bounce');
    
    if (bounce > 0) {
      player.setVelocityY(player.body.velocity.y * -bounce);
    }
    
    // 特殊平台处理逻辑
    if (platformType === 'moving') {
      // 移动平台附加逻辑
    }
  }
}