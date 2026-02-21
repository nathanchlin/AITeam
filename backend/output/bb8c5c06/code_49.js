// 游戏配置
const GRID_SIZE = 20;
const CELL_SIZE = 20;
const GAME_SPEED = 150;
const CANVAS_WIDTH = GRID_SIZE * CELL_SIZE;
const CANVAS_HEIGHT = GRID_SIZE * CELL_SIZE;

// 获取Canvas元素和上下文
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = CANVAS_WIDTH;
canvas.height = CANVAS_HEIGHT;

// 游戏状态
let gameRunning = false;
let score = 0;
let snake = null;
let food = null;

// Snake类定义
class Snake {
  constructor() {
    this.body = [{x: 10, y: 10}];
    this.direction = {x: 1, y: 0};
    this.nextDirection = {x: 1, y: 0};
  }
  
  getBody() {
    return this.body;
  }
  
  setDirection(newDirection) {
    // 防止蛇直接掉头
    if (this.direction.x + newDirection.x === 0 && 
        this.direction.y + newDirection.y === 0) {
      return;
    }
    this.nextDirection = newDirection;
  }
  
  move() {
    this.direction = {...this.nextDirection};
    
    const head = {...this.body[0]};
    head.x += this.direction.x;
    head.y += this.direction.y;
    
    this.body.unshift(head);
    
    // 如果没有吃到食物，移除尾部
    if (!this.eat(food)) {
      this.body.pop();
    }
  }
  
  grow() {
    // 在尾部添加一个新节点
    const tail = {...this.body[this.body.length - 1]};
    this.body.push(tail);
  }
  
  eat(food) {
    const head = this.body[0];
    if (head.x === food.x && head.y === food.y) {
      this.grow();
      return true;
    }
    return false;
  }
  
  checkCollision() {
    const head = this.body[0];
    
    // 检查是否撞墙
    if (head.x < 0 || head.x >= GRID_SIZE || 
        head.y < 0 || head.y >= GRID_SIZE) {
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
}

// 生成食物
function generateFood() {
  let newFood;
  do {
    newFood = {
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE)
    };
    // 确保食物不会生成在蛇身上
  } while (snake.getBody().some(segment => 
    segment.x === newFood.x && segment.y === newFood.y));
  
  food = newFood;
}

// 渲染函数
function render() {
  // 清空画布
  ctx.fillStyle = '#111';
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  
  // 绘制蛇
  ctx.fillStyle = '#0f0';
  snake.getBody().forEach((segment, index) => {
    // 蛇头用不同颜色
    if (index === 0) {
      ctx.fillStyle = '#0a0';
    } else {
      ctx.fillStyle = '#0f0';
    }
    
    ctx.fillRect(
      segment.x * CELL_SIZE, 
      segment.y * CELL_SIZE, 
      CELL_SIZE - 2, 
      CELL_SIZE - 2
    );
  });
  
  // 绘制食物
  ctx.fillStyle = '#f00';
  ctx.fillRect(
    food.x * CELL_SIZE, 
    food.y * CELL_SIZE, 
    CELL_SIZE - 2, 
    CELL_SIZE - 2
  );
  
  // 绘制分数
  ctx.fillStyle = '#fff';
  ctx.font = '16px Arial';
  ctx.fillText(`得分: ${score}`, 10, 20);
}

// 游戏主循环
function gameLoop() {
  if (!gameRunning) return;
  
  snake.move();
  
  if (snake.checkCollision()) {
    gameOver();
    return;
  }
  
  if (snake.eat(food)) {
    score++;
    document.getElementById('score').textContent = `得分: ${score}`;
    generateFood();
    
    // 随着得分增加，提高游戏速度
    if (score % 5 === 0 && GAME_SPEED > 50) {
      clearInterval(gameInterval);
      gameInterval = setInterval(gameLoop, GAME_SPEED - (score / 5) * 10);
    }
  }
  
  render();
}

// 游戏结束
function gameOver() {
  gameRunning = false;
  clearInterval(gameInterval);
  
  ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  
  ctx.fillStyle = '#fff';
  ctx.font = '30px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('游戏结束', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 20);
  ctx.font = '20px Arial';
  ctx.fillText(`最终得分: ${score}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 20);
  ctx.fillText('按空格键重新开始', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 60);
  ctx.textAlign = 'left';
}

// 键盘事件处理
document.addEventListener('keydown', (e) => {
  if (!gameRunning && e.key === ' ') {
    startGame();
    return;
  }
  
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
  if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
    e.preventDefault();
  }
});

// 游戏初始化
function initGame() {
  snake = new Snake();
  generateFood();
  score = 0;
  document.getElementById('score').textContent = `得分: ${score}`;
}

// 开始游戏
function startGame() {
  gameRunning = true;
  initGame();
  render();
  gameLoop();
}

// 游戏循环变量
let gameInterval;

// 页面加载完成后初始化游戏
window.addEventListener('load', () => {
  initGame();
  render();
});