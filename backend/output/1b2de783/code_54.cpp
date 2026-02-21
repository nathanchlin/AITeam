class HitEffect {
private:
    ParticleSystem particleSystem;
    std::vector<std::pair<glm::vec2, float>> hitMarkers;
    
public:
    void createHit(const glm::vec2& position) {
        // 创建命中标记
        hitMarkers.emplace_back(position, 1.0f);
        
        // 创建命中粒子
        particleSystem.emit(position, 30, glm::vec4(0.0f, 1.0f, 1.0f, 1.0f));
    }
    
    void update(float deltaTime) {
        particleSystem.update(deltaTime);
        
        // 更新命中标记
        for (auto it = hitMarkers.begin(); it != hitMarkers.end(); ) {
            it->second -= deltaTime * 2.0f; // 标记逐渐消失
            if (it->second <= 0.0f) {
                it = hitMarkers.erase(it);
            } else {
                ++it;
            }
        }
    }
    
    void render(const glm::mat4& projection) {
        particleSystem.render(projection);
        
        // 渲染命中标记
        for (const auto& marker : hitMarkers) {
            // 渲染十字准星或其他命中标记
            float size = 10.0f * marker.second;
            // 绘制标记...
        }
    }
};