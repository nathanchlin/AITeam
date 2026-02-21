import React from 'react';
import './App.css';
import GameCanvas from './components/GameCanvas';
import GameControls from './components/GameControls';
import ScoreBoard from './components/ScoreBoard';
import useSnakeGame from './hooks/useSnakeGame';
import { GAME_CONFIG } from './utils/constants';

function App() {
  const {
    snake,
    food,
    direction,
    gameOver,
    score,
    highScore,
    startGame,
    pauseGame,
    resumeGame,
    resetGame,
    changeDirection,
    gameSpeed
  } = useSnakeGame(GAME_CONFIG);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Snake Game</h1>
      </header>
      
      <main className="app-main">
        <div className="game-area">
          <GameCanvas 
            snake={snake}
            food={food}
            gameOver={gameOver}
            gameSpeed={gameSpeed}
          />
          
          <div className="game-overlay">
            {gameOver && (
              <div className="game-over">
                <h2>Game Over!</h2>
                <p>Final Score: {score}</p>
                <button onClick={resetGame} className="btn btn-primary">
                  Play Again
                </button>
              </div>
            )}
          </div>
        </div>
        
        <div className="game-sidebar">
          <ScoreBoard score={score} highScore={highScore} />
          <GameControls 
            gameStatus={gameOver ? 'gameOver' : 'idle'}
            onStart={startGame}
            onPause={pauseGame}
            onResume={resumeGame}
            onReset={resetGame}
            onDirectionChange={changeDirection}
          />
        </div>
      </main>
      
      <footer className="app-footer">
        <p>Use arrow keys to control the snake</p>
      </footer>
    </div>
  );
}

export default App;