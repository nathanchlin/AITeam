// 通用内存池
class MemoryPool {
  constructor(createFn, resetFn, initialSize = 100) {
    this.createFn = createFn;
    this.resetFn = resetFn;
    this.pool = [];
    this.active = new Set();
    
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.createFn());
    }
  }
  
  acquire() {
    let obj = this.pool.pop() || this.createFn();
    this.active.add(obj);
    return obj;
  }
  
  release(obj) {
    if (this.active.has(obj)) {
      this.active.delete(obj);
      this.resetFn(obj);
      this.pool.push(obj);
    }
  }
  
  cleanup() {
    // 主动清理未使用的对象
    while (this.pool.length > this.initialSize * 1.5) {
      this.pool.pop();
    }
  }
  
  getMemoryUsage() {
    return {
      active: this.active.size,
      pooled: this.pool.length,
      total: this.active.size + this.pool.length
    };
  }
}