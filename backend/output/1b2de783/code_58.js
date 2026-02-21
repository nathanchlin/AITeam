// 实现对象池模式
class GameObjectPool {
  constructor(createFunc, resetFunc, initialSize = 50) {
    this.pool = [];
    this.createFunc = createFunc;
    this.resetFunc = resetFunc;
    
    // 预创建对象
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.createFunc());
    }
  }
  
  acquire() {
    if (this.pool.length > 0) {
      return this.pool.pop();
    }
    return this.createFunc();
  }
  
  release(obj) {
    this.resetFunc(obj);
    this.pool.push(obj);
  }
}

// 使用示例
const bulletPool = new GameObjectPool(
  () => new Bullet(),
  (bullet) => {
    bullet.active = false;
    bullet.visible = false;
  }
);

// 在游戏循环中
function updateBullets() {
  for (let i = bullets.length - 1; i >= 0; i--) {
    if (!bullets[i].active) {
      bulletPool.release(bullets[i]);
      bullets.splice(i, 1);
    }
  }
}