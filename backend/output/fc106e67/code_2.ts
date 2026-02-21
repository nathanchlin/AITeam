class GameHandler {
    private stateManager: GameStateManager;
    private ninja: Ninja; // 假设这是我们的忍者角色类
    private gameWorld: GameWorld; // 假设这是游戏世界类
    private score: number;
    private highScore: number;
    
    constructor() {
        this.stateManager = new GameStateManager();
        this.ninja = new Ninja();
        this.gameWorld = new GameWorld();
        this.score = 0;
        this.highScore = 0;
        
        // 注册状态变化处理
        this.registerStateHandlers();
    }
    
    private registerStateHandlers(): void {
        // 游戏开始前
        this.stateManager.onStateChange(GameState.STARTING, () => {
            this.onStarting();
        });
        
        // 游戏进行中
        this.stateManager.onStateChange(GameState.PLAYING, () => {
            this.onPlaying();
        });
        
        // 游戏暂停
        this.stateManager.onStateChange(GameState.PAUSED, () => {
            this.onPaused();
        });
        
        // 游戏结束
        this.stateManager.onStateChange(GameState.GAME_OVER, () => {
            this.onGameOver();
        });
        
        // 游戏重新开始
        this.stateManager.onStateChange(GameState.RESTARTING, () => {
            this.onRestarting();
        });
    }
    
    private onStarting(): void {
        console.log("游戏开始前初始化...");
        this.ninja.reset();
        this.gameWorld.generateLevel();
        this.score = 0;
    }
    
    private onPlaying(): void {
        console.log("游戏开始进行...");
        // 开始游戏循环
        this.startGameLoop();
    }
    
    private onPaused(): void {
        console.log("游戏暂停...");
        // 暂停游戏循环
        this.pauseGameLoop();
    }
    
    private onGameOver(): void {
        console.log("游戏结束!");
        if (this.score > this.highScore) {
            this.highScore = this.score;
        }
        this.stopGameLoop();
    }
    
    private onRestarting(): void {
        console.log("重新开始游戏...");
        this.stateManager.changeState(GameState.STARTING);
    }
    
    // 游戏主循环
    private gameLoopId: number | null = null;
    private startGameLoop(): void {
        const gameLoop = () => {
            if (this.stateManager.isState(GameState.PLAYING)) {
                this.update();
                this.render();
                this.gameLoopId = requestAnimationFrame(gameLoop);
            }
        };
        gameLoop();
    }
    
    private pauseGameLoop(): void {
        if (this.gameLoopId !== null) {
            cancelAnimationFrame(this.gameLoopId);
            this.gameLoopId = null;
        }
    }
    
    private stopGameLoop(): void {
        this.pauseGameLoop();
    }
    
    private update(): void {
        // 更新游戏逻辑
        this.ninja.update();
        this.gameWorld.update();
        this.checkCollisions();
        this.updateScore();
    }
    
    private render(): void {
        // 渲染游戏画面
        this.gameWorld.render();
        this.ninja.render();
        this.renderUI();
    }
    
    private checkCollisions(): void {
        // 检查碰撞
        if (this.gameWorld.checkCollisionWithObstacles(this.ninja)) {
            this.stateManager.changeState(GameState.GAME_OVER);
        }
    }
    
    private updateScore(): void {
        // 更新分数
        this.score += 1;
    }
    
    private renderUI(): void {
        // 渲染UI元素
        // 分数、生命值等
    }
    
    // 公共方法，供外部调用改变状态
    public startGame(): void {
        this.stateManager.changeState(GameState.STARTING);
    }
    
    public pauseGame(): void {
        if (this.stateManager.isState(GameState.PLAYING)) {
            this.stateManager.changeState(GameState.PAUSED);
        }
    }
    
    public resumeGame(): void {
        if (this.stateManager.isState(GameState.PAUSED)) {
            this.stateManager.changeState(GameState.PLAYING);
        }
    }
    
    public gameOver(): void {
        this.stateManager.changeState(GameState.GAME_OVER);
    }
    
    public restartGame(): void {
        this.stateManager.changeState(GameState.RESTARTING);
    }
}