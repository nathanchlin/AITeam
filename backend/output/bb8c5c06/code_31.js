// 游戏配置
const GRID_SIZE = 20;
const CELL_SIZE = 20;
const GAME_SPEED = 150;
const INITIAL_SPEED = 150;
const SPEED_INCREMENT = 5;

// 游戏状态
let gameRunning = false;
let score = 0;
let gameSpeed = INITIAL_SPEED;

// 获取DOM元素
const gameBoard = document.getElementById('game-board');
const scoreElement = document.getElementById('score');
const gameOverElement = document.getElementById('game-over');
const restartButton = document.getElementById('restart');

// 蛇类定义
class Snake {
  constructor() {
    this.body = [{x: 10, y: 10}];
    this.direction = {x: 1, y: 0};
    this.nextDirection = {x: 1, y: 0};
    this.growing = false;
  }
  
  getBody() {
    return this.body;
  }
  
  getHead() {
    return this.body[0];
  }
  
  setDirection(newDirection) {
    // 防止蛇直接掉头
    if (this.body.length > 1) {
      if (newDirection.x === -this.direction.x && newDirection.y === -this.direction.y) {
        return;
      }
    }
    this.nextDirection = newDirection;
  }
  
  move() {
    // 更新方向
    this.direction = {...this.nextDirection};
    
    // 计算新头部位置
    const head = this.getHead();
    const newHead = {
      x: head.x + this.direction.x,
      y: head.y + this.direction.y
    };
    
    // 添加新头部
    this.body.unshift(newHead);
    
    // 如果没有增长，移除尾部
    if (!this.growing) {
      this.body.pop();
    } else {
      this.growing = false;
    }
  }
  
  grow() {
    this.growing = true;
  }
  
  checkCollision() {
    const head = this.getHead();
    
    // 检查是否撞墙
    if (head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE) {
      return true;
    }
    
    // 检查是否撞到自己
    for (let i = 1; i < this.body.length; i++) {
      if (head.x === this.body[i].x && head.y === this.body[i].y) {
        return true;
      }
    }
    
    return false;
  }
  
  checkFoodCollision(food) {
    const head = this.getHead();
    return head.x === food.x && head.y === food.y;
  }
}

// 食物类
class Food {
  constructor() {
    this.position = this.generateRandomPosition();
  }
  
  generateRandomPosition() {
    let newFood;
    do {
      newFood = {
        x: Math.floor(Math.random() * GRID_SIZE),
        y: Math.floor(Math.random() * GRID_SIZE)
      };
      // 确保食物不会生成在蛇身上
    } while (snake.getBody().some(segment => segment.x === newFood.x && segment.y === newFood.y));
    
    return newFood;
  }
  
  getPosition() {
    return this.position;
  }
  
  respawn() {
    this.position = this.generateRandomPosition();
  }
}

// 游戏对象
let snake;
let food;

// 初始化游戏
function initGame() {
  snake = new Snake();
  food = new Food();
  score = 0;
  gameSpeed = INITIAL_SPEED;
  scoreElement.textContent = `得分: ${score}`;
  gameOverElement.style.display = 'none';
  gameRunning = true;
}

// 渲染游戏
function render() {
  // 清空游戏板
  gameBoard.innerHTML = '';
  
  // 渲染蛇
  snake.getBody().forEach((segment, index) => {
    const snakeElement = document.createElement('div');
    snakeElement.style.width = `${CELL_SIZE}px`;
    snakeElement.style.height = `${CELL_SIZE}px`;
    snakeElement.style.position = 'absolute';
    snakeElement.style.left = `${segment.x * CELL_SIZE}px`;
    snakeElement.style.top = `${segment.y * CELL_SIZE}px`;
    
    // 蛇头使用不同颜色
    if (index === 0) {
      snakeElement.style.backgroundColor = 'darkgreen';
    } else {
      snakeElement.style.backgroundColor = 'green';
    }
    
    gameBoard.appendChild(snakeElement);
  });
  
  // 渲染食物
  const foodElement = document.createElement('div');
  foodElement.style.width = `${CELL_SIZE}px`;
  foodElement.style.height = `${CELL_SIZE}px`;
  foodElement.style.position = 'absolute';
  foodElement.style.left = `${food.getPosition().x * CELL_SIZE}px`;
  foodElement.style.top = `${food.getPosition().y * CELL_SIZE}px`;
  foodElement.style.backgroundColor = 'red';
  foodElement.style.borderRadius = '50%';
  gameBoard.appendChild(foodElement);
}

// 游戏主循环
function gameLoop() {
  if (!gameRunning) return;
  
  // 移动蛇
  snake.move();
  
  // 检查碰撞
  if (snake.checkCollision()) {
    gameOver();
    return;
  }
  
  // 检查是否吃到食物
  if (snake.checkFoodCollision(food)) {
    score++;
    scoreElement.textContent = `得分: ${score}`;
    snake.grow();
    food.respawn();
    
    // 增加游戏难度
    if (score % 5 === 0) {
      gameSpeed = Math.max(50, gameSpeed - SPEED_INCREMENT);
    }
  }
  
  // 渲染游戏
  render();
  
  // 继续游戏循环
  setTimeout(gameLoop, gameSpeed);
}

// 游戏结束
function gameOver() {
  gameRunning = false;
  gameOverElement.style.display = 'block';
  gameOverElement.textContent = `游戏结束! 最终得分: ${score}`;
}

// 键盘事件处理
document.addEventListener('keydown', (e) => {
  if (!gameRunning) return;
  
  switch(e.key) {
    case 'ArrowUp':
      snake.setDirection({x: 0, y: -1});
      break;
    case 'ArrowDown':
      snake.setDirection({x: 0, y: 1});
      break;
    case 'ArrowLeft':
      snake.setDirection({x: -1, y: 0});
      break;
    case 'ArrowRight':
      snake.setDirection({x: 1, y: 0});
      break;
  }
  
  // 防止方向键滚动页面
  e.preventDefault();
});

// 重新开始按钮
restartButton.addEventListener('click', () => {
  initGame();
  gameLoop();
});

// 页面加载时初始化游戏
window.addEventListener('load', () => {
  // 设置游戏板大小
  gameBoard.style.width = `${GRID_SIZE * CELL_SIZE}px`;
  gameBoard.style.height = `${GRID_SIZE * CELL_SIZE}px`;
  gameBoard.style.position = 'relative';
  gameBoard.style.border = '2px solid #333';
  
  // 初始化并开始游戏
  initGame();
  gameLoop();
});