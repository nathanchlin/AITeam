class Paddle {
private:
    Vector2 position;
    Vector2 velocity;
    float width;
    float height;
    float speed;
    
public:
    Paddle(float x, float y, float width, float height, float speed);
    
    // 访问器
    Vector2 getPosition() const { return position; }
    Vector2 getVelocity() const { return velocity; }
    float getWidth() const { return width; }
    float getHeight() const { return height; }
    
    // 修改器
    void setPosition(const Vector2& pos) { position = pos; }
    void setVelocity(const Vector2& vel) { velocity = vel; }
    void setSpeed(float newSpeed) { speed = newSpeed; }
    
    // 移动方法
    void moveLeft(float deltaTime);
    void moveRight(float deltaTime, int screenWidth);
    
    // 渲染边界
    SDL_Rect getRect() const;
};