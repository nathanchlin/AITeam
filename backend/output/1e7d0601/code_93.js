/**
 * 敌机类
 */
class Enemy {
    constructor(x, y, width, height, type = 'basic') {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.type = type;
        this.speed = type === 'basic' ? 2 : 3;
        this.health = type === 'basic' ? 20 : 50;
        this.shootCooldown = type === 'basic' ? 1500 : 1000;
        this.lastShotTime = 0;
        this.bullets = [];
        this.movementPattern = type === 'basic' ? 'straight' : 'zigzag';
        this.movementTimer = 0;
        this.zigzagDirection = 1;
    }
    
    update(currentTime) {
        // 移动控制
        if (this.movementPattern === 'straight') {
            this.y += this.speed;
        } else if (this.movementPattern === 'zigzag') {
            this.y += this.speed;
            this.x += Math.sin(this.movementTimer * 0.05) * 2 * this.zigzagDirection;
            this.movementTimer++;
        }
        
        // 射击控制
        if (currentTime - this.lastShotTime > this.shootCooldown) {
            this.shoot(currentTime);
            this.lastShotTime = currentTime;
        }
        
        // 更新子弹
        this.bullets = this.bullets.filter(bullet => {
            bullet.update();
            return bullet.y < canvas.height + bullet.height;
        });
    }
    
    shoot(currentTime) {
        const bullet = new Bullet(
            this.x + this.width / 2 - 2,
            this.y + this.height,
            4,
            10,
            5,
            'enemy'
        );
        this.bullets.push(bullet);
    }
    
    takeDamage(amount) {
        this.health -= amount;
        return this.health <= 0;
    }
    
    getHitbox() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }
    
    draw(ctx) {
        // 绘制敌机
        ctx.fillStyle = this.type === 'basic' ? '#ff0000' : '#ff00ff';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 绘制子弹
        this.bullets.forEach(bullet => bullet.draw(ctx));
    }
}