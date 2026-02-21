// 优化前：O(n²)的碰撞检测
function checkCollisions() {
  for (let i = 0; i < bullets.length; i++) {
    for (let j = 0; j < enemies.length; j++) {
      if (isColliding(bullets[i], enemies[j])) {
        handleCollision(bullets[i], enemies[j]);
      }
    }
  }
}

// 优化后：空间分区四叉树
class QuadTree {
  constructor(boundary, capacity) {
    this.boundary = boundary;
    this.capacity = capacity;
    this.objects = [];
    this.divided = false;
  }
  
  insert(object) {
    if (!this.contains(object)) return false;
    
    if (this.objects.length < this.capacity) {
      this.objects.push(object);
      return true;
    } else {
      if (!this.divided) this.subdivide();
      return (this.northeast.insert(object) ||
              this.northwest.insert(object) ||
              this.southeast.insert(object) ||
              this.southwest.insert(object));
    }
  }
  
  query(range, found = []) {
    if (!this.intersects(range)) return found;
    
    for (let obj of this.objects) {
      if (isColliding(obj, range)) {
        found.push(obj);
      }
    }
    
    if (this.divided) {
      this.northeast.query(range, found);
      this.northwest.query(range, found);
      this.southeast.query(range, found);
      this.southwest.query(range, found);
    }
    
    return found;
  }
}

// 使用四叉树进行碰撞检测
function checkCollisionsOptimized() {
  const bulletTree = new QuadTree(canvasBoundary, 10);
  const enemyTree = new QuadTree(canvasBoundary, 10);
  
  // 构建四叉树
  bullets.forEach(bullet => bulletTree.insert(bullet));
  enemies.forEach(enemy => enemyTree.insert(enemy));
  
  // 查询碰撞
  bullets.forEach(bullet => {
    const nearbyEnemies = enemyTree.query(bullet);
    nearbyEnemies.forEach(enemy => {
      if (isColliding(bullet, enemy)) {
        handleCollision(bullet, enemy);
      }
    });
  });
}