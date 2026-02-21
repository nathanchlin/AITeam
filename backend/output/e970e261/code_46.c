void updateGame() {
    // 更新玩家
    updatePlayer();
    
    // 更新敌人
    updateEnemies();
    
    // 更新物品
    updateItems();
    
    // 更新摄像机
    updateCamera();
    
    // 检查碰撞
    checkCollisions();
    
    // 检查关卡完成条件
    checkLevelComplete();
    
    // 更新关卡过渡
    updateLevelTransition();
    
    // 检查游戏结束条件
    if (player.lives <= 0) {
        gameOver();
    }
}

void render() {
    // 根据当前状态渲染
    switch (currentGameState) {
        case GAME_STATE_TITLE:
            renderTitleScreen();
            break;
            
        case GAME_STATE_PLAYING:
            // 渲染游戏世界
            renderGameWorld();
            
            // 渲染UI
            renderGameUI();
            
            // 渲染关卡过渡效果
            renderLevelTransition();
            break;
            
        case GAME_STATE_PAUSED:
            renderGameWorld(); // 先渲染游戏画面
            renderPauseOverlay(); // 再渲染暂停覆盖层
            break;
            
        case GAME_STATE_GAME_OVER:
            renderGameOverScreen();
            break;
            
        case GAME_STATE_WORLD_MAP:
            renderWorldMap();
            break;
            
        case GAME_STATE_CUTSCENE:
            renderCutscene();
            break;
    }
}