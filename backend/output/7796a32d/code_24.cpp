class CollisionSystem {
private:
    std::vector<Platform> platforms;
    std::vector<Obstacle> obstacles;
    Player player;
    
public:
    void update(float deltaTime) {
        // 更新玩家位置
        player.update(deltaTime);
        
        // 执行碰撞检测
        checkCollisions();
    }
    
private:
    void checkCollisions() {
        // 检测与平台的碰撞
        for (const auto& platform : platforms) {
            auto collision = checkAABBCollisionWithDirection(player.getBoundingBox(), platform.getBoundingBox());
            
            if (collision.bottom) {
                // 玩家落在平台上
                player.landOnPlatform(platform);
            } else if (collision.top) {
                // 玩家撞到平台底部
                player.hitPlatformBottom();
            }
            
            if (collision.left || collision.right) {
                // 玩家撞到平台侧面
                player.hitPlatformSide();
            }
        }
        
        // 检测与障碍物的碰撞
        for (const auto& obstacle : obstacles) {
            if (checkAABBCollision(player.getBoundingBox(), obstacle.getBoundingBox())) {
                player.hitObstacle(obstacle);
            }
        }
    }
};