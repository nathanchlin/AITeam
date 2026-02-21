void changeGameState(GameState newState) {
    previousGameState = currentGameState;
    currentGameState = newState;
    
    // 执行状态特定的初始化
    switch (newState) {
        case GAME_STATE_TITLE:
            initTitleScreen();
            break;
            
        case GAME_STATE_PLAYING:
            if (previousGameState == GAME_STATE_WORLD_MAP) {
                // 从世界地图进入游戏，初始化关卡
                initLevel(levelManager.currentLevel);
            }
            break;
            
        case GAME_STATE_GAME_OVER:
            initGameOverScreen();
            break;
            
        case GAME_STATE_WORLD_MAP:
            initWorldMap();
            break;
    }
}