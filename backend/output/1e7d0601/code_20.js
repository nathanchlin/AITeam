/**
 * 玩家飞机类
 */
class Player {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 40;
        this.height = 50;
        this.speed = 300;
        this.active = true;
        this.bullets = [];
        this.lastShot = 0;
        this.shotCooldown = 0.2; // 射击冷却时间（秒）
        this.lives = 3;
        this.score = 0;
    }
    
    update(deltaTime) {
        // 移动控制
        if (input.isKeyPressed('ArrowLeft') || input.isKeyPressed('a')) {
            this.x -= this.speed * deltaTime;
        }
        if (input.isKeyPressed('ArrowRight') || input.isKeyPressed('d')) {
            this.x += this.speed * deltaTime;
        }
        if (input.isKeyPressed('ArrowUp') || input.isKeyPressed('w')) {
            this.y -= this.speed * deltaTime;
        }
        if (input.isKeyPressed('ArrowDown') || input.isKeyPressed('s')) {
            this.y += this.speed * deltaTime;
        }
        
        // 边界检查
        this.x = Math.max(0, Math.min(gameEngine.width - this.width, this.x));
        this.y = Math.max(0, Math.min(gameEngine.height - this.height, this.y));
        
        // 射击控制
        if (input.isKeyPressed(' ') || input.isKeyPressed('Mouse0')) {
            this.shoot();
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
     * 发射子弹
     */
    shoot() {
        const now = performance.now() / 1000;
        if (now - this.lastShot > this.shotCooldown) {
            const bullet = new Bullet(this.x + this.width / 2, this.y, -500, true);
            gameEngine.addEntity(bullet);
            this.bullets.push(bullet);
            this.lastShot = now;
        }
    }
    
    render(ctx) {
        // 绘制玩家飞机
        ctx.fillStyle = '#0f0';
        ctx.beginPath();
        ctx.moveTo(this.x + this.width / 2, this.y);
        ctx.lineTo(this.x, this.y + this.height);
        ctx.lineTo(this.x + this.width / 2, this.y + this.height - 10);
        ctx.lineTo(this.x + this.width, this.y + this.height);
        ctx.closePath();
        ctx.fill();
        
        // 绘制座舱
        ctx.fillStyle = '#0ff';
        ctx.beginPath();
        ctx.arc(this.x + this.width / 2, this.y + 15, 5, 0, Math.PI * 2);
        ctx.fill();
        
        // 绘制引擎火焰
        ctx.fillStyle = '#f80';
        ctx.beginPath();
        ctx.moveTo(this.x + this.width / 2 - 5, this.y + this.height);
        ctx.lineTo(this.x + this.width / 2, this.y + this.height + 10);
        ctx.lineTo(this.x + this.width / 2 + 5, this.y + this.height);
        ctx.closePath();
        ctx.fill();
    }
    
    takeDamage() {
        this.lives--;
        if (this.lives <= 0) {
            this.active = false;
        }
    }
}