function predictCollision(object1, object2, timeStep) {
    // 计算未来位置
    const futureX1 = object1.x + object1.vx * timeStep;
    const futureY1 = object1.y + object1.vy * timeStep;
    const futureX2 = object2.x + object2.vx * timeStep;
    const futureY2 = object2.y + object2.vy * timeStep;
    
    // 检查未来位置是否碰撞
    return checkCollision(
        {x: futureX1, y: futureY1, radius: object1.radius},
        {x: futureX2, y: futureY2, radius: object2.radius}
    );
}