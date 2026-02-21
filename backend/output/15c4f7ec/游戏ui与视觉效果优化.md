# 游戏UI与视觉效果优化

**Agent**: assistant

**Time**: 2026-02-19T20:52:26.587864

---

# 游戏UI与视觉效果优化

我将为1942打飞机游戏设计完整的界面元素和视觉特效，包括开始界面、游戏内UI和结束界面，以及各种动画效果。这将是一个完整的单文件HTML实现，整合之前的功能并添加视觉效果。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1942 打飞机游戏</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #111;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
        }
        
        #gameContainer {
            position: relative;
            width: 800px;
            height: 600px;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.7);
            border-radius: 10px;
            overflow: hidden;
        }
        
        canvas {
            background-color: #000;
            border: 2px solid #0ff;
            display: block;
        }
        
        #gameInfo {
            position: absolute;
            top: 10px;
            left: 10px;
            color: #0ff;
            font-size: 18px;
            text-shadow: 0 0 8px rgba(0, 255, 255, 0.9);
            z-index: 10;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        #gameInfo div {
            margin: 5px 0;
        }
        
        #gameOver {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #f00;
            font-size: 48px;
            text-align: center;
            display: none;
            text-shadow: 0 0 15px rgba(255, 0, 0, 0.9);
            z-index: 20;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 30px;
            border-radius: 10px;
            border: 2px solid rgba(255, 0, 0, 0.5);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.05); }
            100% { transform: translate(-50%, -50%) scale(1); }
        }
        
        #startScreen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #0ff;
            font-size: 24px;
            text-align: center;
            z-index: 20;
            background-color: rgba(0, 0, 0, 0.8);
            padding: 40px;
            border-radius: 10px;
            border: 2px solid rgba(0, 255, 255, 0.5);
            animation: fadeIn 1s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
        
        #startScreen h1 {
            margin-top: 0;
            font-size: 36px;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.9);
            animation: glow 2s infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px rgba(0, 255, 255, 0.9); }
            to { text-shadow: 0 0 20px rgba(0, 255, 255, 1), 0 0 30px rgba(0, 255, 255, 0.8); }
        }
        
        button {
            background-color: transparent;
            border: 2px solid #0ff;
            color: #0ff;
            padding: 12px 25px;
            font-size: 20px;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s;
            border-radius: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            background-color: #0ff;
            color: #000;
            box-shadow: 0 0 15px rgba(0, 255, 255, 1);
            transform: scale(1.05);
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .power-up-indicator {
            position: absolute;
            bottom: 10px;
            right: 10px;
            color: #ff0;
            font-size: 16px;
            text-shadow: 0 0 5px rgba(255, 255, 0, 0.8);
            z-index: 10;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 0, 0.3);
            display: none;
        }
        
        .level-indicator {
            position: absolute;
            top: 10px;
            right: 10px;
            color: #f0f;
            font-size: 18px;
            text-shadow: 0 0 5px rgba(255, 0, 255, 0.8);
            z-index: 10;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 0, 255, 0.3);
        }
        
        #pauseScreen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #0ff;
            font-size: 36px;
            text-align: center;
            display: none;
            z-index: 20;
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px 40px;
            border-radius: 10px;
            border: 2px solid rgba(0, 255, 255, 0.5);
        }
        
        .combo-indicator {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #ff0;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            display: none;
            z-index: 15;
            text-shadow: 0 0 10px rgba(255, 255, 0, 0.9);
            animation: comboAnimation 1s forwards;
        }
        
        @keyframes comboAnimation {
            0% { 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(0.5);
            }
            50% { 
                opacity: 1; 
                transform: translate(-50%, -50%) scale(1.2);
            }
            100% { 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(1.5) translateY(-30px);
            }
        }
        
        .health-bar {
            position: absolute;
            bottom: 10px;
            left: 10px;
            width: 200px;
            height: 20px;
            background-color: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 255, 255, 0.5);
            border-radius: 10px;
            overflow: hidden;
            z-index: 10;
        }
        
        .health-fill {
            height: 100%;
            background: linear-gradient(to right, #f00, #ff0);
            width: 100%;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="gameInfo">
            <div>分数: <span id="score">0</span></div>
            <div>生命: <span id="lives">3</span></div>
        </div>
        <div class="health-bar">
            <div class="health-fill" id="healthFill"></div>
        </div>
        <div class="level-indicator">
            关卡: <span id="level">1</span>
        </div>
        <div id="gameOver">
            <div>游戏结束</div>
            <div>最终分数: <span id="finalScore">0</span></div>
            <button onclick="game.restart()">重新开始</button>
        </div>
        <div id="startScreen">
            <h1>1942 打飞机游戏</h1>
            <p>使用方向键移动飞机，空格键射击</p>
            <p>收集能量提升火力</p>
            <button onclick="game.start()">开始游戏</button>
        </div>
        <div id="pauseScreen">
            游戏暂停
            <div style="font-size: 18px; margin-top: 20px;">按 P 键继续</div>
        </div>
        <div class="power-up-indicator" id="powerUpIndicator">
            能量提升中...
        </div>
        <div class="combo-indicator" id="comboIndicator"></div>
    </div>

    <script>
        // 游戏状态枚举
        const GameState = {
            MENU: 'menu',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over'
        };

        // 游戏主类
        class Game {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.state = GameState.MENU;
                this.score = 0;
                this.lives = 3;
                this.level = 1;
                this.combo = 0;
                this.lastHitTime = 0;
                
                // 游戏对象
                this.player = null;
                this.bullets = [];
                this.enemies = [];
                this.enemyBullets = [];
                this.powerUps = [];
                this.particles = [];
                this.explosions = [];
                
                // 游戏控制
                this.keys = {};
                this.lastTime = 0;
                this.enemySpawnTimer = 0;
                this.enemySpawnInterval = 1000; // 初始生成间隔
                this.powerUpTimer = 0;
                this.powerUpInterval = 15000; // 能量提升生成间隔
                
                // 初始化
                this.init();
            }
            
            init() {
                // 设置事件监听
                window.addEventListener('keydown', (e) => this.handleKeyDown(e));
                window.addEventListener('keyup', (e) => this.handleKeyUp(e));
                
                // 创建玩家
                this.player = new Player(400, 500);
                
                // 开始游戏循环
                this.gameLoop(0);
            }
            
            handleKeyDown(e) {
                this.keys[e.key] = true;
                
                if (e.key === 'p' || e.key === 'P') {
                    if (this.state === GameState.PLAYING) {
                        this.pause();
                    } else if (this.state === GameState.PAUSED) {
                        this.resume();
                    }
                }
            }
            
            handleKeyUp(e) {
                this.keys[e.key] = false;
            }
            
            start() {
                this.state = GameState.PLAYING;
                document.getElementById('startScreen').style.display = 'none';
                this.resetGame();
            }
            
            pause() {
                this.state = GameState.PAUSED;
                document.getElementById('pauseScreen').style.display = 'block';
            }
            
            resume() {
                this.state = GameState.PLAYING;
                document.getElementById('pauseScreen').style.display = 'none';
            }
            
            restart() {
                this.state = GameState.PLAYING;
                document.getElementById('gameOver').style.display = 'none';
                this.resetGame();
            }
            
            resetGame() {
                this.score = 0;
                this.lives = 3;
                this.level = 1;
                this.combo = 0;
                this.bullets = [];
                this.enemies = [];
                this.enemyBullets = [];
                this.powerUps = [];
                this.particles = [];
                this.explosions = [];
                this.enemySpawnTimer = 0;
                this.enemySpawnInterval = 1000;
                this.powerUpTimer = 0;
                
                this.player.reset(400, 500);
                this.updateUI();
            }
            
            updateUI() {
                document.getElementById('score').textContent = this.score;
                document.getElementById('lives').textContent = this.lives;
                document.getElementById('level').textContent = this.level;
                document.getElementById('healthFill').style.width = `${this.player.health * 20}%`;
            }
            
            gameOver() {
                this.state = GameState.GAME_OVER;
                document.getElementById('finalScore').textContent = this.score;
                document.getElementById('gameOver').style.display = 'block';
            }
            
            gameLoop(currentTime) {
                const deltaTime = currentTime - this.lastTime;
                this.lastTime = currentTime;
                
                // 清空画布
                this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // 绘制星空背景
                this.drawStarfield();
                
                if (this.state === GameState.PLAYING) {
                    // 更新游戏逻辑
                    this.update(deltaTime);
                }
                
                // 绘制游戏对象
                this.draw();
                
                // 继续游戏循环
                requestAnimationFrame((time) => this.gameLoop(time));
            }
            
            update(deltaTime) {
                // 更新玩家
                this.player.update(this.keys, this.canvas.width, this.canvas.height);
                
                // 玩家射击
                if (this.keys[' ']) {
                    const bullet = this.player.shoot();
                    if (bullet) {
                        this.bullets.push(bullet);
                    }
                }
                
                // 更新子弹
                for (let i = this.bullets.length - 1; i >= 0; i--) {
                    this.bullets[i].update();
                    
                    // 移除屏幕外的子弹
                    if (this.bullets[i].y < 0) {
                        this.bullets.splice(i, 1);
                    }
                }
                
                // 更新敌机
                for (let i = this.enemies.length - 1; i >= 0; i--) {
                    this.enemies[i].update(deltaTime);
                    
                    // 移除屏幕外的敌机
                    if (this.enemies[i].y > this.canvas.height) {
                        this.enemies.splice(i, 1);
                        continue;
                    }
                    
                    // 敌机射击
                    if (Math.random() < 0.005) {
                        const bullet = this.enemies[i].shoot();
                        if (bullet) {
                            this.enemyBullets.push(bullet);
                        }
                    }
                }
                
                // 更新敌机子弹
                for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
                    this.enemyBullets[i].update();
                    
                    // 移除屏幕外的子弹
                    if (this.enemyBullets[i].y > this.canvas.height) {
                        this.enemyBullets.splice(i, 1);
                    }
                }
                
                // 更新能量提升
                for (let i = this.powerUps.length - 1; i >= 0; i--) {
                    this.powerUps[i].update();
                    
                    // 移除屏幕外的能量提升
                    if (this.powerUps[i].y > this.canvas.height) {
                        this.powerUps.splice(i, 1);
                    }
                }
                
                // 更新粒子效果
                for (let i = this.particles.length - 1; i >= 0; i--) {
                    this.particles[i].update();
                    
                    // 移除生命周期结束的粒子
                    if (this.particles[i].life <= 0) {
                        this.particles.splice(i, 1);
                    }
                }
                
                // 更新爆炸效果
                for (let i = this.explosions.length - 1; i >= 0; i--) {
                    this.explosions[i].update();
                    
                    // 移除完成爆炸效果
                    if (this.explosions[i].isComplete()) {
                        this.explosions.splice(i, 1);
                    }
                }
                
                // 生成敌机
                this.enemySpawnTimer += deltaTime;
                if (this.enemySpawnTimer > this.enemySpawnInterval) {
                    this.spawnEnemy();
                    this.enemySpawnTimer = 0;
                    
                    // 随着游戏进行，增加难度
                    this.enemySpawnInterval = Math.max(300, 1000 - this.level * 50);
                }
                
                // 生成能量提升
                this.powerUpTimer += deltaTime;
                if (this.powerUpTimer > this.powerUpInterval) {
                    this.spawnPowerUp();
                    this.powerUpTimer = 0;
                }
                
                // 碰撞检测
                this.checkCollisions();
                
                // 更新UI
                this.updateUI();
            }
            
            draw() {
                // 绘制玩家
                this.player.draw(this.ctx);
                
                // 绘制子弹
                this.bullets.forEach(bullet => bullet.draw(this.ctx));
                
                // 绘制敌机
                this.enemies.forEach(enemy => enemy.draw(this.ctx));
                
                // 绘制敌机子弹
                this.enemyBullets.forEach(bullet => bullet.draw(this.ctx));
                
                // 绘制能量提升
                this.powerUps.forEach(powerUp => powerUp.draw(this.ctx));
                
                // 绘制粒子效果
                this.particles.forEach(particle => particle.draw(this.ctx));
                
                // 绘制