/**
 * 游戏状态管理模块
 */
class GameState {
  constructor() {
    // 游戏配置
    this.gridSize = 20; // 网格大小
    this.cellSize = 20; // 每个单元格的像素大小
    this.initialSpeed = 150; // 初始速度(毫秒)
    this.speedIncrement = 5; // 每吃一个食物速度增加的毫秒数
    
    // 游戏状态
    this.isRunning = false;
    this.isPaused = false;
    this.score = 0;
    this.highScore = 0;
    this.gameSpeed = this.initialSpeed;
    
    // 蛇的初始状态
    this.snake = new Snake([
      {x: 10, y: 10},
      {x: 9, y: 10},
      {x: 8, y: 10}
    ]);
    
    // 食物
    this.food = null;
    
    // 游戏循环ID
    this.gameLoopId = null;
    
    // 初始化食物
    this.generateFood();
  }
  
  /**
   * 开始游戏
   */
  start() {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.isPaused = false;
    this.score = 0;
    this.gameSpeed = this.initialSpeed;
    
    // 重置蛇
    this.snake = new Snake([
      {x: 10, y: 10},
      {x: 9, y: 10},
      {x: 8, y: 10}
    ]);
    
    // 生成新食物
    this.generateFood();
    
    // 启动游戏循环
    this.gameLoop();
  }
  
  /**
   * 暂停/继续游戏
   */
  togglePause() {
    if (!this.isRunning) return;
    
    this.isPaused = !this.isPaused;
    
    if (this.isPaused) {
      cancelAnimationFrame(this.gameLoopId);
    } else {
      this.gameLoop();
    }
  }
  
  /**
   * 游戏主循环
   */
  gameLoop() {
    if (!this.isRunning || this.isPaused) return;
    
    // 移动蛇
    this.moveSnake();
    
    // 检查碰撞
    if (this.checkCollision()) {
      this.gameOver();
      return;
    }
    
    // 检查是否吃到食物
    if (this.snake.head.x === this.food.x && this.snake.head.y === this.food.y) {
      this.eatFood();
    }
    
    // 更新显示
    this.updateDisplay();
    
    // 继续游戏循环
    setTimeout(() => {
      this.gameLoopId = requestAnimationFrame(() => this.gameLoop());
    }, this.gameSpeed);
  }
  
  /**
   * 移动蛇
   */
  moveSnake() {
    this.snake.move();
  }
  
