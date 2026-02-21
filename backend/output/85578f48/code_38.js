// 游戏主循环
class GameLoop {
    constructor() {
        this.lastTime = 0;
        this.fps = 60;
        this.frameInterval = 1000 / this.fps;
        this.lastFpsUpdate = 0;
        this.frames = 0;
        this.currentFps = 0;
    }
    
    start(callback) {
        const loop = (timestamp) => {
            requestAnimationFrame(loop);
            
            const deltaTime = timestamp - this.lastTime;
            
            if (deltaTime >= this.frameInterval) {
                this.lastTime = timestamp - (deltaTime % this.frameInterval);
                
                // 计算FPS
                this.frames++;
                if (timestamp - this.lastFpsUpdate >= 1000) {
                    this.currentFps = Math.round((this.frames * 1000) / (timestamp - this.lastFpsUpdate));
                    this.frames = 0;
                    this.lastFpsUpdate = timestamp;
                }
                
                // 更新游戏状态
                callback(deltaTime);
            }
        };
        
        requestAnimationFrame(loop);
    }
}