class ShootingEffect {
private:
    ParticleSystem particleSystem;
    std::vector<glm::vec2> muzzleFlashes;
    std::vector<glm::vec2> bulletTrails;
    
public:
    void fire(const glm::vec2& startPos, const glm::vec2& direction) {
        // 枪口闪光
        muzzleFlashes.push_back(startPos);
        
        // 子弹轨迹
        for (int i = 0; i < 5; i++) {
            glm::vec2 trailPos = startPos + direction * (i * 5.0f);
            bulletTrails.push_back(trailPos);
        }
        
        // 创建枪口粒子
        particleSystem.emit(startPos, 20, glm::vec4(1.0f, 1.0f, 0.5f, 1.0f));
    }
    
    void update(float deltaTime) {
        particleSystem.update(deltaTime);
        
        // 更新枪口闪光
        for (auto it = muzzleFlashes.begin(); it != muzzleFlashes.end(); ) {
            // 枪口闪光会快速消失
            it->x += deltaTime * 50.0f; // 向右移动
            if (it->x > 100.0f) { // 超出屏幕边界
                it = muzzleFlashes.erase(it);
            } else {
                ++it;
            }
        }
        
        // 更新子弹轨迹
        for (auto it = bulletTrails.begin(); it != bulletTrails.end(); ) {
            // 轨迹粒子逐渐消失
            static float trailLifetime = 0.1f;
            static float trailElapsed = 0.0f;
            trailElapsed += deltaTime;
            
            if (trailElapsed > trailLifetime) {
                it = bulletTrails.erase(it);
                trailElapsed = 0.0f;
            } else {
                ++it;
            }
        }
    }
    
    void render(const glm::mat4& projection) {
        particleSystem.render(projection);
        
        // 渲染枪口闪光
        // 这里可以使用简单的精灵渲染
        for (const auto& pos : muzzleFlashes) {
            // 渲染闪光效果
        }
        
        // 渲染子弹轨迹
        for (const auto& pos : bulletTrails) {
            // 渲染轨迹效果
        }
    }
};