class Player {
private:
    Vector2 position;
    Vector2 velocity;
    bool isJumping;
    bool isFalling;
    float jumpPower;
    float gravity;
    float moveSpeed;
    
public:
    void update(float deltaTime) {
        // 应用重力
        velocity.y += gravity * deltaTime;
        
        // 更新位置
        position.x += velocity.x * deltaTime;
        position.y += velocity.y * deltaTime;
    }
    
    void jump() {
        if (!isJumping && !isFalling) {
            velocity.y = -jumpPower;
            isJumping = true;
        }
    }
    
    void landOnPlatform(const Platform& platform) {
        position.y = platform.getBoundingBox().y - getBoundingBox().height;
        velocity.y = 0;
        isJumping = false;
        isFalling = false;
    }
    
    void hitPlatformBottom() {
        velocity.y = 0;
        position.y = getBoundingBox().y + getBoundingBox().height;
    }
    
    void hitPlatformSide() {
        velocity.x = 0;
    }
    
    void hitObstacle(const Obstacle& obstacle) {
        // 处理与障碍物的碰撞，可能造成游戏结束或生命值减少
        takeDamage(obstacle.getDamage());
    }
    
    Rect getBoundingBox() const {
        return Rect(position.x, position.y, width, height);
    }
};