// coin.cpp
#include "coin.h"

Coin::Coin(float x, float y) : Collectible(x, y, CollectibleType::COIN) {
    m_bobOffset = 0.0f;
    m_bobSpeed = 2.0f;
    m_rotation = 0.0f;
}

void Coin::update(float deltaTime) {
    if (m_isCollected) {
        // 收集后淡出或上升消失
        m_y -= 100 * deltaTime;
        m_alpha -= 200 * deltaTime;
        if (m_alpha <= 0) {
            m_isActive = false;
        }
        return;
    }
    
    bob(deltaTime);
    rotate(deltaTime);
}

void Coin::bob(float deltaTime) {
    m_bobOffset += m_bobSpeed * deltaTime;
    m_y += sin(m_bobOffset) * 0.5f;
}

void Coin::rotate(float deltaTime) {
    m_rotation += 180 * deltaTime;
}

void Coin::onCollision(GameObject* other) {
    if (m_isCollected) return;
    
    if (other->getType() == ObjectType::PLAYER) {
        m_isCollected = true;
        applyEffect(static_cast<Player*>(other));
    }
}

void Coin::applyEffect(Player* player) {
    // 添加分数
    player->addScore(100);
    
    // 播放收集音效
    // Game::getInstance()->getAudioManager()->playSound("coin");
    
    // 可能增加金币计数
    player->incrementCoins();
}