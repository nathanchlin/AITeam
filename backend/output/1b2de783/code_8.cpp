void GameEngine::run() {
    initialize();
    Clock clock;
    
    while (running) {
        float deltaTime = clock.restart().asSeconds();
        
        // 处理输入
        handleInput();
        
        // 更新游戏状态
        update(deltaTime);
        
        // 渲染
        render();
        
        // 控制帧率
        sf::sleep(sf::milliseconds(16) - clock.getElapsedTime()); // 约60FPS
    }
}

void GameEngine::update(float deltaTime) {
    // 更新所有系统
    for (auto& system : systems) {
        system->update(deltaTime);
    }
    
    // 更新实体
    entityManager->update(deltaTime);
}