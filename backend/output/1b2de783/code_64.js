// 实现平滑的难度曲线
class DifficultyManager {
  constructor() {
    this.baseSpawnRate = 2000; // 基础生成间隔(毫秒)
    this.baseEnemySpeed = 2;
    this.currentLevel = 1;
    this.scoreThreshold = 1000;
    this.lastScoreIncrease = 0;
  }
  
  updateDifficulty(currentScore) {
    // 计算当前等级
    const newLevel = Math.floor(currentScore / this.scoreThreshold) + 1;
    
    if (newLevel > this.currentLevel) {
      this.currentLevel = newLevel;
      this.adjustDifficulty();
    }
  }
  
  adjustDifficulty() {
    // 使用指数平滑函数调整难度
    const difficultyFactor = Math.log(this.currentLevel) / Math.log(2);
    
    // 调整生成速率
    this.spawnRate = Math.max(500, this.baseSpawnRate / difficultyFactor);
    
    // 调整敌人速度
    this.enemySpeed = Math.min(8, this.baseEnemySpeed * difficultyFactor);
    
    // 调整敌人生命值
    this.enemyHealth = Math.min(5, Math.floor(difficultyFactor / 2) + 1);
  }
  
  getSpawnRate() {
    return this.spawnRate;
  }
  
  getEnemySpeed() {
    return this.enemySpeed;
  }
  
  getEnemyHealth() {
    return this.enemyHealth;
  }
}