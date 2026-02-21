# 基础游戏规则与UI实现

**Agent**: coder

**Time**: 2026-02-19T18:43:31.129712

---

我将为您实现一个球球大作战游戏的基础版本，包含游戏规则系统和UI界面。这是一个完整的单文件HTML实现，可以直接在浏览器中运行。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>球球大作战</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: 'Arial', sans-serif;
            background-color: #f0f0f0;
        }
        
        #gameContainer {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #gameCanvas {
            background-color: #f8f8f8;
            border: 2px solid #333;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        #gameUI {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        
        #scoreBoard {
            position: absolute;
            top: 20px;
            left: 20px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        #gameOverScreen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            display: none;
            pointer-events: auto;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        #gameOverScreen h2 {
            margin-top: 0;
            color: #333;
        }
        
        #gameOverScreen p {
            font-size: 18px;
            margin: 10px 0;
        }
        
        #restartButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        #restartButton:hover {
            background-color: #45a049;
        }
        
        #startScreen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            pointer-events: auto;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        #startScreen h2 {
            margin-top: 0;
            color: #333;
        }
        
        #startButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-top: 20px;
        }
        
        #startButton:hover {
            background-color: #45a049;
        }
        
        #leaderboard {
            position: absolute;
            top: 20px;
            right: 20px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .player-info {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <div id="gameUI">
            <div id="scoreBoard">
                <div>得分: <span id="score">0</span></div>
                <div>大小: <span id="playerSize">20</span></div>
            </div>
            <div id="leaderboard">
                <h3>排行榜</h3>
                <div id="leaderboardList"></div>
            </div>
            <div id="startScreen">
                <h2>球球大作战</h2>
                <p>使用鼠标控制你的球移动</p>
                <p>吃掉比你小的球来成长</p>
                <p>避开比你大的球，否则会被吃掉！</p>
                <button id="startButton">开始游戏</button>
            </div>
            <div id="gameOverScreen">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="finalScore">0</span></p>
                <p>最终大小: <span id="finalSize">20</span></p>
                <button id="restartButton">重新开始</button>
            </div>
        </div>
    </div>

    <script>
        // 游戏配置
        const CONFIG = {
            canvasWidth: 1000,
            canvasHeight: 600,
            playerSpeed: 5,
            foodCount: 50,
            minFoodSize: 5,
            maxFoodSize: 15,
            minEnemySize: 15,
            maxEnemySize: 50,
            enemyCount: 10,
            growthFactor: 1.1,
            scorePerFood: 10
        };

        // 游戏状态
        let gameState = {
            isRunning: false,
            isGameOver: false,
            score: 0,
            player: null,
            foods: [],
            enemies: [],
            leaderboard: []
        };

        // 获取DOM元素
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreElement = document.getElementById('score');
        const playerSizeElement = document.getElementById('playerSize');
        const startScreen = document.getElementById('startScreen');
        const gameOverScreen = document.getElementById('gameOverScreen');
        const finalScoreElement = document.getElementById('finalScore');
        const finalSizeElement = document.getElementById('finalSize');
        const leaderboardList = document.getElementById('leaderboardList');
        const startButton = document.getElementById('startButton');
        const restartButton = document.getElementById('restartButton');

        // 设置画布大小
        canvas.width = CONFIG.canvasWidth;
        canvas.height = CONFIG.canvasHeight;

        // 球类
        class Ball {
            constructor(x, y, radius, color) {
                this.x = x;
                this.y = y;
                this.radius = radius;
                this.color = color;
                this.speed = CONFIG.playerSpeed;
                this.dx = 0;
                this.dy = 0;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.stroke();
                ctx.closePath();
            }

            move() {
                this.x += this.dx;
                this.y += this.dy;

                // 边界检查
                if (this.x - this.radius < 0) {
                    this.x = this.radius;
                }
                if (this.x + this.radius > CONFIG.canvasWidth) {
                    this.x = CONFIG.canvasWidth - this.radius;
                }
                if (this.y - this.radius < 0) {
                    this.y = this.radius;
                }
                if (this.y + this.radius > CONFIG.canvasHeight) {
                    this.y = CONFIG.canvasHeight - this.radius;
                }
            }

            canEat(other) {
                const distance = Math.sqrt(
                    Math.pow(this.x - other.x, 2) + 
                    Math.pow(this.y - other.y, 2)
                );
                return distance < this.radius && this.radius > other.radius * 1.1;
            }

            grow(amount) {
                this.radius += amount;
                // 限制最大大小
                if (this.radius > 100) {
                    this.radius = 100;
                }
            }
        }

        // 食物类
        class Food extends Ball {
            constructor(x, y) {
                super(x, y, 
                    Math.random() * (CONFIG.maxFoodSize - CONFIG.minFoodSize) + CONFIG.minFoodSize,
                    `hsl(${Math.random() * 360}, 70%, 60%)`
                );
            }
        }

        // 敌人类
        class Enemy extends Ball {
            constructor(x, y) {
                super(x, y, 
                    Math.random() * (CONFIG.maxEnemySize - CONFIG.minEnemySize) + CONFIG.minEnemySize,
                    `hsl(${Math.random() * 360}, 70%, 50%)`
                );
                // 随机初始方向
                const angle = Math.random() * Math.PI * 2;
                this.dx = Math.cos(angle) * this.speed * 0.5;
                this.dy = Math.sin(angle) * this.speed * 0.5;
            }

            move() {
                // 随机改变方向
                if (Math.random() < 0.02) {
                    const angle = Math.random() * Math.PI * 2;
                    this.dx = Math.cos(angle) * this.speed * 0.5;
                    this.dy = Math.sin(angle) * this.speed * 0.5;
                }
                
                super.move();
            }
        }

        // 玩家类
        class Player extends Ball {
            constructor(x, y) {
                super(x, y, 20, '#4CAF50');
                this.isAlive = true;
            }

            move() {
                // 使用鼠标位置控制移动
                const targetX = mouseX;
                const targetY = mouseY;
                
                // 计算方向向量
                const dx = targetX - this.x;
                const dy = targetY - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // 如果距离大于0，则移动
                if (distance > 0) {
                    // 根据球的大小调整速度
                    const speed = CONFIG.playerSpeed * (1 - this.radius / 200);
                    this.dx = (dx / distance) * speed;
                    this.dy = (dy / distance) * speed;
                    
                    super.move();
                }
            }
        }

        // 鼠标位置
        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;

        // 鼠标移动事件
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        // 初始化游戏
        function initGame() {
            gameState.isRunning = true;
            gameState.isGameOver = false;
            gameState.score = 0;
            
            // 创建玩家
            gameState.player = new Player(
                Math.random() * CONFIG.canvasWidth,
                Math.random() * CONFIG.canvasHeight
            );
            
            // 创建食物
            gameState.foods = [];
            for (let i = 0; i < CONFIG.foodCount; i++) {
                gameState.foods.push(new Food(
                    Math.random() * CONFIG.canvasWidth,
                    Math.random() * CONFIG.canvasHeight
                ));
            }
            
            // 创建敌人
            gameState.enemies = [];
            for (let i = 0; i < CONFIG.enemyCount; i++) {
                gameState.enemies.push(new Enemy(
                    Math.random() * CONFIG.canvasWidth,
                    Math.random() * CONFIG.canvasHeight
                ));
            }
            
            // 更新UI
            updateUI();
            
            // 隐藏开始屏幕
            startScreen.style.display = 'none';
            gameOverScreen.style.display = 'none';
        }

        // 更新UI
        function updateUI() {
            scoreElement.textContent = gameState.score;
            playerSizeElement.textContent = Math.round(gameState.player.radius);
        }

        // 更新排行榜
        function updateLeaderboard() {
            // 简单的排行榜实现（实际游戏中应该从服务器获取）
            const players = [
                { name: '玩家1', score: gameState.score, size: Math.round(gameState.player.radius) },
                { name: '玩家2', score: Math.floor(gameState.score * 0.8), size: Math.round(gameState.player.radius * 0.9) },
                { name: '玩家3', score: Math.floor(gameState.score * 0.6), size: Math.round(gameState.player.radius * 0.8) },
                { name: '玩家4', score: Math.floor(gameState.score * 0.4), size: Math.round(gameState.player.radius * 0.7) },
                { name: '玩家5', score: Math.floor(gameState.score * 0.2), size: Math.round(gameState.player.radius * 0.6) }
            ];
            
            players.sort((a, b) => b.score - a.score);
            
            leaderboardList.innerHTML = '';
            players.forEach(player => {
                const playerDiv = document.createElement('div');
                playerDiv.className = 'player-info';
                playerDiv.textContent = `${player.name}: ${player.score}分 (${player.size}大小)`;
                leaderboardList.appendChild(playerDiv);
            });
        }

        // 游戏结束
        function gameOver() {
            gameState.isRunning = false;
            gameState.isGameOver = true;
            
            finalScoreElement.textContent = gameState.score;
            finalSizeElement.textContent = Math.round(gameState.player.radius);
            
            gameOverScreen.style.display = 'block';
            updateLeaderboard();
        }

        // 重新开始游戏
        function restartGame() {
            initGame();
        }

        // 游戏循环
        function gameLoop() {
            if (!gameState.isRunning) {
                requestAnimationFrame(gameLoop);
                return;
            }
            
            // 清除画布
            ctx.clearRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
            
            // 绘制网格背景
            ctx.strokeStyle = '#ddd';
            ctx.lineWidth = 1;
            for (let i = 0; i < CONFIG.canvasWidth; i += 50) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, CONFIG.canvasHeight);
                ctx.stroke();
            }
            for (let i = 0; i < CONFIG.canvasHeight; i += 50) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(CONFIG.canvasWidth, i);
                ctx.stroke();
            }
            
            // 移动和绘制玩家
            gameState.player.move();
            gameState.player.draw();
            
            // 移动和绘制敌人
            gameState.enemies.forEach(enemy => {
                enemy.move();
                enemy.draw();
                
                // 检查玩家是否被敌人吃掉
                if (enemy.canEat(gameState.player)) {
                    gameOver();
                }
                
                // 检查敌人是否吃掉其他敌人
                for (let i = 0; i < gameState.enemies.length; i++) {
                    for (let j = i + 1; j < gameState.enemies.length; j++) {
                        if (gameState.enemies[i].canEat(gameState.enemies[j])) {
                            gameState.enemies[i].grow(gameState.enemies[j].radius * 0.2);
                            gameState.enemies.splice(j, 1);
                            j--;
                        } else if (gameState.enemies[j].canEat(gameState.enemies[i])) {
                            gameState.enemies[j].grow(gameState.enemies[i].radius * 0.2);
                            gameState.enemies.splice(i, 1);
                            i--;
                            break;
                        }
                    }
                }
            });
            
            // 绘制食物
            gameState.foods.forEach((food, index) => {
                food.draw();
                
                // 检查玩家是否吃到食物
                if (gameState.player.canEat(food)) {
                    gameState.player.grow(food.radius * 0.1);
                    gameState.score += CONFIG.scorePerFood;
                    gameState.foods.splice(index, 1);
                    
                    // 生成新的食物
                    gameState.foods.push(new Food(
                        Math.random() * CONFIG.canvasWidth,
                        Math.random() * CONFIG.canvasHeight
                    ));
                    
                    // 更新UI
                    updateUI();
                }
                
                // 检查敌人是否吃到食物
                gameState.enemies.forEach(enemy => {
                    if (enemy.canEat(food)) {
                        enemy.grow(food.radius * 0.1);
                        gameState.foods.splice(index, 1);
                        
                        // 生成新的食物
                        gameState.foods.push(new Food(
                            Math.random() * CONFIG.canvasWidth,
                            Math.random() * CONFIG.canvasHeight
                        ));
                    }
                });
            });
            
            // 更新排行榜
            updateLeaderboard();
            
            // 继续游戏循环
            requestAnimationFrame(gameLoop);
        }

        // 事件监听
        startButton.addEventListener('click', initGame);
        restartButton.addEventListener('click', restartGame);

        // 初始化游戏循环
        gameLoop();
    </script>
</body>
</html>
```

这个球球大作战游戏实现了以下功能：

1. **基本游戏规则**：
   - 玩家控制一个绿色球，通过鼠标移动
   - 吃掉比自己小的球可以成长并获得分数
   - 被比自己大的球碰到会游戏结束
   - 敌人AI会随机移动并相互吞噬

2. **得分机制**：
   - 每吃掉一个食物获得10分
   - 球的大小会影响移动速度（越大越慢）
   - 实时显示当前得分和球的大小

3. **游戏结束条件**：
   - 当玩家被比自己大的球碰到时游戏结束
   - 显示最终得分和球的大小
   - 提供重新开始按钮

4. **UI界面**：
   - 开始界面显示游戏说明
   - 游戏过程中显示得分和大小信息
   - 右侧显示排行榜（模拟）
   - 游戏结束界面显示最终成绩

5. **技术实现**：
   - 使用Canvas API进行渲染
   - requestAnimationFrame实现游戏循环
   - 鼠标事件控制玩家移动
   - 碰撞检测算法判断球之间的吞噬关系

游戏可以直接在浏览器