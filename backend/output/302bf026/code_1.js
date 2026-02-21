class Tank {
  constructor(x, y, isPlayer = false) {
    this.x = x;
    this.y = y;
    this.isPlayer = isPlayer;
    this.health = 100;
    this.speed = 2;
    this.direction = 0; // 0: 上, 1: 右, 2: 下, 3: 左
    this.bullets = [];
    this.lastShotTime = 0;
    this.shotCooldown = 500; // 毫秒
  }
  
  move(direction) {
    // 根据方向移动坦克
  }
  
  shoot() {
    // 创建子弹并添加到游戏世界
  }
  
  takeDamage(amount) {
    // 减少生命值
  }
  
  destroy() {
    // 坦克被摧毁的逻辑
  }
}