// 移动逻辑
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

// 方向变更逻辑
changeDirection(newDirection) {
    // 防止蛇直接掉头
    if (this.direction.x === -newDirection.x && this.direction.y === -newDirection.y) {
        return;
    }
    nextDirection = newDirection;
}