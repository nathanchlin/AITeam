class QuadTree {
    constructor(boundary, capacity = 4) {
        this.boundary = boundary; // {x, y, width, height}
        this.capacity = capacity;
        this.tanks = [];
        this.bullets = [];
        this.divided = false;
    }
    
    // 插入方法
    insert(object) {
        // 根据对象类型插入到相应的数组
        if (object.type === 'tank') {
            this.tanks.push(object);
        } else if (object.type === 'bullet') {
            this.bullets.push(object);
        }
        
        // 如果超过容量，则分割
        if ((this.tanks.length + this.bullets.length) > this.capacity) {
            this.subdivide();
        }
    }
    
    // 分割方法
    subdivide() {
        // 实现四叉树分割逻辑
    }
    
    // 查询方法
    query(range, found = []) {
        // 实现查询逻辑
        return found;
    }
}