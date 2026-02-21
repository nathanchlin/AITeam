class Ball : public GameObject {
public:
    float radius;
    glm::vec2 direction;
    
    void update(float deltaTime) override;
    void render(Renderer& renderer) override;
    void onCollision(GameObject& other) override;
    
    void launch();
    void reset();
};