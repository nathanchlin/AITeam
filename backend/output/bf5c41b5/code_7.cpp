class Brick : public GameObject {
public:
    int hits;  // 需要击中的次数
    bool isPowerUp;  // 是否包含道具
    PowerUpType powerUpType;  // 道具类型
    
    void update(float deltaTime) override;
    void render(Renderer& renderer) override;
    void onCollision(GameObject& other) override;
    
    void hit();
    bool isDestroyed() const;
};