// 计算玩家速度
function calculatePlayerSpeed(size) {
    // 基础速度
    const baseSpeed = 5;
    // 最大尺寸
    const maxSize = 100;
    // 最小速度系数
    const minSpeedFactor = 0.3;
    
    // 速度与大小成反比，但有最小限制
    const speedFactor = Math.max(minSpeedFactor, 1 - (size / maxSize) * 0.7);
    
    return baseSpeed * speedFactor;
}