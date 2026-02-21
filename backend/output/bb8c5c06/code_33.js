class Snake {
    constructor() {
        this.body = [
            {x: 10, y: 10},
            {x: 9, y: 10},
            {x: 8, y: 10}
        ];
        this.direction = {x: 1, y: 0};
    }
    
    getBody() {
        return this.body;
    }
    
    move() {
        // 应用下一个方向
        this.direction = {...nextDirection};
        
        // 计算新的头部位置
        const head = {...this.body[0]};
        head.x += this.direction.x;
        head.y += this.direction.y;
        
        // 将新头部添加到蛇身
        this.body.unshift(head);
        
        // 如果没有吃到食物，移除尾部
        if (!this.eat(food)) {
            this.body.pop();
        }
        
        return head;
    }
    
    eat(foodPosition) {
        const head = this.body[0];
        if (head.x === foodPosition.x && head.y === foodPosition.y) {
            return true;
        }
        return false;
    }
    
    checkCollision() {
        const head = this.body[0];
        
        // 检查是否撞墙
        if (head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE) {
            return true;
        }
        
        // 检查是否撞到自己
        for (let i = 1; i < this.body.length; i++) {
            if (head.x === this.body[i].x && head.y === this.body[i].y) {
                return true;
            }
        }
        
        return false;
    }
    
    changeDirection(newDirection) {
        // 防止蛇直接掉头
        if (this.direction.x === -newDirection.x && this.direction.y === -newDirection.y) {
            return;
        }
        nextDirection = newDirection;
    }
}