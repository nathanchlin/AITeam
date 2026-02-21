// 食物生成系统
class FoodSystem {
    constructor() {
        this.foods = [];
        this.baseFoodCount = 500;
        this.foodPerPlayer = 10;
        this.rareFoodChance = 0.05; // 5%概率生成稀有食物
    }
    
    // 初始化食物
    initialize(playerCount) {
        this.foods = [];
        const foodCount = this.baseFoodCount + playerCount * this.foodPerPlayer;
        
        for (let i = 0; i < foodCount; i++) {
            this.foods.push(this.createFood());
        }
    }
    
    // 创建食物
    createFood() {
        const isRare = Math.random() < this.rareFoodChance;
        
        return {
            id: Date.now() + Math.random(),
            x: Math.random() * MAP_WIDTH,
            y: Math.random() * MAP_HEIGHT,
            size: isRare ? Math.random() * 8 + 5 : Math.random() * 5 + 2,
            color: isRare ? this.getRandomRareColor() : this.getRandomColor(),
            type: isRare ? 'rare' : 'normal',
            value: isRare ? 5 : 1
        };
    }
    
    // 获取随机颜色
    getRandomColor() {
        const colors = ['#FF5252', '#FF4081', '#E040FB', '#7C4DFF', '#536DFE', 
                        '#448AFF', '#40C4FF', '#18FFFF', '#64FFDA', '#69F0AE',
                        '#B2FF59', '#EEFF41', '#FFFF00', '#FFD740', '#FFAB40',
                        '#FF6E40'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    // 获取稀有食物颜色
    getRandomRareColor() {
        const rareColors = ['#FFD700', '#FF1493', '#00CED1', '#9370DB', '#32CD32'];
        return rareColors[Math.floor(Math.random() * rareColors.length)];
    }
    
    // 补充食物
    replenishFood(playerCount) {
        const foodCount = this.baseFoodCount + playerCount * this.foodPerPlayer;
        
        while (this.foods.length < foodCount) {
            this.foods.push(this.createFood());
        }
    }
    
    // 移除被吃掉的食物
    removeFood(foodId) {
        this.foods = this.foods.filter(food => food.id !== foodId);
    }
}