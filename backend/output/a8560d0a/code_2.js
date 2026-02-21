class GameState {
  constructor() {
    this.currentLevel = 1;
    this.score = 0;
    this.playerHealth = 100;
    this.enemyHealth = 100;
    this.gameStatus = 'MENU'; // MENU, PLAYING, PAUSED, GAME_OVER
    this.entities = []; // 所有游戏实体
    this.keys = {}; // 按键状态
  }
  
  update() {
    // 更新游戏状态
  }
  
  render() {
    // 渲染游戏画面
  }
}