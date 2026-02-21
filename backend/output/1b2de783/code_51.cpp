class Particle {
public:
    glm::vec2 position;
    glm::vec2 velocity;
    glm::vec4 color;
    float size;
    float life;
    float rotation;
    float rotationSpeed;
    
    Particle() : position(0.0f), velocity(0.0f), color(1.0f), 
                 size(1.0f), life(1.0f), rotation(0.0f), rotationSpeed(0.0f) {}
};

class ParticleSystem {
private:
    std::vector<Particle> particles;
    unsigned int VAO, VBO;
    Shader particleShader;
    
public:
    ParticleSystem() {
        // 初始化VAO和VBO
        glGenVertexArrays(1, &VAO);
        glGenBuffers(1, &VBO);
        
        // 绑定VAO和VBO
        glBindVertexArray(VAO);
        glBindBuffer(GL_ARRAY_BUFFER, VBO);
        
        // 设置顶点属性指针
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Particle), (void*)offsetof(Particle, position));
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, sizeof(Particle), (void*)offsetof(Particle, color));
        glEnableVertexAttribArray(2);
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, sizeof(Particle), (void*)offsetof(Particle, size));
        
        glBindBuffer(GL_ARRAY_BUFFER, 0);
        glBindVertexArray(0);
        
        // 加载粒子着色器
        particleShader = Shader("particle.vert", "particle.frag");
    }
    
    void emit(const glm::vec2& position, int count, const glm::vec4& color) {
        for (int i = 0; i < count; i++) {
            Particle p;
            p.position = position;
            
            // 随机速度方向
            float angle = (rand() % 360) * 3.14159f / 180.0f;
            float speed = 0.5f + (rand() % 100) / 100.0f * 2.0f;
            p.velocity.x = cos(angle) * speed;
            p.velocity.y = sin(angle) * speed;
            
            p.color = color;
            p.size = 5.0f + (rand() % 50) / 10.0f;
            p.life = 1.0f;
            p.rotation = (rand() % 360) * 3.14159f / 180.0f;
            p.rotationSpeed = (rand() % 100 - 50) / 100.0f;
            
            particles.push_back(p);
        }
    }
    
    void update(float deltaTime) {
        for (auto it = particles.begin(); it != particles.end(); ) {
            it->life -= deltaTime * 2.0f; // 粒子生命周期
            if (it->life <= 0.0f) {
                it = particles.erase(it);
            } else {
                it->position += it->velocity * deltaTime;
                it->velocity *= 0.98f; // 速度衰减
                it->rotation += it->rotationSpeed * deltaTime;
                it->size *= 0.99f; // 粒子大小衰减
                it->color.a = it->life; // 透明度随生命周期变化
                ++it;
            }
        }
    }
    
    void render(const glm::mat4& projection) {
        particleShader.use();
        particleShader.setMat4("projection", projection);
        
        glBindVertexArray(VAO);
        glBindBuffer(GL_ARRAY_BUFFER, VBO);
        
        // 更新VBO数据
        glBufferData(GL_ARRAY_BUFFER, particles.size() * sizeof(Particle), particles.data(), GL_DYNAMIC_DRAW);
        
        // 渲染粒子
        glDrawArrays(GL_POINTS, 0, particles.size());
        
        glBindBuffer(GL_ARRAY_BUFFER, 0);
        glBindVertexArray(0);
    }
};