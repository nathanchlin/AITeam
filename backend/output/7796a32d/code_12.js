// 玩家类
class Player {
    constructor(x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.velocityX = 0;
        this.velocityY = 0;
        this.speed = 5;
        this.jumpPower = 15;
        this.gravity = 0.8;
        this.isJumping = false;
        this.lives = 3;
        this.score = 0;
        this.color = '#e74c3c';
    }
    
    update() {
        // 应用重力
        this.velocityY += this.gravity;
        
        // 更新位置
        this.x += this.velocityX;
        this.y += this.velocityY;
        
        // 水平摩擦力
        this.velocityX *= 0.9;
    }
    
    jump() {
        if (!this.isJumping) {
            this.velocityY = -this.jumpPower;
            this.isJumping = true;
        }
    }
    
    moveLeft() {
        this.velocityX = -this.speed;
    }
    
    moveRight() {
        this.velocityX = this.speed;
    }
    
    draw(ctx) {
        // 绘制玩家
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 绘制眼睛
        ctx.fillStyle = 'white';
        ctx.fillRect(this.x + 5, this.y + 5, 5, 5);
        ctx.fillRect(this.x + this.width - 10, this.y + 5, 5, 5);
    }
    
    // 检测是否站在平台上
    onPlatform(platform) {
        return this.y + this.height >= platform.y &&
               this.y + this.height <= platform.y + 10 &&
               this.x + this.width > platform.x &&
               this.x < platform.x + platform.width &&
               this.velocityY >= 0;
    }
}