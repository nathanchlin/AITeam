// 实现四叉树用于2D碰撞检测
class QuadTree {
  constructor(boundary, capacity = 4) {
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
    }
    
    if (!this.divided) {
      this.subdivide();
    }
    
    return (this.northeast.insert(object) ||
            this.northwest.insert(object) ||
            this.southeast.insert(object) ||
            this.southwest.insert(object));
  }
  
  query(range, found = []) {
    if (!this.intersects(range)) return found;
    
    for (let obj of this.objects) {
      if (this.intersectsPoint(range, obj)) {
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