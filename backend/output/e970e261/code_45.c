// 暂停游戏
void pauseGame() {
    if (currentGameState == GAME_STATE_PLAYING) {
        changeGameState(GAME_STATE_PAUSED);
    }
}

// 继续游戏
void resumeGame() {
    if (currentGameState == GAME_STATE_PAUSED) {
        changeGameState(GAME_STATE_PLAYING);
    }
}

// 游戏结束
void gameOver() {
    changeGameState(GAME_STATE_GAME_OVER);
}

// 重新开始当前关卡
void restartLevel() {
    loadLevel(levelManager.currentLevel.worldNumber, 
              levelManager.currentLevel.levelNumber);
}