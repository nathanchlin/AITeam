const GameState = {
    MENU: 'menu',
    PLAYING: 'playing',
    PAUSED: 'paused',
    GAME_OVER: 'game_over',
    LEVEL_COMPLETE: 'level_complete'
};

class GameManager {
    constructor() {
        this.currentState = GameState.MENU;
        this.score = 0;
        this.lives = 3;
        this.currentLevel = 1;
    }
    
    changeState(newState) {
        this.currentState = newState;
        // 处理状态转换逻辑
    }
    
    // 其他管理方法...
}