class GameObject {
public:
    glm::vec2 position;
    glm::vec2 velocity;
    glm::vec2 size;
    glm::vec4 color;
    
    virtual void update(float deltaTime) = 0;
    virtual void render(Renderer& renderer) = 0;
    virtual void onCollision(GameObject& other) = 0;
    
    // AABB碰撞检测
    bool isCollidingWith(const GameObject& other) const;
};