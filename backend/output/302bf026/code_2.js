class Bullet {
  constructor(x, y, direction, owner) {
    this.x = x;
    this.y = y;
    this.direction = direction;
    this.owner = owner; // 射击者
    this.speed = 5;
    this.damage = 20;
  }
  
  update() {
    // 根据方向移动子弹
  }
  
  checkCollision() {
    // 检测与坦克、障碍物的碰撞
  }
}