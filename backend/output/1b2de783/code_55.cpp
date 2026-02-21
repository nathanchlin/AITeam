class Game {
private:
    ParticleSystem particleSystem;
    std::vector<ExplosionEffect> explosions;
    ShootingEffect shootingEffect;
    HitEffect hitEffect;
    
public:
    void update(float deltaTime) {
        // 更新粒子系统
        particleSystem.update(deltaTime);
        
        // 更新所有爆炸效果
        for (auto it = explosions.begin(); it != explosions.end(); ) {
            it->update(deltaTime);
            if (!it->getActive()) {
                it = explosions.erase(it);
            } else {
                ++it;
            }
        }
        
        // 更新射击效果
        shootingEffect.update(deltaTime);
        
        // 更新命中效果
        hitEffect.update(deltaTime);
    }
    
    void render(const glm::mat4& projection) {
        // 渲染粒子系统
        particleSystem.render(projection);
        
        // 渲染所有爆炸效果
        for (const auto& explosion : explosions) {
            explosion.render(projection);
        }
        
        // 渲染射击效果
        shootingEffect.render(projection);
        
        // 渲染命中效果
        hitEffect.render(projection);
    }
    
    void createExplosion(const glm::vec2& position) {
        explosions.emplace_back();
        explosions.back().create(position);
    }
    
    void fireWeapon(const glm::vec2& startPos, const glm::vec2& direction) {
        shootingEffect.fire(startPos, direction);
    }
    
    void createHitEffect(const glm::vec2& position) {
        hitEffect.createHit(position);
    }
};