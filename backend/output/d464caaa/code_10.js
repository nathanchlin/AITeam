{
  playerBoard: {
    grid: Array(20).fill(Array(10).fill(0)), // 20x10游戏网格
    currentPiece: {
      type: 'I', // 方块类型
      rotation: 0, // 旋转状态
      position: { x: 3, y: 0 } // 位置坐标
    },
    nextPiece: 'J', // 下一个方块
    score: 0,
    level: 1,
    lines: 0,
    isGameOver: false
  },
  aiBoard: {
    // 同playerBoard结构
  },
  gameStatus: 'playing', // 'waiting', 'playing', 'paused', 'gameOver'
  lastMoveTime: Date.now(),
  speed: 1000 // 方块下落间隔(毫秒)
}