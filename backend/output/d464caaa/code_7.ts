interface GameEngine {
  // 初始化
  initialize(gameConfig: GameConfig): void;
  
  // 方块操作
  moveBlock(direction: Direction): boolean;
  rotateBlock(clockwise: boolean): boolean;
  dropBlock(): void;
  hardDropBlock(): void;
  
  // 游戏状态
  getGameState(): GameState;
  isGameOver(): boolean;
  
  // 行消除
  clearLines(): number; // 返回消除的行数
  
  // 攻击/防御
  receiveAttack(attackData: AttackData): void;
  generateAttack(): AttackData;
}

interface GameState {
  board: number[][]; // 游戏板状态
  currentBlock: Block;
  nextBlock: Block;
  score: number;
  level: number;
  lines: number;
  gameOver: boolean;
  opponentState: OpponentState;
}