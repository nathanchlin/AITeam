// 历史记录面板
const historyPanel = document.createElement('div');
historyPanel.className = 'history-panel';
historyPanel.innerHTML = `
  <h3>游戏历史</h3>
  <div class="history-list"></div>
`;
document.querySelector('.control-panel').appendChild(historyPanel);

// 添加历史记录
function addToHistory(move) {
  const historyItem = document.createElement('div');
  historyItem.className = 'history-item';
  historyItem.textContent = `第${move.step}步: ${move.player} (${move.row},${move.col})`;
  document.querySelector('.history-list').appendChild(historyItem);
  
  // 滚动到最新记录
  historyItem.scrollIntoView({ behavior: 'smooth' });
}