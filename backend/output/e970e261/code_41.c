// 关卡数据结构
typedef struct {
    int levelNumber;
    int worldNumber;
    int timeLimit;
    int coinCount;
    int enemyCount;
    char* levelData; // 关卡数据
} Level;

// 关卡管理器
typedef struct {
    Level currentLevel;
    Level nextLevel;
    int transitionTimer;
    int transitionType; // 0=淡出, 1=滑动, 2=缩放
    int isTransitioning;
} LevelManager;

LevelManager levelManager;

// 初始化关卡管理器
void initLevelManager() {
    levelManager.transitionTimer = 0;
    levelManager.transitionType = 0;
    levelManager.isTransitioning = 0;
}

// 加载新关卡
void loadLevel(int world, int level) {
    // 保存当前状态用于过渡
    levelManager.nextLevel = loadLevelData(world, level);
    
    // 开始过渡
    levelManager.isTransitioning = 1;
    levelManager.transitionTimer = 30; // 0.5秒过渡时间 (60fps)
    levelManager.transitionType = 0; // 使用淡出效果
    
    // 设置游戏状态为过渡中
    currentGameState = GAME_STATE_LEVEL_COMPLETE;
}

// 更新关卡过渡
void updateLevelTransition() {
    if (levelManager.isTransitioning) {
        levelManager.transitionTimer--;
        
        if (levelManager.transitionTimer <= 0) {
            // 过渡完成，加载新关卡
            levelManager.currentLevel = levelManager.nextLevel;
            levelManager.isTransitioning = 0;
            
            // 重置玩家位置和状态
            resetPlayer();
            
            // 返回游戏状态
            currentGameState = GAME_STATE_PLAYING;
        }
    }
}

// 渲染关卡过渡效果
void renderLevelTransition() {
    if (levelManager.isTransitioning) {
        // 计算透明度 (0-255)
        int alpha = (levelManager.transitionTimer * 255) / 30;
        
        // 根据过渡类型渲染
        switch (levelManager.transitionType) {
            case 0: // 淡出效果
                renderWithAlpha(alpha);
                break;
                
            case 1: // 滑动效果
                renderSlideTransition(levelManager.transitionTimer);
                break;
                
            case 2: // 缩放效果
                renderZoomTransition(levelManager.transitionTimer);
                break;
        }
    }
}