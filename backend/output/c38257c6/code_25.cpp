class PhysicsEngine {
public:
    void update(float deltaTime, Game& game) {
        // 更新球的位置
        game.ball.update(deltaTime);
        
        // 检测并处理碰撞
        checkWallCollision(game.ball, game.gameArea);
        
        if (checkPaddleCollision(game.ball, game.paddle)) {
            game.onPaddleHit();
        }
        
        // 检查与砖块的碰撞
        for (auto& brick : game.bricks) {
            if (brick.active && checkBrickCollision(game.ball, brick)) {
                brick.active = false;
                game.onBrickHit(brick);
            }
        }
        
        // 检查游戏结束条件
        if (game.ball.position.y - game.ball.radius > game.gameArea.bottom) {
            game.onGameOver();
        }
    }
};