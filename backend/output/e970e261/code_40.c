void gameLoop() {
    // 初始化游戏
    initGame();
    
    while (1) {
        // 处理输入
        handleInput();
        
        // 根据当前状态更新游戏逻辑
        switch (currentGameState) {
            case GAME_STATE_TITLE:
                updateTitleScreen();
                break;
                
            case GAME_STATE_PLAYING:
                updateGame();
                break;
                
            case GAME_STATE_PAUSED:
                updatePauseScreen();
                break;
                
            case GAME_STATE_GAME_OVER:
                updateGameOverScreen();
                break;
                
            case GAME_STATE_LEVEL_COMPLETE:
                updateLevelCompleteScreen();
                break;
                
            case GAME_STATE_WORLD_MAP:
                updateWorldMap();
                break;
                
            case GAME_STATE_CUTSCENE:
                updateCutscene();
                break;
        }
        
        // 渲染当前状态
        render();
        
        // 简单的帧率控制
        waitFrame();
    }
}