class GemRenderer {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private gemSize: number;
    private padding: number;
    private gemColors: Record<GemType, string>;
    
    constructor(canvas: HTMLCanvasElement, gemSize: number = 50, padding: number = 5) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d')!;
        this.gemSize = gemSize;
        this.padding = padding;
        
        // 定义宝石颜色
        this.gemColors = {
            [GemType.RED]: '#FF5252',
            [GemType.BLUE]: '#448AFF',
            [GemType.GREEN]: '#69F0AE',
            [GemType.YELLOW]: '#FFD740',
            [GemType.PURPLE]: '#E040FB',
            [GemType.ORANGE]: '#FF6E40'
        };
    }
    
    // 渲染单个宝石
    public renderGem(gem: Gem, x: number, y: number): void {
        const centerX = x + this.gemSize / 2;
        const centerY = y + this.gemSize / 2;
        const radius = (this.gemSize / 2 - this.padding) * gem.scale;
        
        // 绘制宝石背景
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        this.ctx.fillStyle = this.gemColors[gem.type];
        this.ctx.fill();
        
        // 添加高光效果
        this.ctx.beginPath();
        this.ctx.arc(centerX - radius/3, centerY - radius/3, radius/3, 0, Math.PI * 2);
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.fill();
        
        // 如果宝石被标记为匹配，添加特效
        if (gem.isMatched) {
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
        }
    }
    
    // 渲染整个网格
    public renderGrid(grid: GameGrid): void {
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制网格背景
        this.ctx.fillStyle = '#2C3E50';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制每个宝石
        for (let row = 0; row < grid.rows; row++) {
            for (let col = 0; col < grid.cols; col++) {
                const gem = grid.gems[row][col];
                if (gem) {
                    const x = col * (this.gemSize + this.padding);
                    const y = row * (this.gemSize + this.padding);
                    this.renderGem(gem, x, y);
                }
            }
        }
    }
    
    // 设置画布大小
    public resizeCanvas(grid: GameGrid): void {
        this.canvas.width = grid.cols * (this.gemSize + this.padding);
        this.canvas.height = grid.rows * (this.gemSize + this.padding);
    }
}