/**
 * 子弹类
 */
class Bullet {
    constructor(x, y, width, height, speed, owner) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.speed = speed;
        this.owner = owner; // 'player' 或 'enemy'
    }
    
    update() {
        this.y += this.speed;
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
        ctx.fillStyle = this.owner === 'player' ? '#00ffff' : '#ffff00';
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}