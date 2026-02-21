class Snake {
    constructor() {
        this.body = [{x: 10, y: 10}];
        this.direction = {x: 1, y: 0};
        this.nextDirection = {x: 1, y: 0};
    }
    
    // 获取蛇身
    getBody() {
        return this.body;
    }
    
    // 获取蛇头
    getHead() {
        return this.body[0];
    }
    
    // 设置移动方向
    setDirection(newDirection) {
        // 防止蛇直接掉头
        if (this.direction.x !== -newDirection.x || this.direction.y !== -newDirection.y) {
            this.nextDirection = newDirection;
        }
    }
    
    // 移动蛇
    move() {
        // 更新方向
        this.direction = {...this.nextDirection};
        
        // 计算新头部位置
        const head = this.getHead();
        const newHead = {
            x: head.x + this.direction.x,
            y: head.y + this.direction.y
        };
        
        // 添加新头部
        this.body.unshift(newHead);
        
        // 如果没有吃到食物，移除尾部
        if (!this.eat(food)) {
            this.body.pop();
        }
    }
    
    // 增长蛇身（吃到食物时调用）
    grow() {
        // 不移除尾部，使蛇变长
        const head = this.getHead();
        const newHead = {
            x: head.x + this.direction.x,
            y: head.y + this.direction.y
        };
        this.body.unshift(newHead);
    }
    
    // 检查是否吃到食物
    eat(food) {
        const head = this.getHead();
        return head.x === food.x && head.y === food.y;
    }
    
    // 检查碰撞
    checkCollision() {
        const head = this.getHead();
        
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
    
    // 绘制蛇
    draw() {
        this.body.forEach((segment, index) => {
            ctx.fillStyle = index === 0 ? '#2ecc71' : '#27ae60'; // 头部颜色稍浅
            ctx.fillRect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
            
            // 添加边框使蛇身更清晰
            ctx.strokeStyle = '#1e8449';
            ctx.strokeRect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        });
    }
}