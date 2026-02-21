class FoodGenerator {
    constructor() {
        this.position = {x: 0, y: 0};
    }
    
    generate(snakeBody) {
        // 生成随机位置，直到找到一个不与蛇身重叠的位置
        let newPosition;
        let isOverlapping;
        
        do {
            isOverlapping = false;
            newPosition = {
                x: Math.floor(Math.random() * GRID_SIZE),
                y: Math.floor(Math.random() * GRID_SIZE)
            };
            
            // 检查是否与蛇身重叠
            for (let segment of snakeBody) {
                if (newPosition.x === segment.x && newPosition.y === segment.y) {
                    isOverlapping = true;
                    break;
                }
            }
        } while (isOverlapping);
        
        this.position = newPosition;
        this.render();
    }
    
    render() {
        // 清除旧食物
        document.querySelectorAll('.food').forEach(cell => {
            cell.classList.remove('food');
        });
        
        // 渲染新食物
        gameBoard[this.position.y][this.position.x].classList.add('food');
    }
    
    checkCollision(snakeHead) {
        return snakeHead.x === this.position.x && snakeHead.y === this.position.y;
    }
}