class Paddle : public GameObject {
public:
    float speed;
    
    void update(float deltaTime) override;
    void render(Renderer& renderer) override;
    void onCollision(GameObject& other) override;
    
    void moveLeft();
    void moveRight();
};