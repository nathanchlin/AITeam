// 初始化游戏
const game = new Gomoku();
game.loadHistoryFromLocalStorage();

// 显示历史记录函数
function showGameHistory() {
  const historyPanel = document.getElementById('historyPanel');
  const historyList = document.getElementById('historyList');
  
  historyList.innerHTML = '';
  
  game.gameHistory.slice().reverse().forEach((gameRecord, index) => {
    const gameDiv = document.createElement('div');
    gameDiv.className = 'game-record';
    gameDiv.innerHTML = `
      <h4>游戏 ${game.gameHistory.length - index} - ${new Date(gameRecord.date).toLocaleString()}</h4>
      <p>结果: ${gameRecord.result} | 时长: ${formatDuration(gameRecord.duration)}</p>
      <button onclick="replayGame(${game.gameHistory.length - 1})">回放</button>
    `;
    historyList.appendChild(gameDiv);
  });
  
  historyPanel.style.display = historyPanel.style.display === 'none' ? 'block' : 'none';
}

// 显示统计信息函数
function showGameStatistics() {
  const statsPanel = document.getElementById('statsPanel');
  const statsContent = document.getElementById('statsContent');
  const stats = game.getGameStatistics();
  
  statsContent.innerHTML = `
    <p>总游戏数: ${stats.totalGames}</p>
    <p>黑棋胜利: ${stats.wins.black}</p>
    <p>白棋胜利: ${stats.wins.white}</p>
    <p>平局: ${stats.wins.draw}</p>
    <p>平均游戏时长: ${formatDuration(stats.averageDuration)}</p>
    <p>最常见开局: ${getMostCommonOpening(stats.mostCommonOpening)}</p>
  `;
  
  statsPanel.style.display = statsPanel.style.display === 'none' ? 'block' : 'none';
}

// 辅助函数
function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  return `${minutes}分${seconds % 60}秒`;
}

function getMostCommonOpening(openings) {
  let mostCommon = '';
  let maxCount = 0;
  
  for (const [opening, count] of Object.entries(openings)) {
    if (count > maxCount) {
      mostCommon = opening;
      maxCount = count;
    }
  }
  
  return maxCount > 0 ? `${mostCommon} (${maxCount}次)` : '数据不足';
}