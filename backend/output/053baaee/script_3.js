function checkBulletTargetCollision(bullet, target) {
    if (target.type === 'tank') {
        // 圆形碰撞检测
        const dx = bullet.x - target.x;
        const dy = bullet.y - target.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < target.radius;
    } else if (target.type === 'obstacle') {
        // 矩形碰撞检测
        return bullet.x > target.x && 
               bullet.x < target.x + target.width &&
               bullet.y > target.y && 
               bullet.y < target.y + target.height;
    }
    return false;
}