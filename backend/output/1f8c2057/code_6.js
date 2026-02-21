import { GAME_CONFIG, DIRECTIONS } from './constants';

export const generateFood = (snake, gridSize) => {
  let newFood;
  do {
    newFood = {
      x: Math.floor(Math.random() * gridSize),
      y: Math.floor(Math.random() * gridSize),
    };
  } while (snake.some(segment => segment.x === newFood.x && segment.y === newFood.y));
  
  return newFood;
};

export const moveSnake = (snake, direction) => {
  const head = { ...snake[0] };
  
  switch (direction) {
    case DIRECTIONS.UP:
      head.y -= 1;
      break;
    case DIRECTIONS.DOWN:
      head.y += 1;
      break;
    case DIRECTIONS.LEFT:
      head.x -= 1;
      break;
    case DIRECTIONS.RIGHT:
      head.x += 1;
      break;
    default:
      break;
  }
  
  const newSnake = [head, ...snake.slice(0, -1)];
  return newSnake;
};

export const checkCollision = (snake, gridSize) => {
  const head = snake[0];
  
  // Wall collision
  if (
    head.x < 0 || 
    head.x >= gridSize || 
    head.y < 0 || 
    head.y >= gridSize
  ) {
    return true;
  }
  
  // Self collision
  for (let i = 1; i < snake.length; i++) {
    if (head.x === snake[i].x && head.y === snake[i].y) {
      return true;
    }
  }
  
  return false;
};

export const checkFoodCollision = (snake, food) => {
  const head = snake[0];
  return head.x === food.x && head.y === food.y;
};

export const growSnake = (snake) => {
  const tail = { ...snake[snake.length - 1] };
  return [...snake, tail];
};