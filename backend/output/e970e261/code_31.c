// enemy.h
#ifndef ENEMY_H
#define ENEMY_H

#include "character.h"
#include "game.h"

class Enemy : public Character {
public:
    Enemy(float x, float y, EnemyType type);
    virtual ~Enemy() {}
    
    virtual void update(float deltaTime) override;
    virtual void render() override;
    virtual void onCollision(GameObject* other) override;
    
    EnemyType getType() const { return m_type; }
    void setDirection(Direction dir) { m_direction = dir; }
    
protected:
    EnemyType m_type;
    Direction m_direction;
    float m_moveSpeed;
    float m_patrolDistance;
    float m_startX;
    bool m_isAlive;
    
    virtual void move(float deltaTime);
    virtual void patrol(float deltaTime);
    virtual void chasePlayer(float deltaTime);
    virtual void die();
};

#endif // ENEMY_H