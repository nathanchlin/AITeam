# 创建HTML结构与基本样式

**Agent**: coder

**Time**: 2026-02-17T17:41:42.563694

---

我将为您创建贪吃蛇游戏的基础HTML结构和基本样式。以下是完整的单个HTML文件，包含所有必要的HTML、CSS和JavaScript代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贪吃蛇游戏</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .game-container {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 600px;
            width: 100%;
        }

        h1 {
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
            color: #4CAF50;
        }

        .game-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 0 10px;
        }

        .score-board, .high-score {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 1.2em;
            font-weight: bold;
        }

        #gameCanvas {
            border: 3px solid #4CAF50;
            border-radius: 8px;
            background-color: #111;
            display: block;
            margin: 0 auto 20px;
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.3);
        }

        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 1.1em;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        button:hover {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.3);
        }

        button:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .game-over {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .game-over-content {
            background: #222;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }

        .game-over h2 {
            color: #f44336;
            margin-bottom: 20px;
            font-size: 2em;
        }

        .instructions {
            margin-top: 20px;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            font-size: 0.9em;
            line-height: 1.6;
        }

        .instructions h3 {
            margin-bottom: 10px;
            color: #4CAF50;
        }

        @media (max-width: 600px) {
            .game-container {
                padding: 15px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            #gameCanvas {
                width: 100%;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>贪吃蛇游戏</h1>
        
        <div class="game-info">
            <div class="score-board">得分: <span id="score">0</span></div>
            <div class="high-score">最高分: <span id="highScore">0</span></div>
        </div>
        
        <canvas id="gameCanvas" width="400" height="400"></canvas>
        
        <div class="controls">
            <button id="startBtn">开始游戏</button>
            <button id="pauseBtn">暂停</button>
            <button id="resetBtn">重置</button>
        </div>
        
        <div class="instructions">
            <h3>游戏说明</h3>
            <p>使用键盘方向键(↑, ↓, ←, →)控制蛇的移动方向</p>
            <p>吃到食物可以增加蛇的长度和得分</p>
            <p>撞到墙壁或自己的身体游戏结束</p>
        </div>
    </div>
    
    <div class="game-over" id="gameOverModal">
        <div class="game-over-content">
            <h2>游戏结束!</h2>
            <p>最终得分: <span id="finalScore">0</span></p>
            <button id="restartBtn">重新开始</button>
        </div>
    </div>

    <script>
        // 游戏变量
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreElement = document.getElementById('score');
        const highScoreElement = document.getElementById('highScore');
        const finalScoreElement = document.getElementById('finalScore');
        const gameOverModal = document.getElementById('gameOverModal');
        
        // 游戏状态
        let gameRunning = false;
        let gamePaused = false;
        let score = 0;
        let highScore = localStorage.getItem('snakeHighScore') || 0;
        highScoreElement.textContent = highScore;
        
        // 游戏设置
        const gridSize = 20;
        const tileCount = canvas.width / gridSize;
        
        // 蛇的初始状态
        let snake = [
            {x: 10, y: 10}
        ];
        let direction = {x: 0, y: 0};
        let food = generateFood();
        
        // 生成食物
        function generateFood() {
            let newFood;
            do {
                newFood = {
                    x: Math.floor(Math.random() * tileCount),
                    y: Math.floor(Math.random() * tileCount)
                };
            } while (snake.some(segment => segment.x === newFood.x && segment.y === newFood.y));
            return newFood;
        }
        
        // 绘制游戏
        function drawGame() {
            // 清空画布
            ctx.fillStyle = '#111';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制蛇
            ctx.fillStyle = '#4CAF50';
            snake.forEach((segment, index) => {
                if (index === 0) {
                    // 蛇头
                    ctx.fillStyle = '#8BC34A';
                } else {
                    ctx.fillStyle = '#4CAF50';
                }
                ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize - 2, gridSize - 2);
            });
            
            // 绘制食物
            ctx.fillStyle = '#f44336';
            ctx.beginPath();
            ctx.arc(
                food.x * gridSize + gridSize / 2,
                food.y * gridSize + gridSize / 2,
                gridSize / 2 - 1,
                0,
                Math.PI * 2
            );
            ctx.fill();
        }
        
        // 更新游戏状态
        function updateGame() {
            if (!gameRunning || gamePaused) return;
            
            // 移动蛇头
            const head = {x: snake[0].x + direction.x, y: snake[0].y + direction.y};
            
            // 检查碰撞
            if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                gameOver();
                return;
            }
            
            // 检查是否撞到自己
            if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
                gameOver();
                return;
            }
            
            snake.unshift(head);
            
            // 检查是否吃到食物
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                scoreElement.textContent = score;
                food = generateFood();
            } else {
                snake.pop();
            }
            
            drawGame();
        }
        
        // 游戏结束
        function gameOver() {
            gameRunning = false;
            finalScoreElement.textContent = score;
            gameOverModal.style.display = 'flex';
            
            if (score > highScore) {
                highScore = score;
                highScoreElement.textContent = highScore;
                localStorage.setItem('snakeHighScore', highScore);
            }
        }
        
        // 重置游戏
        function resetGame() {
            snake = [{x: 10, y: 10}];
            direction = {x: 0, y: 0};
            score = 0;
            scoreElement.textContent = score;
            food = generateFood();
            gameRunning = false;
            gamePaused = false;
            drawGame();
        }
        
        // 开始游戏
        function startGame() {
            if (!gameRunning) {
                gameRunning = true;
                gamePaused = false;
                gameLoop();
            }
        }
        
        // 暂停/继续游戏
        function togglePause() {
            if (gameRunning) {
                gamePaused = !gamePaused;
                if (!gamePaused) {
                    gameLoop();
                }
            }
        }
        
        // 游戏主循环
        function gameLoop() {
            if (gameRunning && !gamePaused) {
                updateGame();
                setTimeout(gameLoop, 100);
            }
        }
        
        // 键盘控制
        document.addEventListener('keydown', (e) => {
            if (!gameRunning || gamePaused) return;
            
            switch(e.key) {
                case 'ArrowUp':
                    if (direction.y === 0) {
                        direction = {x: 0, y: -1};
                    }
                    break;
                case 'ArrowDown':
                    if (direction.y === 0) {
                        direction = {x: 0, y: 1};
                    }
                    break;
                case 'ArrowLeft':
                    if (direction.x === 0) {
                        direction = {x: -1, y: 0};
                    }
                    break;
                case 'ArrowRight':
                    if (direction.x === 0) {
                        direction = {x: 1, y: 0};
                    }
                    break;
            }
        });
        
        // 按钮事件
        document.getElementById('startBtn').addEventListener('click', startGame);
        document.getElementById('pauseBtn').addEventListener('click', togglePause);
        document.getElementById('resetBtn').addEventListener('click', resetGame);
        document.getElementById('restartBtn').addEventListener('click', () => {
            gameOverModal.style.display = 'none';
            resetGame();
            startGame();
        });
        
        // 初始化游戏
        drawGame();
    </script>
</body>
</html>
```

这个HTML文件包含了贪吃蛇游戏的基础结构和样式，具有以下特点：

1. **游戏界面结构**：
   - 游戏标题
   - 得分板和最高分显示
   - 游戏画布（400x400像素）
   - 控制按钮（开始、暂停、重置）
   - 游戏说明
   - 游戏结束弹窗

2. **视觉设计**：
   - 深色背景与绿色主题的配色方案
   - 渐变背景和阴影效果增强视觉层次
   - 响应式设计，适配不同屏幕尺寸
   - 按钮悬停和点击效果

3. **基本功能实现**：
   - 蛇的绘制（头部和身体区分）
   - 食物的绘制（圆形）
   - 基本的键盘控制方向
   - 得分系统
   - 最高分记录（使用localStorage保存）

4. **游戏状态管理**：
   - 开始/暂停/重置功能
   - 游戏结束弹窗

这个文件已经包含了所有必要的HTML、CSS和JavaScript代码，可以直接在浏览器中打开运行。游戏的核心逻辑（移动、碰撞检测、吃食物等）已经实现，但您可以根据需要进一步完善游戏细节。