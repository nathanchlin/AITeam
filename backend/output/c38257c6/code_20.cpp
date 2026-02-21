struct PhysicsConfig {
    float gravity = 0.0f;  // 打砖块游戏通常不需要重力
    float friction = 0.99f; // 空气阻力
    float restitution = 0.95f; // 碰撞能量保持系数
};