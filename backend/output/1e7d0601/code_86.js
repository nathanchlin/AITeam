// 难度管理系统
class DifficultyManager {
  constructor(game) {
    this.game = game;
    this.currentLevel = 1;
    this.scoreThreshold = 5000;
    this.difficultyCurve = {
      enemySpeed: 1.0,
      enemyHealth: 1.0,
      spawnRate: 1.0
    };
  }
  
  update() {
    // 根据分数调整难度
    const scoreLevel = Math.floor(this.game.score / this.scoreThreshold);
    if (scoreLevel > this.currentLevel) {
      this.currentLevel = scoreLevel;
      this.adjustDifficulty();
    }
  }
  
  adjustDifficulty() {
    // 平滑调整难度参数
    this.difficultyCurve.enemySpeed = 1.0 + (this.currentLevel - 1) * 0.1;
    this.difficultyCurve.enemyHealth = 1.0 + (this.currentLevel - 1) * 0.15;
    this.difficultyCurve.spawnRate = Math.max(0.5, 1.0 - (this.currentLevel - 1) * 0.05);
    
    // 应用新难度
    this.game.enemyManager.updateDifficulty(this.difficultyCurve);
    
    // 显示难度提升提示
    this.game.ui.addComboEffect(`LEVEL ${this.currentLevel}`);
  }
}