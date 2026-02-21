// collectible.h
#ifndef COLLECTIBLE_H
#define COLLECTIBLE_H

#include "gameobject.h"

enum class CollectibleType {
    COIN,
    MUSHROOM,
    STAR,
    FIRE_FLOWER
};

class Collectible : public GameObject {
public:
    Collectible(float x, float y, CollectibleType type);
    virtual ~Collectible() {}
    
    virtual void update(float deltaTime) override;
    virtual void render() override;
    virtual void onCollision(GameObject* other) override;
    
    CollectibleType getType() const { return m_type; }
    bool isCollected() const { return m_isCollected; }
    
protected:
    CollectibleType m_type;
    bool m_isCollected;
    float m_bobOffset;
    float m_bobSpeed;
    float m_rotation;
    
    virtual void applyEffect(Player* player);
    virtual void bob(float deltaTime);
    virtual void rotate(float deltaTime);
};

#endif // COLLECTIBLE_H