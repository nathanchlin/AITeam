// 实现对象池示例
class GameObjectPool {
    constructor(createFn, resetFn) {
        this.pool = [];
        this.createFn = createFn;
        this.resetFn = resetFn;
        this.activeObjects = new Set();
    }
    
    acquire() {
        let obj;
        if (this.pool.length > 0) {
            obj = this.pool.pop();
        } else {
            obj = this.createFn();
        }
        this.activeObjects.add(obj);
        return obj;
    }
    
    release(obj) {
        this.resetFn(obj);
        this.activeObjects.delete(obj);
        this.pool.push(obj);
    }
    
    updateAll(deltaTime) {
        this.activeObjects.forEach(obj => {
            if (obj.update) obj.update(deltaTime);
        });
    }
    
    renderAll(ctx) {
        this.activeObjects.forEach(obj => {
            if (obj.render) obj.render(ctx);
        });
    }
}