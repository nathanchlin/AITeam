class Match3Game {
    private gridSystem: GameGridSystem;
    private inputHandler: GameInputHandler;
    
    constructor(canvasId: string, rows: number = 8, cols: number = 8) {
        const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!canvas) {
            throw new Error(`Canvas with id "${canvasId}" not found`);
        }
        
        const renderer = new GemRenderer(canvas);
        this.gridSystem = new GameGridSystem(rows, cols, renderer);
        this.inputHandler = new GameInputHandler(this.gridSystem);
    }
    
    // 开始游戏
    public start(): void {
        this.gridSystem.render();
    }
    
    // 获取网格系统（用于扩展功能）
    public getGridSystem(): GameGridSystem {
        return this.gridSystem;
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    const game = new Match3Game('gameCanvas', 8, 8);
    game.start();
});