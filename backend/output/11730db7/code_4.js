class LevelManager {
  constructor() {
    this.currentLevel = 1;
    this.levels = this.initializeLevels();
    this.objectives = this.getObjectivesForLevel(this.currentLevel);
  }
  
  initializeLevels() {
    return [
      {
        id: 1,
        gridSize: { width: 8, height: 8 },
        scoreTarget: 1000,
        moveLimit: 30,
        specialElements: []
      },
      {
        id: 2,
        gridSize: { width: 8, height: 8 },
        scoreTarget: 2000,
        moveLimit: 25,
        specialElements: ['bomb']
      },
      {
        id: 3,
        gridSize: { width: 9, height: 9 },
        scoreTarget: 3000,
        moveLimit: 20,
        specialElements: ['bomb', 'lightning']
      }
      // 可以添加更多关卡
    ];
  }
  
  getObjectivesForLevel(levelId) {
    const level = this.levels.find(l => l.id === levelId);
    if (!level) return null;
    
    return {
      scoreTarget: level.scoreTarget,
      moveLimit: level.moveLimit,
      specialElements: level.specialElements
    };
  }
  
  update() {
    // 检查是否完成当前关卡目标
    if (this.isLevelComplete()) {
      this.nextLevel();
    }
  }
  
  isLevelComplete() {
    // 检查是否达到目标分数
    if (this.gameState.score >= this.objectives.scoreTarget) {
      return true;
    }
    
    // 检查是否用完所有步数
    if (this.gameState.remainingMoves <= 0) {
      this.gameOver();
      return true;
    }
    
    return false;
  }
  
  nextLevel() {
    this.currentLevel++;
    this.objectives = this.getObjectivesForLevel(this.currentLevel);
    
    // 重置游戏状态
    this.gameState.reset();
    
    // 触发关卡切换事件
    const event = new CustomEvent('levelComplete', {
      detail: { level: this.currentLevel - 1 }
    });
    document.dispatchEvent(event);
  }
  
  gameOver() {
    // 触发游戏结束事件
    const event = new CustomEvent('gameOver', {
      detail: { level: this.currentLevel, score: this.gameState.score }
    });
    document.dispatchEvent(event);
  }
}