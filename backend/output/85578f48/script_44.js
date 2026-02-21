// 食物价值计算
function calculateFoodValue(food, playerSize) {
    // 基础价值与大小成正比
    let baseValue = food.size * 0.5;
    
    // 稀有食物加成
    if (food.type === 'rare') {
        baseValue *= 3;
    }
    
    // 大球吃小球惩罚
    if (playerSize > food.size * 3) {
        baseValue *= 0.5; // 大球吃小球只能获得50%价值
    }
    
    // 小球吃大球奖励
    if (playerSize < food.size * 0.5) {
        baseValue *= 1.5; // 小球吃大球获得150%价值
    }
    
    return Math.floor(baseValue);
}