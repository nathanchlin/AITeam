// 工具函数集合
const Utils = {
    // 生成随机数
    random: (min, max) => {
        return Math.random() * (max - min) + min;
    },
    
    // 生成随机整数
    randomInt: (min, max) => {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },
    
    // 检测碰撞
    checkCollision: (rect1, rect2) => {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    },
    
    // 限制值在范围内
    clamp: (value, min, max) => {
        return Math.min(Math.max(value, min), max);
    },
    
    // 角度转换为弧度
    toRadians: (degrees) => {
        return degrees * (Math.PI / 180);
    },
    
    // 弧度转换为角度
    toDegrees: (radians) => {
        return radians * (180 / Math.PI);
    }
};