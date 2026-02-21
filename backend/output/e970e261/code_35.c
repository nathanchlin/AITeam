// mushroom.cpp
#include "mushroom.h"

Mushroom::Mushroom(float x, float y) : Collectible(x, y, CollectibleType::MUSHROOM) {
    m_velocityX = 50.0f;
    m_velocityY = 0.0f;
    m_gravity = 500.0f;
}

void Mushroom::update(float deltaTime) {
    if (m_isCollected) return;
    
    // 应用重力
    if (!isOnGround()) {
        m_velocityY += m_gravity * deltaTime;
    } else {
        m_velocityY = 0.0f;
        // 在地面上时随机改变方向
        if (rand() % 100 < 2) {
            m_velocityX = -m_velocityX;
        }
    }
    
    m_x += m_velocityX * deltaTime;
    m_y += m_velocityY * deltaTime;
    
    // 检查是否掉出屏幕
    if (m_y > Game::getInstance()->getScreenHeight() + 50) {
        m_isActive = false;
    }
}

void Mushroom::onCollision(GameObject* other) {
    if (m_isCollected) return;
    
    if (other->getType() == ObjectType::PLAYER) {
        m_isCollected = true;
        applyEffect(static_cast<Player*>(other));
    }
}

void Mushroom::applyEffect(Player* player) {
    // 使玩家变大
    player->grow();
    
    // 播放音效
    // Game::getInstance()->getAudioManager()->playSound("powerup");
    
    // 添加分数
    player->addScore(1000);
}