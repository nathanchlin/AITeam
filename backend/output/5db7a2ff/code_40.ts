class GameStateManager {
  private readonly STORAGE_KEY = '2046GameState';
  private readonly STATS_KEY = '2046GameStats';
  private gameState: GameState;
  private gameStats: GameStats;

  constructor(gridSize: number = 4) {
    this.initializeGameState(gridSize);
    this.initializeGameStats();
    this.loadFromStorage();
  }

  // 初始化游戏状态
  private initializeGameState(gridSize: number) {
    this.gameState = {
      board: Array(gridSize).fill(null).map(() => Array(gridSize).fill(0)),
      score: 0,
      highestScore: 0,
      gridSize,
      lastMoveTime: new Date(),
      gameStatus: 'playing'
    };
  }

  // 初始化游戏统计数据
  private initializeGameStats() {
    this.gameStats = {
      gamesPlayed: 0,
      gamesWon: 0,
      totalScore: 0,
      averageScore: 0,
      longestWinStreak: 0,
      currentWinStreak: 0
    };
  }

  // 从本地存储加载数据
  private loadFromStorage() {
    try {
      const savedState = localStorage.getItem(this.STORAGE_KEY);
      const savedStats = localStorage.getItem(this.STATS_KEY);
      
      if (savedState) {
        this.gameState = JSON.parse(savedState);
      }
      
      if (savedStats) {
        this.gameStats = JSON.parse(savedStats);
      }
    } catch (error) {
      console.error('Failed to load game state from storage:', error);
    }
  }

  // 保存数据到本地存储
  private saveToStorage() {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.gameState));
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.gameStats));
    } catch (error) {
      console.error('Failed to save game state to storage:', error);
    }
  }

  // 更新棋盘状态
  updateBoard(newBoard: number[][]) {
    this.gameState.board = newBoard;
    this.gameState.lastMoveTime = new Date();
    this.saveToStorage();
  }

  // 更新分数
  updateScore(newScore: number) {
    this.gameState.score = newScore;
    
    // 更新最高分
    if (newScore > this.gameState.highestScore) {
      this.gameState.highestScore = newScore;
    }
    
    this.saveToStorage();
  }

  // 设置游戏状态
  setGameStatus(status: 'playing' | 'won' | 'lost') {
    const previousStatus = this.gameState.gameStatus;
    this.gameState.gameStatus = status;
    
    // 更新统计数据
    if (previousStatus !== 'playing' && status === 'playing') {
      // 新游戏开始
      this.gameStats.gamesPlayed++;
      if (previousStatus === 'won') {
        this.gameStats.currentWinStreak++;
        if (this.gameStats.currentWinStreak > this.gameStats.longestWinStreak) {
          this.gameStats.longestWinStreak = this.gameStats.currentWinStreak;
        }
      } else {
        this.gameStats.currentWinStreak = 0;
      }
    } else if (previousStatus === 'playing' && status === 'won') {
      // 游戏胜利
      this.gameStats.gamesWon++;
      this.gameStats.totalScore += this.gameState.score;
      this.gameStats.averageScore = this.gameStats.totalScore / this.gameStats.gamesPlayed;
    }
    
    this.saveToStorage();
  }

  // 重置当前游戏
  resetGame() {
    this.initializeGameState(this.gameState.gridSize);
    this.saveToStorage();
  }

  // 获取当前游戏状态
  getGameState(): GameState {
    return { ...this.gameState };
  }

  // 获取游戏统计数据
  getGameStats(): GameStats {
    return { ...this.gameStats };
  }

  // 导出游戏数据
  exportGameData(): string {
    return JSON.stringify({
      gameState: this.gameState,
      gameStats: this.gameStats,
      exportDate: new Date().toISOString()
    });
  }

  // 导入游戏数据
  importGameData(data: string): boolean {
    try {
      const imported = JSON.parse(data);
      if (imported.gameState && imported.gameStats) {
        this.gameState = imported.gameState;
        this.gameStats = imported.gameStats;
        this.saveToStorage();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to import game data:', error);
      return false;
    }
  }

  // 清除所有保存的数据
  clearAllData() {
    localStorage.removeItem(this.STORAGE_KEY);
    localStorage.removeItem(this.STATS_KEY);
    this.initializeGameState(this.gameState.gridSize);
    this.initializeGameStats();
  }
}