/**
 * 玩家飞机类
 */
class Player {
    constructor(x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.speed = 5;
        this.health = 100;
        this.bullets = [];
        this.lastShotTime = 0;
        this.shotCooldown = 200; // 毫秒
        this.invulnerable = false;
        this.invulnerableTime = 0;
    }
    
    update(keys, currentTime) {
        // 移动控制
        if (keys.ArrowUp && this.y > 0) {
            this.y -= this.speed;
        }
        if (keys.ArrowDown && this.y < canvas.height - this.height) {
            this.y += this.speed;
        }
        if (keys.ArrowLeft && this.x > 0) {
            this.x -= this.speed;
        }
        if (keys.ArrowRight && this.x < canvas.width - this.width) {
            this.x += this.speed;
        }
        
        // 射击控制
        if (keys[' '] && currentTime - this.lastShotTime > this.shotCooldown) {
            this.shoot(currentTime);
            this.lastShotTime = currentTime;
        }
        
        // 更新子弹
        this.bullets = this.bullets.filter(bullet => {
            bullet.update();
            return bullet.y > -bullet.height;
        });
        
        // 更新无敌时间
        if (this.invulnerable && currentTime - this.invulnerableTime > 2000) {
            this.invulnerable = false;
        }
    }
    
    shoot(currentTime) {
        const bullet = new Bullet(
            this.x + this.width / 2 - 2,
            this.y,
            4,
            10,
            -10,
            'player'
        );
        this.bullets.push(bullet);
    }
    
    takeDamage(amount) {
        if (!this.invulnerable) {
            this.health -= amount;
            this.invulnerable = true;
            this.invulnerableTime = Date.now();
            return true;
        }
        return false;
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
        // 绘制玩家飞机
        ctx.fillStyle = this.invulnerable && Math.floor(Date.now() / 100) % 2 ? 'rgba(0, 255, 0, 0.5)' : '#00ff00';
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 绘制子弹
        this.bullets.forEach(bullet => bullet.draw(ctx));
    }
}