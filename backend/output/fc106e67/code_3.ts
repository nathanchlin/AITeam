class Ninja {
    private x: number;
    private y: number;
    private velocityY: number;
    private isJumping: boolean;
    private color: string;
    
    constructor() {
        this.x = 100;
        this.y = 300;
        this.velocityY = 0;
        this.isJumping = false;
        this.color = '#00FF00'; // 绿色忍者
    }
    
    public reset(): void {
        this.x = 100;
        this.y = 300;
        this.velocityY = 0;
        this.isJumping = false;
    }
    
    public update(): void {
        // 更新忍者位置
        this.y += this.velocityY;
        
        // 重力效果
        if (this.y < 300) {
            this.velocityY += 0.5; // 重力加速度
        } else {
            this.y = 300;
            this.velocityY = 0;
            this.isJumping = false;
        }
    }
    
    public jump(): void {
        if (!this.isJumping) {
            this.velocityY = -12; // 跳跃初速度
            this.isJumping = true;
        }
    }
    
    public render(): void {
        // 渲染忍者角色
        // 这里使用伪代码表示渲染逻辑
        console.log(`Rendering ninja at (${this.x}, ${this.y}) with color ${this.color}`);
    }
    
    public getPosition(): { x: number, y: number } {
        return { x: this.x, y: this.y };
    }
}