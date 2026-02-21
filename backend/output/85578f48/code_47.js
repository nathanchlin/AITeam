// 碰撞检测核心逻辑
class CollisionDetector {
    constructor() {
        this.players = new Map();
        this.foods = [];
    }
    
    // 添加玩家
    addPlayer(player) {
        this.players.set(player.id, player);
    }
    
    // 移除玩家
    removePlayer(playerId) {
        this.players.delete(playerId);
    }
    
    // 添加食物
    addFood(food) {
        this.foods.push(food);
    }
    
    // 更新所有碰撞
    updateCollisions() {
        // 玩家与食物碰撞检测
        this.checkPlayerFoodCollisions();
        
        // 玩家之间碰撞检测
        this.checkPlayerPlayerCollisions();
    }
    
    // 玩家与食物碰撞检测
    checkPlayerFoodCollisions() {
        for (const [playerId, player] of this.players) {
            for (let i = 0; i < this.foods.length; i++) {
                const food = this.foods[i];
                const distance = this.getDistance(player, food);
                
                if (distance < player.size + food.size) {
                    // 玩家吃掉食物
                    player.eatFood(food);
                    
                    // 移除食物并生成新食物
                    this.foods.splice(i, 1);
                    this.generateNewFood();
                    i--;
                }
            }
        }
    }
    
    // 玩家之间碰撞检测
    checkPlayerPlayerCollisions() {
        const playersToRemove = [];
        
        for (const [playerId, player] of this.players) {
            for (const [targetId, target] of this.players) {
                if (playerId === targetId) continue;
                
                const distance = this.getDistance(player, target);
                
                // 如果玩家更大，可以吃掉目标
                if (distance < player.size && player.size > target.size * 1.1) {
                    // 玩家吃掉目标
                    const score = player.eatPlayer(target);
                    
                    // 记录得分
                    player.addScore(score);
                    
                    // 标记目标为待删除
                    if (!playersToRemove.includes(targetId)) {
                        playersToRemove.push(targetId);
                    }
                }
            }
        }
        
        // 移除被吃掉的玩家
        for (const playerId of playersToRemove) {
            this.players.delete(playerId);
        }
    }
    
    // 计算两点距离
    getDistance(obj1, obj2) {
        const dx = obj1.position.x - obj2.position.x;
        const dy = obj1.position.y - obj2.position.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    // 生成新食物
    generateNewFood() {
        const food = {
            id: generateId(),
            x: Math.random() * MAP_WIDTH,
            y: Math.random() * MAP_HEIGHT,
            size: Math.random() * 5 + 2,
            color: this.getRandomColor()
        };
        this.foods.push(food);
    }
}