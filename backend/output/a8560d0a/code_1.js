// 坦克实体
class Tank {
  constructor(x, y, isPlayer) {
    this.x = x;
    this.y = y;
    this.width = 40;
    this.height = 40;
    this.speed = 2;
    this.health = 100;
    this.direction = 'up'; // up, down, left, right
    this.isPlayer = isPlayer;
    this.lastShot = 0;
    this.shotCooldown = 500; // 毫秒
  }
  
  move(direction) {
    // 移动逻辑
  }
  
  shoot() {
    // 射击逻辑
  }
}

// 总部实体
class Headquarters {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.width = 60;
    this.height = 60;
    this.health = 500;
    this.maxHealth = 500;
  }
  
  takeDamage(amount) {
    this.health -= amount;
    if (this.health <= 0) {
      // 游戏结束逻辑
    }
  }
}

// 子弹实体
class Bullet {
  constructor(x, y, direction) {
    this.x = x;
    this.y = y;
    this.width = 10;
    this.height = 10;
    this.speed = 5;
    this.direction = direction;
    this.damage = 20;
  }
  
  update() {
    // 子弹移动逻辑
  }
}