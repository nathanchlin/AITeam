// collisionmanager.h
#ifndef COLLISIONMANAGER_H
#define COLLISIONMANAGER_H

#include "gameobject.h"
#include "player.h"
#include "enemy.h"
#include "collectible.h"

class CollisionManager {
public:
    static CollisionManager* getInstance();
    
    void checkCollisions();
    void checkPlayerCollisions(Player* player);
    void checkEnemyCollisions();
    void checkCollectibleCollisions();
    
private:
    CollisionManager() {}
    static CollisionManager* m_instance;
    
    bool checkAABB(const GameObject* a, const GameObject* b);
    bool checkCircleAABB(const Circle& circle, const AABB& aabb);
    void resolveCollision(GameObject* a, GameObject* b);
};

#endif // COLLISIONMANAGER_H