// 使用固定时间步长和累积器
class PhysicsEngine {
private:
    const float fixedDeltaTime = 1.0f / 60.0f; // 60 FPS
    float accumulator = 0.0f;
    
public:
    void update(float deltaTime) {
        accumulator += deltaTime;
        
        while (accumulator >= fixedDeltaTime) {
            // 使用固定时间步长进行物理模拟
            updatePhysicsStep(fixedDeltaTime);
            accumulator -= fixedDeltaTime;
        }
    }
    
    void updatePhysicsStep(float dt) {
        // 简化的物理更新
        for (auto& entity : entities) {
            // 只对可见区域内的实体进行物理计算
            if (isInViewport(entity)) {
                entity.velocity += entity.acceleration * dt;
                entity.position += entity.velocity * dt;
            }
        }
    }
};