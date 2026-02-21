import { useState, useEffect, useCallback, useRef } from 'react';
import { GAME_STATES, GAME_CONFIG } from '../utils/constants';
import { 
  generateFood, 
  moveSnake, 
  checkCollision, 
  checkFoodCollision, 
  growSnake 
} from '../utils/gameLogic';

const useSnakeGame = (config) => {
  const [snake, setSnake] = useState([{ x: 10, y: 10 }]);
  const [food, setFood] = useState(generateFood([{ x: 10, y: 10 }], config.GRID_SIZE));
  const [direction, setDirection] = useState(null);
  const [gameState, setGameState] = useState(GAME_STATES.IDLE);
  const [score, setScore] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [gameSpeed, setGameSpeed] = useState(config.INITIAL_SPEED);
  
  const directionRef = useRef(direction);
  const gameStateRef = useRef(gameState);
  
  // Update refs when state changes
  directionRef.current = direction;
  gameStateRef.current = gameState;
  
  // Load high score from localStorage
  useEffect(() => {
    const savedHighScore = localStorage.getItem('snakeHighScore');
    if (savedHighScore) {
      setHighScore(parseInt(savedHighScore, 10));
    }
  }, []);
  
  // Save high score to localStorage
  useEffect(() => {
    if (score > highScore) {
      setHighScore(score);
      localStorage.setItem('snakeHighScore', score.toString());
    }
  }, [score, highScore]);
  
  // Handle keyboard input
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (gameStateRef.current === GAME_STATES.GAME_OVER) return;
      
      switch (e.key) {
        case 'ArrowUp':
          if (directionRef.current !== 'DOWN') {
            setDirection('UP');
          }
          break;
        case 'ArrowDown':
          if (directionRef.current !== 'UP') {
            setDirection('DOWN');
          }
          break;
        case 'ArrowLeft':
          if (directionRef.current !== 'RIGHT') {
            setDirection('LEFT');
          }
          break;
        case 'ArrowRight':
          if (directionRef.current !== 'LEFT') {
            setDirection('RIGHT');
          }
          break;
        case ' ':
          if (gameStateRef.current === GAME_STATES.RUNNING) {
            setGameState(GAME_STATES.PAUSED);
          } else if (gameStateRef.current === GAME_STATES.PAUSED) {
            setGameState(GAME_STATES.RUNNING);
          }
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);
  
  // Game loop
  useEffect(() => {
    if (gameState !== GAME_STATES.RUNNING) return;
    
    const gameLoop = setInterval(() => {
      setSnake(prevSnake => {
        const newSnake = moveSnake(prevSnake, directionRef.current);
        
        // Check for food collision
        if (checkFoodCollision(newSnake, food)) {
          setScore(prevScore => prevScore + 10);
          setFood(generateFood(newSnake, config.GRID_SIZE));
          
          // Grow snake
          const grownSnake = growSnake(newSnake);
          
          // Increase speed (with cap)
          if (gameSpeed > config.MAX_SPEED) {
            setGameSpeed(prevSpeed => prevSpeed - config.SPEED_INCREMENT);
          }
          
          return grownSnake;
        }
        
        return newSnake;
      });
    }, gameSpeed);
    
    return () => clearInterval(gameLoop);
  }, [gameState, food, gameSpeed, config]);
  
  // Check for collisions
  useEffect(() => {
    if (gameState !== GAME_STATES.RUNNING) return;
    
    if (checkCollision(snake, config.GRID_SIZE)) {
      setGameState(GAME_STATES.GAME_OVER);
    }
  }, [snake, gameState, config.GRID_SIZE]);
  
  const startGame = useCallback(() => {
    setSnake([{ x: 10, y: 10 }]);
    setFood(generateFood([{ x: 10, y: 10 }], config.GRID_SIZE));
    setDirection('RIGHT');
    setGameState(GAME_STATES.RUNNING);
    setScore(0);
    setGameSpeed(config.INITIAL_SPEED);
  }, [config]);
  
  const pauseGame = useCallback(() => {
    if (gameState === GAME_STATES.RUNNING) {
      setGameState(GAME_STATES.PAUSED);
    }
  }, [gameState]);
  
  const resumeGame = useCallback(() => {
    if (gameState === GAME_STATES.PAUSED) {
      setGameState(GAME_STATES.RUNNING);
    }
  }, [gameState]);
  
  const resetGame = useCallback(() => {
    setSnake([{ x: 10, y: 10 }]);
    setFood(generateFood([{ x: 10, y: 10 }], config.GRID_SIZE));
    setDirection(null);
    setGameState(GAME_STATES.IDLE);
    setScore(0);
    setGameSpeed(config.INITIAL_SPEED);
  }, [config]);
  
  const changeDirection = useCallback((newDirection) => {
    if (gameState === GAME_STATES.RUNNING) {
      // Prevent 180-degree turns
      if (
        (newDirection === 'UP' && directionRef.current !== 'DOWN') ||
        (newDirection === 'DOWN' && directionRef.current !== 'UP') ||
        (newDirection === 'LEFT' && directionRef.current !== 'RIGHT') ||
        (newDirection === 'RIGHT' && directionRef.current !== 'LEFT')
      ) {
        setDirection(newDirection);
      }
    }
  }, [gameState]);
  
  return {
    snake,
    food,
    direction,
    gameOver: gameState === GAME_STATES.GAME_OVER,
    gameState,
    score,
    highScore,
    gameSpeed,
    startGame,
    pauseGame,
    resumeGame,
    resetGame,
    changeDirection,
  };
};

export default useSnakeGame;