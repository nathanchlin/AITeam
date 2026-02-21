// 玩家坦克类中的射击方法
class Player {
  // ... 其他代码 ...
  
  shoot() {
    // 计算子弹发射位置（坦克中心）
    let bulletX = this.x;
    let bulletY = this.y;
    
    // 根据坦克方向调整子弹初始位置
    switch (this.direction) {
      case 'up':
        bulletY -= this.size/2;
        break;
      case 'down':
        bulletY += this.size/2;
        break;
      case 'left':
        bulletX -= this.size/2;
        break;
      case 'right':
        bulletX += this.size/2;
        break;
    }
    
    // 发射子弹
    bulletManager.shoot(bulletX, bulletY, this.direction, true);
  }
}

// 敌人坦克类中的射击方法
class Enemy {
  // ... 其他代码 ...
  
  shoot() {
    // 随机决定是否射击
    if (Math.random() < 0.01) { // 1%的概率每帧射击
      // 计算子弹发射位置（坦克中心）
      let bulletX = this.x;
      let bulletY = this.y;
      
      // 根据坦克方向调整子弹初始位置
      switch (this.direction) {
        case 'up':
          bulletY -= this.size/2;
          break;
        case 'down':
          bulletY += this.size/2;
          break;
        case 'left':
          bulletX -= this.size/2;
          break;
        case 'right':
          bulletX += this.size/2;
          break;
      }
      
      // 发射子弹
      bulletManager.shoot(bulletX, bulletY, this.direction, false);
    }
  }
}