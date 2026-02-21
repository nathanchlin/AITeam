class PhysicsEngine {
public:
    struct CollisionInfo {
        bool isColliding;
        glm::vec2 collisionNormal;
        float penetrationDepth;
    };
    
    void update(float deltaTime);
    CollisionInfo checkCollision(const GameObject& obj1, const GameObject& obj2);
    void resolveCollision(GameObject& obj1, GameObject& obj2, const CollisionInfo& info);
    
    // 简化的碰撞检测
    bool checkBallPaddleCollision(const Ball& ball, const Paddle& paddle);
    bool checkBallBrickCollision(const Ball& ball, const Brick& brick);
};