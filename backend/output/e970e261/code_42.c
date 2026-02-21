void checkLevelComplete() {
    // 检查是否到达终点旗杆
    if (player.reachedFlag) {
        // 增加分数和统计
        updateScore();
        saveStats();
        
        // 准备下一关
        int nextLevel = levelManager.currentLevel.levelNumber + 1;
        
        // 如果是关卡的最后一关
        if (nextLevel > 4) { // 假设每世界4关
            // 进入世界地图
            currentGameState = GAME_STATE_WORLD_MAP;
        } else {
            // 加载下一关
            loadLevel(levelManager.currentLevel.worldNumber, nextLevel);
        }
    }
}