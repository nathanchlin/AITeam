class EnemySpawnSystem : public System {
private:
    float spawnInterval;
    float lastSpawnTime;
    int maxEnemies;
    float spawnRadius;
    std::vector<EnemyType> enemyTypes;
    
public:
    void update(float deltaTime) override;
    Entity* spawnEnemy(const EnemyType& type);
    void setSpawnRate(float rate);
    void setMaxEnemies(int count);
    void addEnemyType(const EnemyType& type);
};

class EnemyAIComponent : public Component {
public:
    enum AIType { PATROL, CHASE, RANDOM };
    AIType aiType;
    float speed;
    float detectionRange;
    std::function<void(Entity* target)> onTargetAcquired;
};