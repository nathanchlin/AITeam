class Ball {
private:
    Vector2 position;
    Vector2 velocity;
    float radius;
    float speed;
    
public:
    Ball(float x, float y, float radius, float speed);
    
    // 访问器
    Vector2 getPosition() const { return position; }
    Vector2 getVelocity() const { return velocity; }
    float getRadius() const { return radius; }
    float getSpeed() const { return speed; }
    
    // 修改器
    void setPosition(const Vector2& pos) { position = pos; }
    void setVelocity(const Vector2& vel) { velocity = vel; }
    void setSpeed(float newSpeed) { speed = newSpeed; }
    
    // 移动方法
    void move(float deltaTime);
    
    // 渲染边界
    SDL_Rect getRect() const;
};