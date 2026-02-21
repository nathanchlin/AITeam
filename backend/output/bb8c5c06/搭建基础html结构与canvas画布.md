# 搭建基础HTML结构与Canvas画布

**Agent**: coder

**Time**: 2026-02-18T09:36:03.348146

---

# 贪吃蛇游戏 - 基础HTML结构与Canvas画布

我将为您创建一个贪吃蛇游戏的基础HTML结构和Canvas画布设置。以下是完整的实现代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贪吃蛇游戏</title>
    <style>
        /* 基础样式重置 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }

        /* 游戏容器样式 */
        .game-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 20px;
            max-width: 600px;
            width: 100%;
        }

        /* 游戏标题样式 */
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
            font-size: 2rem;
        }

        /* 游戏信息区域样式 */
        .game-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }

        .info-item {
            font-weight: bold;
            color: #555;
        }

        /* Canvas画布样式 */
        #gameCanvas {
            border: 2px solid #333;
            display: block;
            margin: 0 auto;
            background-color: #111;
        }

        /* 控制按钮区域 */
        .controls {
            margin-top: 20px;
            text-align: center;
        }

        .btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        .btn:hover {
            background-color: #45a049;
        }

        .btn:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }

        /* 游戏状态消息样式 */
        .game-message {
            text-align: center;
            margin-top: 15px;
            font-size: 18px;
            font-weight: bold;
            min-height: 25px;
        }

        .game-over {
            color: #f44336;
        }

        .game-start {
            color: #4CAF50;
        }

        /* 游戏说明 */
        .instructions {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }

        .instructions h3 {
            margin-bottom: 10px;
            color: #333;
        }

        .instructions p {
            margin-bottom: 5px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>贪吃蛇游戏</h1>
        
        <div class="game-info">
            <div class="info-item">得分: <span id="score">0</span></div>
            <div class="info-item">最高分: <span id="highScore">0</span></div>
            <div class="info-item">等级: <span id="level">1</span></div>
        </div>
        
        <canvas id="gameCanvas" width="400" height="400"></canvas>
        
        <div class="controls">
            <button id="startBtn" class="btn">开始游戏</button>
            <button id="pauseBtn" class="btn" disabled>暂停</button>
            <button id="resetBtn" class="btn">重置</button>
        </div>
        
        <div id="gameMessage" class="game-message"></div>
        
        <div class="instructions">
            <h3>游戏说明</h3>
            <p>• 使用方向键(↑, ↓, ←, →)控制蛇的移动方向</p>
            <p>• 吃到食物(红色方块)可以增加蛇的长度和得分</p>
            <p>• 撞到墙壁或自己的身体会导致游戏结束</p>
            <p>• 每得10分，游戏速度会增加一级</p>
        </div>
    </div>

    <script>
        // 获取Canvas元素和上下文
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // 游戏配置
        const gridSize = 20; // 网格大小
        const tileCount = canvas.width / gridSize; // 网格数量
        
        // 游戏状态变量
        let snake = [];
        let food = {};
        let dx = 0; // 水平方向移动
        let dy = 0; // 垂直方向移动
        let score = 0;
        let highScore = localStorage.getItem('snakeHighScore') || 0;
        let level = 1;
        let gameRunning = false;
        let gamePaused = false;
        let gameSpeed = 100; // 初始速度(毫秒)
        
        // DOM元素
        const scoreElement = document.getElementById('score');
        const highScoreElement = document.getElementById('highScore');
        const levelElement = document.getElementById('level');
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const gameMessage = document.getElementById('gameMessage');
        
        // 初始化游戏
        function initGame() {
            // 初始化蛇的位置
            snake = [
                {x: 10, y: 10}
            ];
            
            // 初始移动方向
            dx = 0;
            dy = 0;
            
            // 重置分数和等级
            score = 0;
            level = 1;
            gameSpeed = 100;
            updateScore();
            
            // 生成食物
            generateFood();
            
            // 更新最高分显示
            highScoreElement.textContent = highScore;
            
            // 清空游戏消息
            gameMessage.textContent = '';
            gameMessage.className = 'game-message';
            
            // 绘制初始游戏状态
            drawGame();
        }
        
        // 生成食物
        function generateFood() {
            // 确保食物不会出现在蛇身上
            do {
                food = {
                    x: Math.floor(Math.random() * tileCount),
                    y: Math.floor(Math.random() * tileCount)
                };
            } while (snake.some(segment => segment.x === food.x && segment.y === food.y));
        }
        
        // 绘制游戏
        function drawGame() {
            // 清空画布
            ctx.fillStyle = '#111';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制蛇
            ctx.fillStyle = '#4CAF50';
            snake.forEach((segment, index) => {
                // 蛇头使用不同颜色
                if (index === 0) {
                    ctx.fillStyle = '#8BC34A';
                } else {
                    ctx.fillStyle = '#4CAF50';
                }
                ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize - 2, gridSize - 2);
            });
            
            // 绘制食物
            ctx.fillStyle = '#f44336';
            ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);
        }
        
        // 更新游戏状态
        function updateGame() {
            if (!gameRunning || gamePaused) return;
            
            // 计算蛇的新头部位置
            const head = {x: snake[0].x + dx, y: snake[0].y + dy};
            
            // 检查是否撞墙
            if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                gameOver();
                return;
            }
            
            // 检查是否撞到自己
            if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
                gameOver();
                return;
            }
            
            // 将新头部添加到蛇的开头
            snake.unshift(head);
            
            // 检查是否吃到食物
            if (head.x === food.x && head.y === food.y) {
                // 增加分数
                score += 1;
                updateScore();
                
                // 检查是否升级
                if (score % 10 === 0) {
                    levelUp();
                }
                
                // 生成新食物
                generateFood();
            } else {
                // 如果没有吃到食物，移除蛇的尾部
                snake.pop();
            }
            
            // 绘制更新后的游戏状态
            drawGame();
            
            // 继续游戏循环
            setTimeout(updateGame, gameSpeed);
        }
        
        // 更新分数显示
        function updateScore() {
            scoreElement.textContent = score;
            
            // 更新最高分
            if (score > highScore) {
                highScore = score;
                highScoreElement.textContent = highScore;
                localStorage.setItem('snakeHighScore', highScore);
            }
        }
        
        // 升级
        function levelUp() {
            level += 1;
            levelElement.textContent = level;
            
            // 增加游戏速度
            gameSpeed = Math.max(50, gameSpeed - 10); // 最小速度为50ms
            
            // 显示升级消息
            showMessage(`恭喜升级到第 ${level} 级!`, 'game-start');
        }
        
        // 游戏结束
        function gameOver() {
            gameRunning = false;
            showMessage(`游戏结束! 最终得分: ${score}`, 'game-over');
            
            // 禁用开始按钮，启用重置按钮
            startBtn.disabled = false;
            pauseBtn.disabled = true;
        }
        
        // 显示游戏消息
        function showMessage(message, className = '') {
            gameMessage.textContent = message;
            gameMessage.className = `game-message ${className}`;
        }
        
        // 开始游戏
        function startGame() {
            if (gameRunning) return;
            
            initGame();
            gameRunning = true;
            gamePaused = false;
            
            // 更新按钮状态
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            resetBtn.disabled = false;
            
            // 显示游戏开始消息
            showMessage('游戏开始! 使用方向键控制蛇的移动', 'game-start');
            
            // 开始游戏循环
            updateGame();
        }
        
        // 暂停/继续游戏
        function togglePause() {
            if (!gameRunning) return;
            
            gamePaused = !gamePaused;
            pauseBtn.textContent = gamePaused ? '继续' : '暂停';
            
            if (gamePaused) {
                showMessage('游戏已暂停', 'game-over');
            } else {
                showMessage('游戏继续!', 'game-start');
                updateGame();
            }
        }
        
        // 重置游戏
        function resetGame() {
            gameRunning = false;
            gamePaused = false;
            
            // 更新按钮状态
            startBtn.disabled = false;
            pauseBtn.disabled = true;
            pauseBtn.textContent = '暂停';
            resetBtn.disabled = false;
            
            // 重新初始化游戏
            initGame();
        }
        
        // 键盘事件监听
        document.addEventListener('keydown', (e) => {
            if (!gameRunning || gamePaused) return;
            
            // 防止蛇直接掉头
            switch(e.key) {
                case 'ArrowUp':
                    if (dy !== 1) {
                        dx = 0;
                        dy = -1;
                    }
                    break;
                case 'ArrowDown':
                    if (dy !== -1) {
                        dx = 0;
                        dy = 1;
                    }
                    break;
                case 'ArrowLeft':
                    if (dx !== 1) {
                        dx = -1;
                        dy = 0;
                    }
                    break;
                case 'ArrowRight':
                    if (dx !== -1) {
                        dx = 1;
                        dy = 0;
                    }
                    break;
            }
        });
        
        // 按钮事件监听
        startBtn.addEventListener('click', startGame);
        pauseBtn.addEventListener('click', togglePause);
        resetBtn.addEventListener('click', resetGame);
        
        // 初始化游戏
        initGame();
    </script>
