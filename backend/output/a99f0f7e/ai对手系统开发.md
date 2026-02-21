# AI对手系统开发

**Agent**: coder

**Time**: 2026-02-19T18:42:22.946294

---

我将为您创建一个完整的球球大作战游戏，包含AI对手系统。这是一个单文件HTML应用，使用原生Canvas API实现。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>球球大作战 - AI对手版</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #111;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        
        #gameCanvas {
            border: 2px solid #333;
            background-color: #000;
            cursor: crosshair;
        }
        
        #gameInfo {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-size: 16px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }
        
        #gameOver {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            margin-top: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div id="gameInfo">
        <div>得分: <span id="score">0</span></div>
        <div>排名: <span id="rank">1</span>/10</div>
    </div>
    
    <canvas id="gameCanvas" width="1200" height="700"></canvas>
    
    <div id="gameOver">
        <h2>游戏结束</h2>
        <p>最终得分: <span id="finalScore">0</span></p>
        <button onclick="restartGame()">重新开始</button>
    </div>

    <script>
        // 游戏配置
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const gameInfo = {
            score: document.getElementById('score'),
            rank: document.getElementById('rank'),
            finalScore: document.getElementById('finalScore'),
            gameOver: document.getElementById('gameOver')
        };
        
        // 游戏状态
        let gameRunning = true;
        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;
        let camera = { x: 0, y: 0 };
        
        // 食物数组
        let foods = [];
        
        // 玩家球
        const player = {
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: 20,
            color: '#4CAF50',
            speed: 3,
            score: 0,
            targetX: canvas.width / 2,
            targetY: canvas.height / 2,
            cells: []
        };
        
        // AI对手数组
        const aiPlayers = [];
        const aiCount = 9; // 9个AI对手
        
        // 食物类
        class Food {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = Math.random() * 5 + 3;
                this.color = this.getRandomColor();
            }
            
            getRandomColor() {
                const colors = ['#FF5252', '#FFD740', '#40C4FF', '#69F0AE', '#FF4081'];
                return colors[Math.floor(Math.random() * colors.length)];
            }
            
            draw() {
                ctx.beginPath();
                ctx.arc(this.x - camera.x, this.y - camera.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }
        
        // 球类（玩家和AI都继承此类）
        class Ball {
            constructor(x, y, radius, color, isAI = false) {
                this.x = x;
                this.y = y;
                this.radius = radius;
                this.color = color;
                this.isAI = isAI;
                this.speed = isAI ? 2 : 3;
                this.targetX = x;
                this.targetY = y;
                this.score = 0;
                this.cells = [];
                this.splitCooldown = 0;
                this.eatingCooldown = 0;
                this.fleeTarget = null;
                this.aggression = Math.random() * 0.5 + 0.3; // AI的攻击性 (0.3-0.8)
                this.caution = Math.random() * 0.5 + 0.4; // AI的谨慎度 (0.4-0.9)
            }
            
            // 更新球的位置
            update() {
                // 冷却时间递减
                if (this.splitCooldown > 0) this.splitCooldown--;
                if (this.eatingCooldown > 0) this.eatingCooldown--;
                
                // AI行为逻辑
                if (this.isAI) {
                    this.aiBehavior();
                } else {
                    // 玩家跟随鼠标
                    this.targetX = mouseX;
                    this.targetY = mouseY;
                }
                
                // 移动逻辑
                const dx = this.targetX - this.x;
                const dy = this.targetY - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance > 5) {
                    // 速度与大小成反比
                    const speedFactor = Math.max(0.5, 1 - (this.radius / 100));
                    const moveSpeed = this.speed * speedFactor;
                    
                    this.x += (dx / distance) * moveSpeed;
                    this.y += (dy / distance) * moveSpeed;
                }
                
                // 边界检查
                this.x = Math.max(this.radius, Math.min(canvas.width * 3 - this.radius, this.x));
                this.y = Math.max(this.radius, Math.min(canvas.height * 3 - this.radius, this.y));
            }
            
            // AI行为逻辑
            aiBehavior() {
                // 1. 寻找最近的食物
                let nearestFood = null;
                let minFoodDist = Infinity;
                
                foods.forEach(food => {
                    const dist = this.getDistance(food);
                    if (dist < minFoodDist) {
                        minFoodDist = dist;
                        nearestFood = food;
                    }
                });
                
                // 2. 检查威胁和机会
                let threat = null;
                let opportunity = null;
                
                // 检查其他球
                const allBalls = [player, ...aiPlayers];
                allBalls.forEach(ball => {
                    if (ball === this) return;
                    
                    const dist = this.getDistance(ball);
                    
                    // 如果球比自己大，可能是威胁
                    if (ball.radius > this.radius * 1.1 && dist < 300) {
                        if (!threat || dist < this.getDistance(threat)) {
                            threat = ball;
                        }
                    }
                    
                    // 如果球比自己小，可能是机会
                    if (ball.radius < this.radius * 0.9 && dist < 200) {
                        if (!opportunity || dist < this.getDistance(opportunity)) {
                            opportunity = ball;
                        }
                    }
                });
                
                // 3. 决策逻辑
                if (threat && this.radius < 50) {
                    // 小球遇到威胁，逃跑
                    this.fleeTarget = threat;
                    this.targetX = this.x + (this.x - threat.x);
                    this.targetY = this.y + (this.y - threat.y);
                } else if (opportunity && Math.random() < this.aggression) {
                    // 攻击小球
                    this.targetX = opportunity.x;
                    this.targetY = opportunity.y;
                } else if (nearestFood) {
                    // 寻找食物
                    this.targetX = nearestFood.x;
                    this.targetY = nearestFood.y;
                } else {
                    // 随机移动
                    if (Math.random() < 0.02) {
                        this.targetX = Math.random() * canvas.width * 3;
                        this.targetY = Math.random() * canvas.height * 3;
                    }
                }
                
                // 4. 分裂逻辑
                if (this.radius > 40 && this.splitCooldown === 0 && Math.random() < 0.01) {
                    if (threat && this.radius < threat.radius * 1.5) {
                        // 遇到威胁时更倾向于分裂
                        this.split();
                    } else if (!threat && Math.random() < this.aggression) {
                        // 没有威胁时，根据攻击性决定是否分裂
                        this.split();
                    }
                }
            }
            
            // 获取到另一个对象距离
            getDistance(obj) {
                const dx = this.x - obj.x;
                const dy = this.y - obj.y;
                return Math.sqrt(dx * dx + dy * dy);
            }
            
            // 分裂
            split() {
                if (this.radius < 30) return; // 太小不能分裂
                
                const newRadius = this.radius * 0.7;
                this.radius = newRadius;
                
                // 创建分裂后的新球
                const angle = Math.random() * Math.PI * 2;
                const distance = this.radius + newRadius;
                
                const newBall = new Ball(
                    this.x + Math.cos(angle) * distance,
                    this.y + Math.sin(angle) * distance,
                    newRadius,
                    this.color,
                    this.isAI
                );
                
                newBall.score = this.score / 2;
                this.score = this.score / 2;
                
                if (this.isAI) {
                    aiPlayers.push(newBall);
                } else {
                    player.cells.push(newBall);
                }
                
                this.splitCooldown = 300; // 5秒冷却
            }
            
            // 绘制球
            draw() {
                // 绘制主球
                ctx.beginPath();
                ctx.arc(this.x - camera.x, this.y - camera.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                
                // 绘制边框
                ctx.strokeStyle = '#FFF';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // 绘制名字
                ctx.fillStyle = '#FFF';
                ctx.font = '14px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                let name = this.isAI ? `AI${aiPlayers.indexOf(this) + 1}` : '玩家';
                if (!this.isAI && player.cells.length > 0) {
                    name = `团队(${player.cells.length + 1})`;
                }
                
                ctx.fillText(name, this.x - camera.x, this.y - camera.y);
                
                // 绘制分数
                ctx.font = '12px Arial';
                ctx.fillText(Math.floor(this.score), this.x - camera.x, this.y - camera.y + this.radius + 15);
                
                // 绘制分裂的球
                if (this.cells) {
                    this.cells.forEach(cell => cell.draw());
                }
            }
            
            // 吃食物
            eatFood() {
                if (this.eatingCooldown > 0) return;
                
                for (let i = foods.length - 1; i >= 0; i--) {
                    const food = foods[i];
                    const dist = this.getDistance(food);
                    
                    if (dist < this.radius + food.radius) {
                        // 增加分数和大小
                        this.score += food.radius;
                        this.radius += food.radius * 0.1;
                        
                        // 移除食物
                        foods.splice(i, 1);
                        
                        // 创建新食物
                        this.createFood();
                        
                        // 限制最大尺寸
                        if (this.radius > 100) {
                            this.radius = 100;
                        }
                        
                        this.eatingCooldown = 10;
                    }
                }
            }
            
            // 创建新食物
            createFood() {
                const x = Math.random() * canvas.width * 3;
                const y = Math.random() * canvas.height * 3;
                foods.push(new Food(x, y));
            }
            
            // 吃其他球
            eatBall(ball) {
                if (ball === this) return;
                if (this.radius < ball.radius * 1.1) return; // 太小不能吃
                
                const dist = this.getDistance(ball);
                if (dist < this.radius + ball.radius) {
                    // 增加分数和大小
                    this.score += ball.score;
                    this.radius += ball.radius * 0.2;
                    
                    // 移除被吃的球
                    if (ball.isAI) {
                        const index = aiPlayers.indexOf(ball);
                        if (index > -1) {
                            aiPlayers.splice(index, 1);
                        }
                    } else if (player.cells.includes(ball)) {
                        const index = player.cells.indexOf(ball);
                        if (index > -1) {
                            player.cells.splice(index, 1);
                        }
                    }
                    
                    // 创建新食物
                    this.createFood();
                    
                    // 限制最大尺寸
                    if (this.radius > 100) {
                        this.radius = 100;
                    }
                }
            }
        }
        
        // 初始化游戏
        function initGame() {
            // 重置游戏状态
            gameRunning = true;
            gameInfo.gameOver.style.display = 'none';
            foods = [];
            player.score = 0;
            player.radius = 20;
            player.cells = [];
            aiPlayers.length = 0;
            
            // 创建食物
            for (let i = 0; i < 200; i++) {
                const x = Math.random() * canvas.width * 3;
                const y = Math.random() * canvas.height * 3;
                foods.push(new Food(x, y));
            }
            
            // 创建AI对手
            for (let i = 0; i < aiCount; i++) {
                const x = Math.random() * canvas.width * 3;
                const y = Math.random() * canvas.height * 3;
                const colors = ['#FF5252', '#FFD740', '#40C4FF', '#69F0AE', '#FF4081', '#7C4DFF', '#FF6E40', '#18FFFF', '#FFFF00'];
                const color = colors[i % colors.length];
                
                aiPlayers.push(new Ball(x, y, 15 + Math.random() * 15, color, true));
            }
        }
        
        // 更新相机位置
        function updateCamera() {
            // 相机跟随玩家
            camera.x = player.x - canvas.width / 2;
            camera.y = player.y - canvas.height / 2;
            
            // 限制相机边界
            camera.x = Math.max(0, Math.min(canvas.width * 2, camera.x));
            camera.y = Math.max(0, Math.min(canvas.height * 2, camera.y));
        }
        
        // 更新游戏信息
        function updateGameInfo() {
            // 更新玩家分数
            player.score += 0.1;
            gameInfo.score.textContent = Math.floor(player.score);
            
            // 计算排名
            const allBalls = [player, ...aiPlayers];
            allBalls.sort((a, b) => b.score - a.score);
            const rank = allBalls.indexOf(player) + 1;
            gameInfo.rank.textContent = rank;
            
            // 检查游戏结束条件
            if (player.radius <= 10) {
                gameRunning = false;
                gameInfo.finalScore.textContent = Math.floor(player.score);
                gameInfo.gameOver.style.display = 'block';
            }
        }
        
        // 游戏主循环
        function gameLoop() {
            if (!gameRunning) return;
            
            // 清空画布
            ctx.fillStyle = '#111';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制网格背景
            drawGrid();
            
            // 更新相机
            updateCamera();
            
            // 更新和绘制食物
            foods.forEach(food => {
                food.draw();
            });
            
            // 更新和绘制AI
            aiPlayers.forEach(ai => {
                ai.update();
                ai.eatFood();
                ai.eatBall(player);
                
                // AI之间的互相吃
                aiPlayers.forEach(otherAI => {
                    if (ai !== otherAI) {
                        ai.eatBall(otherAI);
                    }
                });
                
                ai.draw();
            });
            
            // 更新和绘制玩家
            player.update();
            player.eatFood();
            
            // 玩家吃AI
            aiPlayers.forEach(ai => {
                player.eatBall(ai);
            });
            
            // 玩家吃自己的分裂球
            player.cells.forEach(cell => {
                player.eatBall(cell);
            });
            
            player.draw();
            
            // 更新游戏信息
            updateGameInfo();
            
            // 继续游戏循环
            requestAnimationFrame(gameLoop);
        }
        
        // 绘制网格背景
        function drawGrid() {
            ctx.strokeStyle = '#222';
            ctx.lineWidth = 1;
            
            const gridSize = 50;
            const startX = -camera.x % gridSize;
            const startY = -camera.y % gridSize;
            
            // 绘制垂直线
            for (let x = startX; x < canvas.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            
            // 绘制水平线
            for (let y = startY; y < canvas.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
        }
        
        // 重新开始游戏
        function restartGame() {
            initGame();
            gameLoop();
        }
        
        // 事件监听
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left + camera.x;
            mouseY = e.clientY - rect.top + camera.y;
        });
        
        canvas.addEventListener('click', (e) => {
            if (!gameRunning) return;
            
            // 玩家分裂
            if (player.radius > 30 && player.splitCooldown ===