class CollisionSystem : public System {
private:
    std::vector<std::unique_ptr<CollisionShape>> collisionShapes;
    
public:
    void update(float deltaTime) override;
    void checkCollisions();
    void addCollisionShape(std::unique_ptr<CollisionShape> shape);
    bool checkCollision(CollisionShape* a, CollisionShape* b);
};

class CollisionComponent : public Component {
public:
    std::unique_ptr<CollisionShape> shape;
    bool isTrigger;
    std::function<void(Entity* other)> onCollision;
};