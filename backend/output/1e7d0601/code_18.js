/**
 * 游戏引擎核心模块
 * 提供Canvas渲染、游戏循环和基础功能
 */
class GameEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = 800;
        this.height = 600;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        
        // 游戏状态
        this.isRunning = false;
        this.lastTime = 0;
        this.deltaTime = 0;
        
        // 游戏对象集合
        this.entities = [];
        this.tags = {};
        
        // 背景滚动相关
        this.backgroundY = 0;
        this.backgroundSpeed = 2;
    }
    
    /**
     * 初始化游戏引擎
     */
    init() {
        console.log("游戏引擎初始化中...");
        this.isRunning = true;
        this.lastTime = performance.now();
        this.gameLoop();
    }
    
    /**
     * 游戏主循环
     */
    gameLoop() {
        if (!this.isRunning) return;
        
        // 计算时间差
        const currentTime = performance.now();
        this.deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        // 更新背景
        this.updateBackground();
        
        // 更新所有实体
        this.updateEntities();
        
        // 渲染所有实体
        this.renderEntities();
        
        // 继续循环
        requestAnimationFrame(() => this.gameLoop());
    }
    
    /**
     * 更新背景滚动
     */
    updateBackground() {
        this.backgroundY += this.backgroundSpeed;
        if (this.backgroundY >= this.height) {
            this.backgroundY = 0;
        }
        
        // 绘制简单背景
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.height);
        gradient.addColorStop(0, "#001a33");
        gradient.addColorStop(1, "#003366");
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // 绘制云朵效果
        this.ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
        for (let i = 0; i < 5; i++) {
            const y = (i * 150 + this.backgroundY) % this.height;
            this.ctx.beginPath();
            this.ctx.arc(100, y, 30, 0, Math.PI * 2);
            this.ctx.arc(130, y, 40, 0, Math.PI * 2);
            this.ctx.arc(160, y, 30, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    /**
     * 更新所有实体
     */
    updateEntities() {
        for (let i = this.entities.length - 1; i >= 0; i--) {
            const entity = this.entities[i];
            if (entity.active) {
                entity.update(this.deltaTime);
            } else {
                this.entities.splice(i, 1);
            }
        }
    }
    
    /**
     * 渲染所有实体
     */
    renderEntities() {
        for (const entity of this.entities) {
            if (entity.active) {
                entity.render(this.ctx);
            }
        }
    }
    
    /**
     * 添加实体到游戏
     */
    addEntity(entity) {
        this.entities.push(entity);
        return entity;
    }
    
    /**
     * 通过标签获取实体
     */
    getEntitiesByTag(tag) {
        if (!this.tags[tag]) {
            this.tags[tag] = [];
        }
        return this.tags[tag];
    }
    
    /**
     * 按标签添加实体
     */
    addEntityWithTag(entity, tag) {
        this.addEntity(entity);
        if (!this.tags[tag]) {
            this.tags[tag] = [];
        }
        this.tags[tag].push(entity);
        return entity;
    }
    
    /**
     * 停止游戏
     */
    stop() {
        this.isRunning = false;
    }
    
    /**
     * 重新开始游戏
     */
    restart() {
        this.entities = [];
        this.tags = {};
        this.init();
    }
}