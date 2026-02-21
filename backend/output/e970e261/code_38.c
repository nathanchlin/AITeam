// game.cpp
void Game::initialize() {
    // 创建玩家
    m_player = new Player(100, 300);
    
    // 初始化关卡
    LevelManager::getInstance()->initialize();
    
    // 生成一些敌人和收集品
    LevelManager::getInstance()->spawnEnemy(300, 350, EnemyType::GOOMBA);
    LevelManager::getInstance()->spawnEnemy(500, 350, EnemyType::GOOMBA);
    LevelManager::getInstance()->spawnCollectible(200, 300, CollectibleType::COIN);
    LevelManager::getInstance()->spawnCollectible(400, 280, CollectibleType::MUSHROOM);
}

void Game::update(float deltaTime) {
    // 更新玩家
    m_player->update(deltaTime);
    
    // 更新关卡中的敌人和收集品
    LevelManager::getInstance()->update(deltaTime);
    
    // 检测碰撞
    CollisionManager::getInstance()->checkCollisions();
}