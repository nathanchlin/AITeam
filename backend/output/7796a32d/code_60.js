// 工具函数
const Utils = {
    // 生成随机整数
    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },
    
    // 生成随机浮点数
    randomFloat(min, max) {
        return Math.random() * (max - min) + min;
    },
    
    // 计算两点之间的距离
    distance(x1, y1, x2, y2) {
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    },
    
    // 检查矩形碰撞
    rectCollision(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    },
    
    // 格式化数字为两位数
    formatNumber(num) {
        return num < 10 ? '0' + num : num;
    },
    
    // 缓动函数
    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
};