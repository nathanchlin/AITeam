{
  type: 'gameState', // 'playerMove', 'aiAction', 'gameEvent'
  timestamp: Date.now(),
  data: {
    // 根据消息类型包含不同数据
    move: { direction: 'left', rotation: false }, // 玩家移动
    action: { position: { x: 4, y: 18 }, rotation: 1 }, // AI行动
    event: { type: 'lineClear', lines: 2, garbageLines: 1 } // 游戏事件
  }
}