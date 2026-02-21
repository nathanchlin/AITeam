// 对象池实现
class ObjectPool {
  constructor(createFn, resetFn, initialSize = 100) {
    this.createFn = createFn;
    this.resetFn = resetFn;
    this.pool = [];
    this.active = [];
    
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.createFn());
    }
  }
  
  acquire() {
    let obj;
    if (this.pool.length > 0) {
      obj = this.pool.pop();
    } else {
      obj = this.createFn();
    }
    this.active.push(obj);
    return obj;
  }
  
  release(obj) {
    const index = this.active.indexOf(obj);
    if (index !== -1) {
      this.active.splice(index, 1);
      this.resetFn(obj);
      this.pool.push(obj);
    }
  }
  
  update() {
    // 更新所有活动对象
    for (let i = this.active.length - 1; i >= 0; i--) {
      if (this.active[i].isDead) {
        this.release(this.active[i]);
      }
    }
  }
}

// 使用对象池管理子弹
const bulletPool = new ObjectPool(
  () => new Bullet(),
  (bullet) => {
    bullet.reset();
  },
  200
);

// 发射子弹时
function fireBullet() {
  const bullet = bulletPool.acquire();
  bullet.init(player.x, player.y);
  bullets.push(bullet);
}