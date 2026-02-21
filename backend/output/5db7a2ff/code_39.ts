interface GameState {
  board: number[][];       // 游戏棋盘状态
  score: number;           // 当前分数
  highestScore: number;    // 历史最高分
  gridSize: number;        // 棋盘大小 (如4x4)
  lastMoveTime: Date;      // 最后移动时间
  gameStatus: 'playing' | 'won' | 'lost'; // 游戏状态
}

interface GameStats {
  gamesPlayed: number;     // 游戏总场次
  gamesWon: number;        // 获胜场次
  totalScore: number;      // 累计分数
  averageScore: number;    // 平均分数
  longestWinStreak: number; // 最长连胜
  currentWinStreak: number; // 当前连胜
}