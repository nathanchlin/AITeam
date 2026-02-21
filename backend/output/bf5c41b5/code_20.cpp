struct Vector2 {
    float x, y;
    
    Vector2 operator+(const Vector2& other) const {
        return {x + other.x, y + other.y};
    }
    
    Vector2 operator-(const Vector2& other) const {
        return {x - other.x, y - other.y};
    }
    
    Vector2 operator*(float scalar) const {
        return {x * scalar, y * scalar};
    }
};

struct Ball {
    Vector2 position;
    Vector2 velocity;
    float radius;
};

struct Paddle {
    Vector2 position;
    float width;
    float height;
};

struct Brick {
    Vector2 position;
    float width;
    float height;
    bool active;
};