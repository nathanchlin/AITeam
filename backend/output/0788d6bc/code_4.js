// 建议监控的游戏指标
gameMetrics = {
  playerDeaths: {
    byCause: ["enemyBullet", "collision", "outOfBounds"],
    perLevel: []
  },
  enemyKills: {
    perMinute: [],
    accuracy: []
  },
  timeSpent: {
    perLevel: [],
    averageSession: 0
  },
  playerActions: {
    shotsFired: 0,
    shotsHit: 0,
    movements: 0
  }
}