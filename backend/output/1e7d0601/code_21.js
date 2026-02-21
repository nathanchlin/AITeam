/**
 * 敌机类
 */
class Enemy {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 35;
        this.height = 45;
        this.speed = 150;
        this.active = true;
        this.bullets = [];
        this.lastShot = 0;
        this.shotCooldown = 1.5 + Math.random() * 1; // 随机射击冷却
        this.points = 100; // 击中得分
    }
    
    update(deltaTime) {
        // 向下移动
        this.y += this.speed * deltaTime;
        
        // 如果敌机移出屏幕，标记为非活动
        if (this.y > gameEngine.height) {
            this.active = false;
        }
        
        // 随机射击
        const now = performance.now() / 1000;
        if (now - this.lastShot > this.shotCooldown && Math.random() < 0.01) {
            this.shoot();
            this.lastShot = now;
        }
        
        // 更新子弹
        for (let i = this.bullets.length - 1; i >= 0; i--) {
            this.bullets[i].update(deltaTime);
            if (!this.bullets[i].active) {
                this.bullets.splice(i, 1);
            }
        }
    }
    
    /**
     * 敌机射击
     */
    shoot() {
        const bullet = new Bullet(this.x + this.width / 2, this.y + this.height, 300, false);
        gameEngine.addEntity(bullet);
        this.bullets.push(bullet);
    }
    
    render(ctx) {
        // 绘制敌机
        ctx.fillStyle = '#f00';
        ctx.beginPath();
        ctx.moveTo(this.x + this.width / 2, this.y + this.height);
        ctx.lineTo(this.x, this.y);
        ctx.lineTo(this.x + this.width / 2, this.y + 10);
        ctx.lineTo(this.x + this.width, this.y);
        ctx.closePath();
        ctx.fill();
        
        // 绘制敌机细节
        ctx.fillStyle = '#f80';
        ctx.beginPath();
        ctx.arc(this.x + this.width / 2, this.y + 20, 4, 0, Math.PI * 2);
        ctx.fill();
    }
    
    /**
     * 敌机被击中
     */
    hit() {
        this.active = false;
        // 增加玩家分数
        if (gameEngine.tags.player && gameEngine.tags.player.length > 0) {
            gameEngine.tags.player[0].score += this.points;
            updateUI();
        }
    }
}