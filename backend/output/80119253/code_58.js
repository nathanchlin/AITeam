class Gomoku {
  constructor() {
    // ... 其他初始化代码 ...
    this.gameHistory = []; // 存储所有游戏记录
    this.currentGameRecord = {
      date: new Date().toISOString(),
      moves: [],
      result: null,
      duration: 0
    };
    this.gameStartTime = null;
  }

  // 开始新游戏时初始化记录
  startNewGame() {
    this.currentGameRecord = {
      date: new Date().toISOString(),
      moves: [],
      result: null,
      duration: 0
    };
    this.gameStartTime = Date.now();
    this.moveHistory = [];
  }

  // 在落子时记录到历史
  makeMove(row, col) {
    // ... 原有代码 ...
    
    // 记录到当前游戏记录
    this.currentGameRecord.moves.push({
      moveNumber: this.moveHistory.length,
      player: this.currentPlayer,
      row,
      col,
      timestamp: Date.now() - this.gameStartTime
    });
    
    return true;
  }

  // 游戏结束时保存记录
  endGame(winner) {
    this.currentGameRecord.result = winner ? `${winner} 胜利` : '平局';
    this.currentGameRecord.duration = Date.now() - this.gameStartTime;
    this.gameHistory.push({...this.currentGameRecord});
    
    // 保存到本地存储
    this.saveHistoryToLocalStorage();
  }

  // 保存历史记录到本地存储
  saveHistoryToLocalStorage() {
    try {
      localStorage.setItem('gomokuGameHistory', JSON.stringify(this.gameHistory));
    } catch (e) {
      console.error('保存游戏历史失败:', e);
    }
  }

  // 从本地存储加载历史记录
  loadHistoryFromLocalStorage() {
    try {
      const history = localStorage.getItem('gomokuGameHistory');
      if (history) {
        this.gameHistory = JSON.parse(history);
      }
    } catch (e) {
      console.error('加载游戏历史失败:', e);
    }
  }

  // 获取游戏历史统计
  getGameStatistics() {
    const stats = {
      totalGames: this.gameHistory.length,
      wins: { black: 0, white: 0, draw: 0 },
      averageDuration: 0,
      mostCommonOpening: {}
    };
    
    let totalDuration = 0;
    
    this.gameHistory.forEach(game => {
      if (game.result.includes('黑')) stats.wins.black++;
      else if (game.result.includes('白')) stats.wins.white++;
      else stats.wins.draw++;
      
      totalDuration += game.duration;
      
      // 分析开局
      if (game.moves.length > 1) {
        const opening = `${game.moves[0].row},${game.moves[0].col}-${game.moves[1].row},${game.moves[1].col}`;
        stats.mostCommonOpening[opening] = (stats.mostCommonOpening[opening] || 0) + 1;
      }
    });
    
    stats.averageDuration = totalDuration / this.gameHistory.length;
    
    return stats;
  }
}