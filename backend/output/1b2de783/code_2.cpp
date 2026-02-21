class PlayerControlSystem : public System {
private:
    float moveSpeed;
    float rotationSpeed;
    float fireRate;
    float lastFireTime;
    
public:
    PlayerControlSystem();
    void update(float deltaTime) override;
    void handleInput(const InputEvent& event);
    void movePlayer(Entity* player, const Vector2& direction);
    void rotatePlayer(Entity* player, float angle);
    void fireWeapon(Entity* player);
};

class PlayerInputComponent : public Component {
public:
    std::function<void(const InputEvent&)> onInput;
};