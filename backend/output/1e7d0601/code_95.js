// game.js
class GameState {
    constructor() {
        this.states = {
            MENU: 'menu',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over',
            LEVEL_COMPLETE: 'level_complete'
        };
        this.currentState = this.states.MENU;
        this.score = 0;
        this.lives = 3;
        this.level = 1;
        this.highScore = 0;
    }
    
    setState(newState) {
        this.currentState = newState;
        // 触发状态变化事件
        document.dispatchEvent(new CustomEvent('gameStateChanged', { 
            detail: { state: newState } 
        }));
    }
    
    reset() {
        this.score = 0;
        this.lives = 3;
        this.level = 1;
    }
}

// 全局游戏状态
const gameState = new GameState();