  /**
   * 检查碰撞
   */
  checkCollision() {
    const head = this.snake.head;
    
    // 检查是否撞墙
    if (head.x < 0 || head.x >= this.gridSize || 
        head.y < 0 || head.y >= this.gridSize) {
      return true;
    }
    
    // 检查是否撞到自己
    for (let i = 1; i < this.snake.body.length; i++) {
      if (head.x === this.snake.body[i].x && head.y === this.snake.body[i].y) {
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * 吃食物
   */
  eatFood() {
    // 增加蛇的长度
    this.snake.grow();
    
    // 增加分数
    this.score += 10;
    
    // 更新最高分
    if (this.score > this.highScore) {
      this.highScore = this.score;
    }
    
    // 增加速度
    this.gameSpeed = Math.max(50, this.gameSpeed - this.speedIncrement);
    
    // 生成新食物
    this.generateFood();
  }
  
  /**
   * 生成食物
   */
  generateFood() {
    let newFood;
    let isOnSnake;
    
    do {
      isOnSnake = false;
      newFood = {
        x: Math.floor(Math.random() * this.gridSize),
        y: Math.floor(Math.random() * this.gridSize)
      };
      
      // 检查食物是否生成在蛇身上
      for (const segment of this.snake.body) {
        if (segment.x === newFood.x && segment.y === newFood.y) {
          isOnSnake = true;
          break;
        }
      }
    } while (isOnSnake);
    
    this.food = newFood;
  }
  
  /**
   * 游戏结束
   */
  gameOver() {
    this.isRunning = false;
    cancelAnimationFrame(this.gameLoopId);
    
    // 显示游戏结束消息
    this.showGameOverMessage();
  }
  
  /**
   * 显示游戏结束消息
   */
  showGameOverMessage() {
    const message = `游戏结束! 得分: ${this.score} | 最高分: ${this.highScore}`;
    const gameOverElement = document.getElementById('game-over');
    if (gameOverElement) {
      gameOverElement.textContent = message;
      gameOverElement.style.display = 'block';
    }
  }
  
  /**
   * 更新显示
   */
  updateDisplay() {
    // 更新蛇的显示
    this.snake.render(this.cellSize);
    
    // 更新食物显示
    this.renderFood();
    
    // 更新分数显示
    this.updateScore();
  }
  
  /**
   * 渲染食物
   */
  renderFood() {
    // 清除旧的食物
    const oldFood = document.querySelector('.food');
    if (oldFood) {
      oldFood.remove();
    }
    
    // 创建新的食物元素
    const foodElement = document.createElement('div');
    foodElement.className = 'food';
    foodElement.style.width = `${this.cellSize}px`;
    foodElement.style.height = `${this.cellSize}px`;
    foodElement.style.left = `${this.food.x * this.cellSize}px`;
    foodElement.style.top = `${this.food.y * this.cellSize}px`;
    foodElement.style.backgroundColor = 'red';
    foodElement.style.position = 'absolute';
    
    // 添加到游戏区域
    const gameBoard = document.getElementById('game-board');
    if (gameBoard) {
      gameBoard.appendChild(foodElement);
    }
  }
  
  /**
   * 更新分数显示
   */
  updateScore() {
    const scoreElement = document.getElementById('score');
    if (scoreElement) {
      scoreElement.textContent = `得分: ${this.score} | 最高分: ${this.highScore}`;
    }
  }
  
  /**
   * 处理键盘输入
   */
  handleKeyPress(key) {
    if (!this.isRunning || this.isPaused) return;
    
    switch(key) {
      case 'ArrowUp':
        if (this.snade.direction.y === 0) {
          this.snake.setDirection({x: 0, y: -1});
        }
        break;
      case 'ArrowDown':
        if (this.snake.direction.y === 0) {
          this.snake.setDirection({x: 0, y: 1});
        }
        break;
      case 'ArrowLeft':
        if (this.snake.direction.x === 0) {
          this.snake.setDirection({x: -1, y: 0});
        }
        break;
      case 'ArrowRight':
        if (this.snake.direction.x === 0) {
          this.snake.setDirection({x: 1, y: 0});
        }
        break;
    }
  }
}

/**
 * 蛇的类
 */
class Snake {
  constructor(initialBody) {
    this.body = initialBody;
    this.direction = {x: 1, y: 0}; // 初始向右移动
  }
  
  /**
   * 获取蛇头
   */
  get head() {
    return this.body[0];
  }
  
  /**
   * 移动蛇
   */
  move() {
    // 计算新的头部位置
    const newHead = {
      x: this.head.x + this.direction.x,
      y: this.head.y + this.direction.y
    };
    
    // 将新头部添加到身体前面
    this.body.unshift(newHead);
    
    // 移除尾部（如果没有吃到食物）
    this.body.pop();
  }
  
  /**
   * 增长蛇（吃到食物时调用）
   */
  grow() {
    // 在尾部添加一个新节
    const tail = this.body[this.body.length - 1];
    this.body.push({...tail});
  }
  
  /**
   * 设置方向
   */
  setDirection(newDirection) {
    this.direction = newDirection;
  }
  
  /**
   * 渲染蛇
   */
  render(cellSize) {
    // 清除旧的蛇元素
    const oldSnake = document.querySelectorAll('.snake');
    oldSnake.forEach(segment => segment.remove());
    
    // 创建新的蛇元素
    this.body.forEach((segment, index) => {
      const segmentElement = document.createElement('div');
      segmentElement.className = 'snake';
      segmentElement.style.width = `${cellSize}px`;
      segmentElement.style.height = `${cellSize}px`;
      segmentElement.style.left = `${segment.x * cellSize}px`;
      segmentElement.style.top = `${segment.y * cellSize}px`;
      segmentElement.style.backgroundColor = index === 0 ? 'darkgreen' : 'green';
      segmentElement.style.position = 'absolute';
      
      // 添加到游戏区域
      const gameBoard = document.getElementById('game-board');
      if (gameBoard) {
        gameBoard.appendChild(segmentElement);
      }
    });
  }
}

// 游戏实例
let game;

/**
 * 初始化游戏
 */
function initGame() {
  game = new GameState();
  
  // 设置键盘事件监听
  document.addEventListener('keydown', (e) => {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
      e.preventDefault(); // 防止页面滚动
      game.handleKeyPress(e.key);
    }
    
    // 空格键暂停/继续
    if (e.key === ' ') {
      e.preventDefault();
      if (game.isRunning) {
        game.togglePause();
      } else {
        game.start();
      }
    }
  });
  
  // 设置开始按钮
  const startButton = document.getElementById('start-button');
  if (startButton) {
    startButton.addEventListener('click', () => {
      if (game.isRunning) {
        game.togglePause();
        startButton.textContent = game.isPaused ? '继续' : '暂停';
      } else {
        game.start();
        startButton.textContent = '暂停';
      }
    });
  }
  
  // 初始渲染
  game.updateDisplay();
}

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', initGame);