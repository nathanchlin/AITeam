// 玩家控制核心逻辑
class PlayerController {
    constructor(playerId) {
        this.playerId = playerId;
        this.position = { x: 0, y: 0 };
        this.velocity = { x: 0, y: 0 };
        this.size = 20;
        this.color = this.getRandomColor();
        this.targetPosition = { x: 0, y: 0 };
        this.speed = this.calculateSpeed();
    }
    
    // 设置目标位置
    setTargetPosition(x, y) {
        this.targetPosition = { x, y };
    }
    
    // 更新玩家位置
    update(deltaTime) {
        // 计算方向向量
        const dx = this.targetPosition.x - this.position.x;
        const dy = this.targetPosition.y - this.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // 如果距离大于阈值，则移动
        if (distance > 1) {
            // 归一化方向向量
            const nx = dx / distance;
            const ny = dy / distance;
            
            // 更新速度
            this.velocity.x = nx * this.speed;
            this.velocity.y = ny * this.speed;
            
            // 更新位置
            this.position.x += this.velocity.x * deltaTime;
            this.position.y += this.velocity.y * deltaTime;
        } else {
            // 到达目标，速度归零
            this.velocity.x = 0;
            this.velocity.y = 0;
        }
        
        // 边界检查
        this.checkBoundaries();
    }
    
    // 计算速度（大小与速度成反比）
    calculateSpeed() {
        const baseSpeed = 5;
        const sizeFactor = 100 / (this.size + 10);
        return baseSpeed * sizeFactor;
    }
    
    // 分裂
    split() {
        if (this.size > 20) {
            const newSize = this.size / 2;
            const newPlayer = {
                id: generateId(),
                position: { ...this.position },
                velocity: { 
                    x: this.velocity.x * 2, 
                    y: this.velocity.y * 2 
                },
                size: newSize,
                color: this.color
            };
            
            this.size = newSize;
            this.speed = this.calculateSpeed();
            
            return newPlayer;
        }
        return null;
    }
    
    // 吃球
    eatBall(ball) {
        // 计算新大小
        const mass = Math.PI * this.size * this.size;
        const ballMass = Math.PI * ball.size * ball.size;
        const newMass = mass + ballMass * 0.8; // 80%的转化率
        this.size = Math.sqrt(newMass / Math.PI);
        
        // 更新速度
        this.speed = this.calculateSpeed();
        
        // 返回得分
        return Math.floor(ball.size);
    }
}