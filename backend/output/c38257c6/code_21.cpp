struct Ball {
    Vector2 position;
    Vector2 velocity;
    float radius;
    float mass = 1.0f;
    
    void update(float deltaTime) {
        position += velocity * deltaTime;
        velocity *= PhysicsConfig().friction; // 应用空气阻力
    }
};