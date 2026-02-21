// 游戏主组件
const Game2046UI: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>(initialState);
  
  useEffect(() => {
    const game = new Game2046();
    // 初始化游戏和事件监听
    return () => game.cleanup();
  }, []);
  
  return (
    <div className="game-container">
      <ScoreDisplay score={gameState.score} />
      <GameBoard board={gameState.board} />
      <GameOverOverlay visible={gameState.gameOver} />
    </div>
  );
};

// 游戏板组件
const GameBoard: React.FC<{board: number[][]}> = ({ board }) => {
  return (
    <div className="game-board">
      {board.map((row, y) => 
        row.map((value, x) => (
          <Tile key={`${x}-${y}`} value={value} />
        ))
      )}
    </div>
  );
};