/**
 * 子弹类
 */
class Bullet {
    constructor(x, y, speed, isPlayerBullet) {
        this.x = x;
        this.y = y;
        this.width = 4;
        this.height = 10;
        this.speed = speed;
        this.active = true;
        this.isPlayerBullet = isPlayerBullet;
    }
    
    update(deltaTime) {
        // 移动子弹
        this.y += this.speed * deltaTime;
        
        // 如果子弹移出屏幕，标记为非活动
        if (this.y < -this.height || this.y > gameEngine.height) {
            this.active = false;
        }
    }
    
    render(ctx) {
        ctx.fillStyle = this.isPlayerBullet ? '#0ff' : '#f0f';
        ctx.fillRect(this.x - this.width / 2, this.y, this.width, this.height);
    }
    
    /**
     * 检测碰撞
     */
    checkCollision(target) {
        return this.x < target.x + target.width &&
               this.x + this.width > target.x &&
               this.y < target.y + target.height &&
               this.y + this.height > target.y;
    }
}