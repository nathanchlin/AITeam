class ScoreSystem {
  constructor() {
    this.currentScore = 0;
    this.highScore = this.loadHighScore();
    this.scoreElement = null;
    this.highScoreElement = null;
  }

  /**
   * 初始化计分系统，创建显示元素
   * @param {HTMLElement} container - 计分显示容器
   */
  init(container) {
    // 创建分数显示容器
    const scoreContainer = document.createElement('div');
    scoreContainer.style.position = 'absolute';
    scoreContainer.style.top = '20px';
    scoreContainer.style.left = '20px';
    scoreContainer.style.color = 'white';
    scoreContainer.style.fontSize = '24px';
    scoreContainer.style.fontFamily = 'Arial, sans-serif';
    scoreContainer.style.textShadow = '2px 2px 4px rgba(0, 0, 0, 0.5)';
    scoreContainer.style.zIndex = '100';
    
    // 创建当前分数显示
    this.scoreElement = document.createElement('div');
    this.scoreElement.textContent = `Score: ${this.currentScore}`;
    this.scoreElement.style.marginBottom = '10px';
    
    // 创建最高分显示
    this.highScoreElement = document.createElement('div');
    this.highScoreElement.textContent = `High Score: ${this.highScore}`;
    
    scoreContainer.appendChild(this.scoreElement);
    scoreContainer.appendChild(this.highScoreElement);
    container.appendChild(scoreContainer);
  }

  /**
   * 增加分数
   */
  increaseScore() {
    this.currentScore++;
    this.updateScoreDisplay();
    
    // 检查是否创造新纪录
    if (this.currentScore > this.highScore) {
      this.highScore = this.currentScore;
      this.saveHighScore();
      this.updateHighScoreDisplay();
    }
  }

  /**
   * 重置当前分数
   */
  resetScore() {
    this.currentScore = 0;
    this.updateScoreDisplay();
  }

  /**
   * 更新分数显示
   */
  updateScoreDisplay() {
    if (this.scoreElement) {
      this.scoreElement.textContent = `Score: ${this.currentScore}`;
    }
  }

  /**
   * 更新最高分显示
   */
  updateHighScoreDisplay() {
    if (this.highScoreElement) {
      this.highScoreElement.textContent = `High Score: ${this.highScore}`;
    }
  }

  /**
   * 从 localStorage 加载最高分
   * @returns {number} 最高分
   */
  loadHighScore() {
    try {
      const savedScore = localStorage.getItem('flappyBirdHighScore');
      return savedScore ? parseInt(savedScore, 10) : 0;
    } catch (error) {
      console.error('Error loading high score:', error);
      return 0;
    }
  }

  /**
   * 保存最高分到 localStorage
   */
  saveHighScore() {
    try {
      localStorage.setItem('flappyBirdHighScore', this.highScore.toString());
    } catch (error) {
      console.error('Error saving high score:', error);
    }
  }
}

// 使用示例
// const scoreSystem = new ScoreSystem();
// scoreSystem.init(gameContainer); // 将计分系统添加到游戏容器中
// scoreSystem.increaseScore(); // 当玩家通过一组管道时调用