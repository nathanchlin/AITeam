class PhysicsEngine {
private:
    // 碰撞检测数据结构
    struct CollisionInfo {
        bool hasCollision;
        Vector2 normal;
        float penetration;
    };
    
public:
    // 运动更新
    void updateBall(Ball& ball, float deltaTime);
    void updatePaddle(Paddle& paddle, float deltaTime);
    
    // 碰撞检测
    CollisionInfo checkBallPaddleCollision(const Ball& ball, const Paddle& paddle);
    CollisionInfo checkBallBrickCollision(const Ball& ball, const Brick& brick);
    CollisionInfo checkBallWallCollision(const Ball& ball, int screenWidth, int screenHeight);
    
    // 碰撞响应
    void resolveBallPaddleCollision(Ball& ball, const Paddle& paddle);
    void resolveBallBrickCollision(Ball& ball, Brick& brick);
    void resolveBallWallCollision(Ball& ball, int screenWidth, int screenHeight);
    
    // 边界检查
    bool isBallOut(const Ball& ball, int screenHeight);
};