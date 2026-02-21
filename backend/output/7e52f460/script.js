function generateFood() {
    let foodPosition;
    let foodOnSnake;
    
    // 确保食物不会出现在蛇身上
    do {
        foodPosition = {
            x: Math.floor(Math.random() * (GRID_SIZE)),
            y: Math.floor(Math.random() * (GRID_SIZE))
        };
        
        // 检查食物是否在蛇身上
        foodOnSnake = snake.some(segment => 
            segment.x === foodPosition.x && segment.y === foodPosition.y
        );
    } while (foodOnSnake);
    
    food = foodPosition;
}