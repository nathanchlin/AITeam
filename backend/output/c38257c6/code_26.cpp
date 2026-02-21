// 计算两个向量的点积
float dot(const Vector2& a, const Vector2& b) {
    return a.x * b.x + a.y * b.y;
}

// 限制值在指定范围内
float clamp(float value, float min, float max) {
    return std::max(min, std::min(max, value));
}