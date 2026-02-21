// 游戏配置
const GRID_SIZE = 20;
const CELL_SIZE = 20;
const GAME_SPEED = 150;
const INITIAL_SPEED = 150;
const SPEED_INCREMENT = 5;

// 游戏元素
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const gameOverElement = document.getElementById('gameOver');
const restartButton = document.getElementById('restartButton');

// 游戏状态
let gameRunning = false;
let score = 0;
let currentSpeed = INITIAL_SPEED;
let food = {};
let snake;

// 设置画布大小
canvas.width = GRID_SIZE * CELL_SIZE;
canvas.height = GRID_SIZE * CELL_SIZE;

// 蛇类定义
class Snake {
  constructor() {
    this.body = [{x: Math.floor(GRID_SIZE/2), y: Math.floor(GRID_SIZE/2)}];
    this.direction = {x: 1, y: 0};
    this.nextDirection = {x: 1, y: 0};
  }
  
  // 获取蛇的身体
  getBody() {
    return this.body;
  }
  
  // 设置方向
  setDirection(newDirection) {
    // 防止蛇直接掉头
    if (this.direction.x + newDirection.x === 0 && this.direction.y + newDirection.y === 0) {
      return;
    }
    this.nextDirection = newDirection;
  }
  
  // 移动蛇
  move() {
    this.direction = {...this.nextDirection};
    
    const head = {...this.body[0]};
    head.x += this.direction.x;
    head.y += this.direction.y;
    
    this.body.unshift(head);
    
    // 如果没有吃到食物，移除尾部
    return false; // 返回false表示没有吃到食物
  }
  
  // 增长蛇
  grow() {
    // 不移除尾部，使蛇变长
    return true;
  }
  
  // 检查是否吃到食物
  checkFoodCollision(food) {
    const head = this.body[0];
    return head.x === food.x && head.y === food.y;
  }
  
  // 检查是否撞墙
  checkWallCollision() {
    const head = this.body[0];
    return head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE;
  }
  
  // 检查是否撞到自己
  checkSelfCollision() {
    const head = this.body[0];
    for (let i = 1; i < this.body.length; i++) {
      if (head.x === this.body[i].x && head.y === this.body[i].y) {
        return true;
      }
    }
    return false;
  }
  
  // 检查所有碰撞
  checkCollision() {
    return this.checkWallCollision() || this.checkSelfCollision();
  }
}

// 生成食物
function generateFood() {
  do {
    food = {
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE)
    };
    // 确保食物不会生成在蛇身上
  } while (snake.getBody().some(segment => segment.x === food.x && segment.y === food.y));
}

// 渲染游戏
function render() {
  // 清空画布
  ctx.fillStyle = '#111';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // 绘制蛇
  ctx.fillStyle = '#0f0';
  snake.getBody().forEach((segment, index) => {
    // 蛇头用不同颜色
    if (index === 0) {
      ctx.fillStyle = '#0a0';
    } else {
      ctx.fillStyle = '#0f0';
    }
    ctx.fillRect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    ctx.strokeStyle = '#000';
    ctx.strokeRect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
  });
  
  // 绘制食物
  ctx.fillStyle = '#f00';
  ctx.beginPath();
  ctx.arc(
    food.x * CELL_SIZE + CELL_SIZE / 2,
    food.y * CELL_SIZE + CELL_SIZE / 2,
    CELL_SIZE / 2,
    0,
    Math.PI * 2
  );
  ctx.fill();
}

// 游戏结束
function gameOver() {
  gameRunning = false;
  gameOverElement.style.display = 'block';
}

// 重新开始游戏
function restartGame() {
  gameRunning = true;
  score = 0;
  currentSpeed = INITIAL_SPEED;
  scoreElement.textContent = `得分: ${score}`;
  gameOverElement.style.display = 'none';
  
  snake = new Snake();
  generateFood();
  gameLoop();
}

// 游戏主循环
function gameLoop() {
  if (!gameRunning) return;
  
  // 移动蛇
  const ateFood = snake.move();
  
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
    generateFood();
    
    // 每得5分增加游戏速度
    if (score % 5 === 0) {
      currentSpeed = Math.max(50, currentSpeed - SPEED_INCREMENT);
    }
  }
  
  render();
  
  // 使用setTimeout控制游戏速度
  setTimeout(gameLoop, currentSpeed);
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

// 重新开始按钮事件
restartButton.addEventListener('click', restartGame);

// 初始化游戏
function initGame() {
  snake = new Snake();
  generateFood();
  render();
  restartGame();
}

// 页面加载完成后初始化游戏
window.addEventListener('load', initGame);