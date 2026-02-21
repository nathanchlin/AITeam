function render() {
    // 只清除变化的部分
    const head = snake[0];
    const tail = snake[snake.length - 1];
    
    // 清除蛇尾
    ctx.fillStyle = '#111';
    ctx.fillRect(tail.x * cellSize, tail.y * cellSize, cellSize, cellSize);
    
    // 绘制新蛇头
    ctx.fillStyle = snakeColor;
    ctx.fillRect(head.x * cellSize, head.y * cellSize, cellSize, cellSize);
    
    // 绘制食物
    ctx.fillStyle = foodColor;
    ctx.fillRect(food.x * cellSize, food.y * cellSize, cellSize, cellSize);
    
    // 更新分数显示
    updateScore();
}