class Snake {
    constructor() {
        this.reset();
    }
    
    reset() {
        // 初始蛇身在中间，长度为3
        const middle = Math.floor(GRID_SIZE / 2);
        this.body = [
            {x: middle, y: middle},
            {x: middle - 1, y: middle},
            {x: middle - 2, y: middle}
        ];
        this.direction = 'right';
        this.grow = false;
    }
    
    move() {
        // 更新方向
        this.direction = nextDirection;
        
        // 计算新头部位置
        const head = {...this.body[0]};
        
        switch (this.direction) {
            case 'up':
                head.y -= 1;
                break;
            case 'down':
                head.y += 1;
                break;
            case 'left':
                head.x -= 1;
                break;
            case 'right':
                head.x += 1;
                break;
        }
        
        // 检查是否撞墙
        if (head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE) {
            return false;
        }
        
        // 检查是否撞到自己
        for (let segment of this.body) {
            if (head.x === segment.x && head.y === segment.y) {
                return false;
            }
        }
        
        // 添加新头部
        this.body.unshift(head);
        
        // 如果没有吃到食物，移除尾部
        if (!this.grow) {
            this.body.pop();
        } else {
            this.grow = false;
        }
        
        return true;
    }
    
    growSnake() {
        this.grow = true;
    }
    
    render() {
        // 清除所有蛇的样式
        document.querySelectorAll('.snake, .snake-head').forEach(cell => {
            cell.classList.remove('snake', 'snake-head');
        });
        
        // 渲染蛇身
        this.body.forEach((segment, index) => {
            if (index === 0) {
                gameBoard[segment.y][segment.x].classList.add('snake-head');
            } else {
                gameBoard[segment.y][segment.x].classList.add('snake');
            }
        });
    }
}