// levelManager.js
class LevelManager {
    constructor() {
        this.levels = [
            {
                id: 1,
                name: "太平洋战区",
                background: "ocean",
                enemyWaves: [
                    { type: "basic", count: 5, spacing: 1000, speed: 1 },
                    { type: "basic", count: 8, spacing: 800, speed: 1.2 },
                    { type: "fast", count: 3, spacing: 1500, speed: 2.5 },
                    { type: "basic", count: 10, spacing: 600, speed: 1.5 }
                ],
                boss: null,
                specialEvents: [
                    { time: 5000, type: "powerUp", description: "获得强化武器" },
                    { time: 15000, type: "enemyFormation", description: "敌机编队攻击" }
                ],
                objectives: {
                    score: 5000,
                    survivalTime: 30000,
                    noDamage: true
                },
                difficulty: 1
            },
            {
                id: 2,
                name: "山地战区",
                background: "mountain",
                enemyWaves: [
                    { type: "basic", count: 6, spacing: 900, speed: 1.3 },
                    { type: "tank", count: 2, spacing: 2000, speed: 0.8 },
                    { type: "fast", count: 5, spacing: 1200, speed: 2.2 },
                    { type: "basic", count: 12, spacing: 700, speed: 1.6 },
                    { type: "zigzag", count: 4, spacing: 1600, speed: 1.8 }
                ],
                boss: {
                    type: "medium",
                    health: 50,
                    speed: 0.7,
                    shootPattern: "spread",
                    score: 2000
                },
                specialEvents: [
                    { time: 8000, type: "powerUp", description: "获得护盾" },
                    { time: 20000, type: "enemyFormation", description: "敌机编队攻击" },
                    { time: 25000, type: "meteorShower", description: "流星雨" }
                ],
                objectives: {
                    score: 10000,
                    survivalTime: 45000,
                    noDamage: false
                },
                difficulty: 1.5
            },
            {
                id: 3,
                name: "城市战区",
                background: "city",
                enemyWaves: [
                    { type: "basic", count: 8, spacing: 800, speed: 1.4 },
                    { type: "tank", count: 3, spacing: 1800, speed: 0.9 },
                    { type: "fast", count: 6, spacing: 1100, speed: 2.4 },
                    { type: "zigzag", count: 5, spacing: 1500, speed: 2 },
                    { type: "basic", count: 15, spacing: 600, speed: 1.7 }
                ],
                boss: {
                    type: "large",
                    health: 100,
                    speed: 0.5,
                    shootPattern: "spiral",
                    score: 5000
                },
                specialEvents: [
                    { time: 10000, type: "powerUp", description: "获得双重武器" },
                    { time: 15000, type: "enemyFormation", description: "敌机编队攻击" },
                    { time: 30000, type: "meteorShower", description: "流星雨" },
                    { time: 35000, type: "enemySwarm", description: "敌机群" }
                ],
                objectives: {
                    score: 20000,
                    survivalTime: 60000,
                    noDamage: false
                },
                difficulty: 2
            }
        ];
        
        this.currentLevel = 0;
        this.levelStartTime = 0;
        this.lastEventTime = 0;
    }
    
    getCurrentLevel() {
        return this.levels[this.currentLevel];
    }
    
    nextLevel() {
        if (this.currentLevel < this.levels.length - 1) {
            this.currentLevel++;
            this.levelStartTime = Date.now();
            this.lastEventTime = 0;
            return true;
        }
        return false;
    }
    
    checkSpecialEvents() {
        const level = this.getCurrentLevel();
        const currentTime = Date.now() - this.levelStartTime;
        
        level.specialEvents.forEach(event => {
            if (currentTime >= event.time && currentTime < event.time + 1000) {
                this.triggerSpecialEvent(event);
            }
        });
    }
    
    triggerSpecialEvent(event) {
        switch (event.type) {
            case "powerUp":
                // 触发强化道具生成
                gameEngine.spawnPowerUp();
                break;
            case "enemyFormation":
                // 触发敌机编队
                gameEngine.spawnEnemyFormation();
                break;
            case "meteorShower":
                // 触发流星雨
                gameEngine.startMeteorShower();
                break;
            case "enemySwarm":
                // 触发敌机群
                gameEngine.spawnEnemySwarm();
                break;
        }
    }
    
    checkLevelComplete() {
        const level = this.getCurrentLevel();
        const currentTime = Date.now() - this.levelStartTime;
        
        // 检查是否达到关卡目标
        if (gameState.score >= level.objectives.score && 
            currentTime >= level.objectives.survivalTime) {
            return true;
        }
        return false;
    }
}

// 全局关卡管理器
const levelManager = new LevelManager();