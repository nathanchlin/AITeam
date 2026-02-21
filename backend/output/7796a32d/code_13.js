// 平台类
class Platform {
    constructor(x, y, width, height, type = 'normal') {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.type = type;
        this.color = this.getColorByType();
        this.passed = false;
    }
    
    getColorByType() {
        switch (this.type) {
            case 'normal':
                return '#2ecc71';
            case 'moving':
                return '#3498db';
            case 'breakable':
                return '#f39c12';
            case 'danger':
                return '#e74c3c';
            default:
                return '#2ecc71';
        }
    }
    
    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 添加一些细节
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.fillRect(this.x, this.y, this.width, 5);
    }
    
    // 移动平台更新
    update() {
        if (this.type === 'moving') {
            // 这里可以添加移动逻辑
        }
    }
}