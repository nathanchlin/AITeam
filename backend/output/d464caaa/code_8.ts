interface AIController {
  // 初始化
  initialize(difficulty: Difficulty): void;
  
  // 决策
  makeDecision(gameState: GameState): AIAction;
  
  // 策略调整
  setStrategy(strategy: AIStrategy): void;
  adjustDifficulty(newDifficulty: Difficulty): void;
}

interface AIAction {
  type: 'move' | 'rotate' | 'drop' | 'hardDrop';
  direction?: Direction;
  clockwise?: boolean;
  delay: number; // 执行延迟(毫秒)
}