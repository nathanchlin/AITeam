class ExplosionEffect {
private:
    ParticleSystem particleSystem;
    glm::vec2 position;
    bool isActive;
    float duration;
    float elapsed;
    
public:
    ExplosionEffect() : isActive(false), duration(0.5f), elapsed(0.0f) {}
    
    void create(const glm::vec2& pos) {
        position = pos;
        isActive = true;
        elapsed = 0.0f;
        
        // 创建初始爆炸粒子
        particleSystem.emit(position, 100, glm::vec4(1.0f, 0.5f, 0.0f, 1.0f));
        
        // 创建延迟的烟雾效果
        particleSystem.emit(position, 50, glm::vec4(0.5f, 0.5f, 0.5f, 0.7f));
    }
    
    void update(float deltaTime) {
        if (isActive) {
            elapsed += deltaTime;
            particleSystem.update(deltaTime);
            
            // 在爆炸过程中持续产生粒子
            if (elapsed < duration) {
                if (rand() % 5 == 0) {
                    particleSystem.emit(position, 10, glm::vec4(1.0f, 0.3f, 0.0f, 0.8f));
                }
            } else {
                isActive = false;
            }
        }
    }
    
    void render(const glm::mat4& projection) {
        if (isActive) {
            particleSystem.render(projection);
        }
    }
    
    bool getActive() const { return isActive; }
};