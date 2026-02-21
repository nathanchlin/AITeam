interface GameClient {
  // 连接管理
  connect(serverUrl: string): Promise<void>;
  disconnect(): void;
  
  // 游戏控制
  startGame(): void;
  pauseGame(): void;
  resumeGame(): void;
  endGame(): void;
  
  // 操作接口
  moveLeft(): void;
  moveRight(): void;
  rotate(): void;
  drop(): void;
  hardDrop(): void;
  
  // 状态查询
  getGameState(): GameState;
  getOpponentState(): GameState;
}

interface GameServer {
  // 玩家管理
  registerPlayer(playerId: string, playerName: string): void;
  unregisterPlayer(playerId: string): void;
  
  // 游戏匹配
  matchPlayers(playerId: string): Promise<string>; // 返回对手ID
  
  // 游戏状态同步
  updateGameState(playerId: string, state: GameState): void;
  broadcastGameState(gameId: string, state: GameState): void;
  
  // 攻击/防御
  sendAttack(gameId: string, attackerId: string, attackData: AttackData): void;
  receiveAttack(gameId: string, defenderId: string, attackData: AttackData): void;
}