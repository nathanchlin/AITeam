class Brick {
private:
    Vector2 position;
    float width;
    float height;
    bool active;
    int hitsRequired;
    int points;
    
public:
    Brick(float x, float y, float width, float height, int hits, int points);
    
    // 访问器
    Vector2 getPosition() const { return position; }
    float getWidth() const { return width; }
    float getHeight() const { return height; }
    bool isActive() const { return active; }
    int getHitsRequired() const { return hitsRequired; }
    int getPoints() const { return points; }
    
    // 修改器
    void setPosition(const Vector2& pos) { position = pos; }
    void setActive(bool state) { active = state; }
    void hit();
    
    // 渲染边界
    SDL_Rect getRect() const;
};