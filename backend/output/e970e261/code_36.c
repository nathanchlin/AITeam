// levelmanager.h
#ifndef LEVELMANAGER_H
#define LEVELMANAGER_H

#include <vector>
#include "enemy.h"
#include "collectible.h"

class LevelManager {
public:
    static LevelManager* getInstance();
    
    void initialize();
    void update(float deltaTime);
    void render();
    
    void spawnEnemy(float x, float y, EnemyType type);
    void spawnCollectible(float x, float y, CollectibleType type);
    void clearAll();
    
    std::vector<Enemy*> getEnemies() const { return m_enemies; }
    std::vector<Collectible*> getCollectibles() const { return m_collectibles; }
    
private:
    LevelManager() {}
    static LevelManager* m_instance;
    
    std::vector<Enemy*> m_enemies;
    std::vector<Collectible*> m_collectibles;
    
    void loadLevelData(int level);
    void spawnEnemiesFromData(const std::vector<EnemySpawnData>& data);
    void spawnCollectiblesFromData(const std::vector<CollectibleSpawnData>& data);
};

#endif // LEVELMANAGER_H