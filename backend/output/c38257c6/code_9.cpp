// 主游戏循环
void gameLoop() {
    // 初始化
    GameStateManager gameState;
    Renderer renderer;
    PhysicsEngine physics;
    InputSystem input;
    
    // 创建游戏对象
    auto paddle = std::make_shared<Paddle>(...);
    auto ball = std::make_shared<Ball>(...);
    std::vector<std::shared_ptr<Brick>> bricks;
    
    // 注册到状态管理器
    gameState.setPaddle(paddle);
    gameState.setBall(ball);
    gameState.setBricks(bricks);
    
    // 游戏主循环
    while (!gameState.isGameOver() && !gameState.isWin()) {
        // 1. 处理输入
        input.update();
        input.handlePaddleMovement(*paddle, deltaTime);
        input.handleGameControls(gameState);
        
        // 2. 更新物理
        physics.updateBall(*ball, deltaTime);
        physics.updatePaddle(*paddle, deltaTime);
        
        // 3. 碰撞检测与响应
        if (auto collision = physics.checkBallPaddleCollision(*ball, *paddle)) {
            physics.resolveBallPaddleCollision(*ball, *paddle);
        }
        
        // 检测砖块碰撞
        for (auto& brick : bricks) {
            if (brick->isActive()) {
                if (auto collision = physics.checkBallBrickCollision(*ball, *brick)) {
                    physics.resolveBallBrickCollision(*ball, *brick);
                    brick->hit();
                    if (!brick->isActive()) {
                        gameState.addScore(brick->getPoints());
                    }
                }
            }
        }
        
        // 检测墙壁碰撞
        physics.resolveBallWallCollision(*ball, screenWidth, screenHeight);
        
        // 检测球是否掉落
        if (physics.isBallOut(*ball, screenHeight)) {
            gameState.loseLife();
            // 重置球和挡板位置
            ball->reset();
            paddle->reset();
        }
        
        // 4. 更新游戏状态
        gameState.update(deltaTime);
        
        // 5. 渲染
        renderer.clear();
        renderer.render(*paddle);
        renderer.render(*ball);
        renderer.render(bricks);
        renderer.renderUI(gameState.getScore(), gameState.getLives(), gameState.getState());
        renderer.present();
    }
}