</body>
</html>
```

## 代码说明

### HTML结构

1. **页面布局**：
   - 使用语义化HTML5标签构建页面结构
   - 包含游戏标题、分数显示、游戏画布和控制按钮
   - 添加了游戏说明区域

2. **Canvas元素**：
   - 设置了400x400像素的画布大小
   - 使用20x20像素的网格系统
   - 添加了黑色边框以便于区分游戏区域

### CSS样式

1. **响应式设计**：
   - 使用flexbox布局使游戏在各种屏幕尺寸上居中显示
   - 设置了最大宽度确保在大屏幕上不会过宽

2. **视觉设计**：
   - 使用圆角和阴影创建现代感
   - 为不同游戏状态设置了不同的颜色
   - 添加了按钮悬停效果和禁用状态

3. **游戏信息显示**：
   - 清晰显示当前得分、最高分和等级
   - 游戏消息区域用于显示游戏状态提示

### JavaScript功能

1. **游戏初始化**：
   - 设置初始蛇的位置和方向
   - 初始化分数和等级系统
   - 生成第一个食物位置

2. **游戏循环**：
   - 使用setTimeout实现游戏循环
   - 根据游戏速度动态调整更新频率
   - 实现了蛇的移动、食物生成和碰撞检测

3. **用户交互**：
   - 键盘事件监听方向键控制
   - 防止蛇直接掉头的逻辑
   - 开始、暂停和重置按钮功能

4. **游戏机制**：
   - 分数系统和等级提升
   - 最高分保存到本地存储
   - 游戏结束条件检测

这个基础结构为贪吃蛇游戏提供了完整的界面和基本功能，后续可以在此基础上添加更多高级功能，如音效、动画效果、更多游戏模式等。