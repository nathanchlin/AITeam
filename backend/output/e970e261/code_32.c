// goomba.cpp
#include "goomba.h"

Goomba::Goomba(float x, float y) : Enemy(x, y, EnemyType::GOOMBA) {
    m_moveSpeed = 50.0f;
    m_patrolDistance = 100.0f;
    m_startX = x;
    m_isAlive = true;
    m_isJumping = false;
    m_jumpVelocity = 0.0f;
    m_gravity = 500.0f;
    m_jumpPower = -200.0f;
}

void Goomba::update(float deltaTime) {
    if (!m_isAlive) return;
    
    // 检测玩家是否在附近
    Player* player = Game::getInstance()->getPlayer();
    float distance = abs(player->getX() - m_x);
    
    if (distance < 150.0f) {
        chasePlayer(deltaTime);
    } else {
        patrol(deltaTime);
    }
    
    // 应用重力
    if (!isOnGround()) {
        m_jumpVelocity += m_gravity * deltaTime;
    } else {
        m_jumpVelocity = 0.0f;
        m_isJumping = false;
    }
    
    m_y += m_jumpVelocity * deltaTime;
    
    // 检查是否掉出屏幕
    if (m_y > Game::getInstance()->getScreenHeight() + 50) {
        m_isAlive = false;
    }
}

void Goomba::patrol(float deltaTime) {
    // 简单的巡逻行为
    if (m_x <= m_startX - m_patrolDistance) {
        m_direction = Direction::RIGHT;
    } else if (m_x >= m_startX + m_patrolDistance) {
        m_direction = Direction::LEFT;
    }
    
    move(deltaTime);
}

void Goomba::chasePlayer(float deltaTime) {
    Player* player = Game::getInstance()->getPlayer();
    
    if (player->getX() < m_x) {
        m_direction = Direction::LEFT;
    } else {
        m_direction = Direction::RIGHT;
    }
    
    move(deltaTime);
    
    // 如果玩家在上方，尝试跳跃
    if (player->getY() < m_y - 20 && !m_isJumping && isOnGround()) {
        jump();
    }
}

void Goomba::move(float deltaTime) {
    float moveAmount = m_moveSpeed * deltaTime;
    
    if (m_direction == Direction::LEFT) {
        m_x -= moveAmount;
    } else {
        m_x += moveAmount;
    }
}

void Goomba::onCollision(GameObject* other) {
    if (!m_isAlive) return;
    
    if (other->getType() == ObjectType::PLAYER) {
        Player* player = static_cast<Player*>(other);
        
        // 如果玩家从上方踩踏敌人
        if (player->getVelocity().y > 0 && player->getY() < m_y) {
            die();
            player->bounce();
        } else {
            // 玩家受伤
            player->takeDamage();
        }
    }
}

void Goomba::die() {
    m_isAlive = false;
    // 播放死亡动画
    // 可以添加分数等
}