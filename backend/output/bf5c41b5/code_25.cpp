void updateCollisions(Ball& ball, Paddle& paddle, std::vector<Brick>& bricks, 
                     SpatialGrid& spatialGrid, float screenWidth, float screenHeight) {
    // 检查边界碰撞
    if (!checkBoundaryCollision(ball, screenWidth, screenHeight)) {
        // 游戏结束
        return;
    }
    
    // 检查挡板碰撞
    checkPaddleCollision(ball, paddle);
    
    // 更新空间分区
    spatialGrid.clear();
    for (Brick& brick : bricks) {
        if (brick.active) {
            spatialGrid.add(brick);
        }
    }
    
    // 获取附近的砖块并检测碰撞
    std::vector<Brick*> nearbyBricks = spatialGrid.getNearbyBricks(ball);
    for (Brick* brick : nearbyBricks) {
        if (checkBrickCollision(ball, *brick)) {
            // 碰撞处理
        }
    }
}