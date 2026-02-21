// 创建状态管理器实例
const gameStateManager = new GameStateManager(4);

// 更新游戏状态
gameStateManager.updateBoard([
  [2, 2, 0, 0],
  [0, 0, 0, 0],
  [0, 0, 0, 0],
  [0, 0, 0, 0]
]);

// 更新分数
gameStateManager.updateScore(100);

// 获取当前状态
const currentState = gameStateManager.getGameState();
console.log('Current game state:', currentState);

// 获取统计数据
const stats = gameStateManager.getGameStats();
console.log('Game statistics:', stats);

// 导出游戏数据
const exportedData = gameStateManager.exportGameData();
console.log('Exported game data:', exportedData);

// 导入游戏数据
const importSuccess = gameStateManager.importGameData(exportedData);
console.log('Import success:', importSuccess);

// 重置游戏
gameStateManager.resetGame();

// 清除所有数据
// gameStateManager.clearAllData();