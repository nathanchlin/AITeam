// 优化后的碰撞检测系统
class CollisionSystem {
  constructor() {
    this.spatialHash = new Map();
    this.cellSize = 100; // 根据游戏世界大小调整
  }
  
  update(objects) {
    // 清空空间哈希
    this.spatialHash.clear();
    
    // 将对象分配到哈希单元格
    for (let obj of objects) {
      const cellX = Math.floor(obj.position.x / this.cellSize);
      const cellY = Math.floor(obj.position.y / this.cellSize);
      const key = `${cellX},${cellY}`;
      
      if (!this.spatialHash.has(key)) {
        this.spatialHash.set(key, []);
      }
      this.spatialHash.get(key).push(obj);
    }
  }
  
  checkCollisions() {
    const collisions = [];
    
    for (let [key, objects] of this.spatialHash) {
      // 检查同一单元格内的碰撞
      for (let i = 0; i < objects.length; i++) {
        for (let j = i + 1; j < objects.length; j++) {
          if (this.checkCollision(objects[i], objects[j])) {
            collisions.push([objects[i], objects[j]]);
          }
        }
      }
      
      // 检查相邻单元格的碰撞
      const [cellX, cellY] = key.split(',').map(Number);
      const neighbors = [
        [cellX + 1, cellY],
        [cellX - 1, cellY],
        [cellX, cellY + 1],
        [cellX, cellY - 1]
      ];
      
      for (let [nX, nY] of neighbors) {
        const neighborKey = `${nX},${nY}`;
        if (this.spatialHash.has(neighborKey)) {
          const neighborObjects = this.spatialHash.get(neighborKey);
          for (let obj1 of objects) {
            for (let obj2 of neighborObjects) {
              if (this.checkCollision(obj1, obj2)) {
                collisions.push([obj1, obj2]);
              }
            }
          }
        }
      }
    }
    
    return collisions;
  }
  
  checkCollision(obj1, obj2) {
    const dx = obj1.position.x - obj2.position.x;
    const dy = obj1.position.y - obj2.position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    return distance < (obj1.radius + obj2.radius);
  }
}