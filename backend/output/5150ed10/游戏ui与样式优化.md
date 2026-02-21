# 游戏UI与样式优化

**Agent**: coder

**Time**: 2026-02-18T14:10:51.500553

---

# 游戏UI与样式优化方案

## 游戏界面设计

我将为"是男人就要撑过100秒"的飞行躲避游戏设计一个完整的UI界面，包括开始界面、游戏界面和结束界面。

### HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>是男人就要撑过100秒</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- 开始界面 -->
    <div id="startScreen" class="screen active">
        <div class="game-title">是男人就要撑过100秒</div>
        <div class="game-subtitle">躲避障碍，挑战极限</div>
        <button id="startButton" class="game-button">开始游戏</button>
        <div class="instructions">
            <p>操作说明：</p>
            <p>↑↓ 或 W/S - 上下移动</p>
            <p>←→ 或 A/D - 左右移动</p>
            <p>空格 - 暂停/继续</p>
        </div>
    </div>

    <!-- 游戏界面 -->
    <div id="gameScreen" class="screen">
        <div class="game-header">
            <div class="score">时间: <span id="timeDisplay">0</span>秒</div>
            <div class="lives">生命: <span id="livesDisplay">3</span></div>
        </div>
        <canvas id="gameCanvas"></canvas>
        <div id="pauseOverlay" class="overlay hidden">
            <div class="pause-content">
                <h2>游戏暂停</h2>
                <button id="resumeButton" class="game-button">继续游戏</button>
            </div>
        </div>
    </div>

    <!-- 结束界面 -->
    <div id="endScreen" class="screen">
        <div class="game-title">游戏结束</div>
        <div class="final-score">你坚持了 <span id="finalTime">0</span> 秒</div>
        <div id="newRecord" class="new-record hidden">新纪录！</div>
        <div class="score-rank">
            <h3>历史最佳</h3>
            <ol id="highScoresList"></ol>
        </div>
        <button id="restartButton" class="game-button">再玩一次</button>
    </div>

    <script src="game.js"></script>
</body>
</html>
```

### CSS样式 (styles.css)

```css
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white;
    overflow: hidden;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 屏幕通用样式 */
.screen {
    position: absolute;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.5s ease, visibility 0.5s ease;
}

.screen.active {
    opacity: 1;
    visibility: visible;
}

/* 标题样式 */
.game-title {
    font-size: 3rem;
    font-weight: bold;
    text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.5);
    margin-bottom: 1rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.game-subtitle {
    font-size: 1.5rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

/* 按钮样式 */
.game-button {
    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    border: none;
    color: white;
    padding: 1rem 2rem;
    font-size: 1.2rem;
    border-radius: 50px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 1px;
}

.game-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    background: linear-gradient(45deg, #ee5a24, #ff6b6b);
}

.game-button:active {
    transform: translateY(1px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* 开始界面样式 */
#startScreen {
    text-align: center;
}

.instructions {
    margin-top: 3rem;
    background: rgba(0, 0, 0, 0.3);
    padding: 1.5rem;
    border-radius: 10px;
    max-width: 400px;
}

.instructions p {
    margin: 0.5rem 0;
    font-size: 1rem;
}

/* 游戏界面样式 */
#gameScreen {
    padding: 0;
}

.game-header {
    position: absolute;
    top: 20px;
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
    z-index: 10;
    font-size: 1.2rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

#gameCanvas {
    background: rgba(0, 0, 0, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    max-width: 100%;
    max-height: 70vh;
}

/* 暂停界面样式 */
.overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 20;
}

.pause-content {
    background: rgba(0, 0, 0, 0.8);
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
}

/* 结束界面样式 */
#endScreen {
    text-align: center;
}

.final-score {
    font-size: 2rem;
    margin: 1.5rem 0;
}

.new-record {
    color: #ffd700;
    font-size: 1.5rem;
    margin: 1rem 0;
    animation: flash 1s infinite;
}

@keyframes flash {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.score-rank {
    margin: 2rem 0;
    background: rgba(0, 0, 0, 0.3);
    padding: 1.5rem;
    border-radius: 10px;
    max-width: 300px;
}

.score-rank h3 {
    margin-bottom: 1rem;
    font-size: 1.3rem;
}

#highScoresList {
    list-style: none;
    padding: 0;
}

#highScoresList li {
    padding: 0.5rem;
    margin: 0.3rem 0;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .game-title {
        font-size: 2rem;
    }
    
    .game-subtitle {
        font-size: 1.2rem;
    }
    
    .game-button {
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
    }
    
    .instructions {
        font-size: 0.9rem;
        padding: 1rem;
    }
    
    .game-header {
        font-size: 1rem;
    }
    
    #gameCanvas {
        max-height: 60vh;
    }
}

@media (max-width: 480px) {
    .game-title {
        font-size: 1.8rem;
    }
    
    .instructions {
        font-size: 0.8rem;
        padding: 0.8rem;
        max-width: 300px;
    }
    
    .game-header {
        padding: 0 10px;
        font-size: 0.9rem;
    }
    
    #gameCanvas {
        max-height: 50vh;
    }
}
```

## 游戏界面功能实现

### JavaScript游戏逻辑 (game.js)

```javascript
// 游戏状态
const GameState = {
    START: 'start',
    PLAYING: 'playing',
    PAUSED: 'paused',
    ENDED: 'ended'
};

// 游戏变量
let gameState = GameState.START;
let canvas, ctx;
let player, obstacles, particles;
let gameTime = 0;
let lastTime = 0;
let lives = 3;
let highScores = [];
let animationId;

// 玩家对象
class Player {
    constructor() {
        this.width = 50;
        this.height = 30;
        this.x = 100;
        this.y = canvas.height / 2 - this.height / 2;
        this.speed = 5;
        this.color = '#4CAF50';
    }
    
    update() {
        // 边界检查
        this.y = Math.max(0, Math.min(canvas.height - this.height, this.y));
    }
    
    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 绘制玩家细节
        ctx.fillStyle = '#2E7D32';
        ctx.fillRect(this.x + 5, this.y + 5, this.width - 10, this.height - 10);
        
        // 绘制引擎火焰效果
        ctx.fillStyle = '#FF9800';
        ctx.fillRect(this.x - 10, this.y + 10, 10, 10);
        ctx.fillStyle = '#FF5722';
        ctx.fillRect(this.x - 15, this.y + 12, 5, 6);
    }
    
    moveUp() {
        this.y -= this.speed;
    }
    
    moveDown() {
        this.y += this.speed;
    }
    
    moveLeft() {
        this.x -= this.speed;
        if (this.x < 0) this.x = 0;
    }
    
    moveRight() {
        this.x += this.speed;
        if (this.x > canvas.width - this.width) this.x = canvas.width - this.width;
    }
}

// 障碍物对象
class Obstacle {
    constructor() {
        this.width = 30 + Math.random() * 50;
        this.height = 30 + Math.random() * 100;
        this.x = canvas.width;
        this.y = Math.random() * (canvas.height - this.height);
        this.speed = 3 + Math.random() * 3 + gameTime / 10; // 随时间增加速度
        this.color = `hsl(${Math.random() * 360}, 70%, 50%)`;
    }
    
    update() {
        this.x -= this.speed;
    }
    
    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        
        // 添加阴影效果
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(this.x + 5, this.y + 5, this.width, this.height);
    }
    
    isOffScreen() {
        return this.x + this.width < 0;
    }
    
    collidesWith(player) {
        return player.x < this.x + this.width &&
               player.x + player.width > this.x &&
               player.y < this.y + this.height &&
               player.y + player.height > this.y;
    }
}

// 粒子效果
class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = Math.random() * 5 + 2;
        this.speedX = Math.random() * 3 - 1.5;
        this.speedY = Math.random() * 3 - 1.5;
        this.color = `hsl(${Math.random() * 360}, 70%, 50%)`;
        this.life = 1.0;
    }
    
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        this.life -= 0.02;
        this.size *= 0.98;
    }
    
    draw() {
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
    }
    
    isDead() {
        return this.life <= 0;
    }
}

// 初始化游戏
function initGame() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    
    // 设置画布大小
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // 加载高分
    loadHighScores();
    
    // 绑定事件
    document.getElementById('startButton').addEventListener('click', startGame);
    document.getElementById('restartButton').addEventListener('click', restartGame);
    document.getElementById('resumeButton').addEventListener('click', resumeGame);
    
    // 键盘控制
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    
    // 触摸控制（移动设备）
    canvas.addEventListener('touchstart', handleTouchStart);
    canvas.addEventListener('touchmove', handleTouchMove);
    
    // 显示开始界面
    showScreen('startScreen');
}

// 调整画布大小
function resizeCanvas() {
    const maxWidth = window.innerWidth * 0.9;
    const maxHeight = window.innerHeight * 0.6;
    
    canvas.width = Math.min(800, maxWidth);
    canvas.height = Math.min(400, maxHeight);
    
    // 如果玩家已经存在，更新位置
    if (player) {
        player.x = Math.min(player.x, canvas.width - player.width);
        player.y = Math.min(player.y, canvas.height - player.height);
    }
}

// 开始游戏
function startGame() {
    gameState = GameState.PLAYING;
    gameTime = 0;
    lives = 3;
    
    // 初始化游戏对象
    player = new Player();
    obstacles = [];
    particles = [];
    
    // 更新UI
    updateGameUI();
    showScreen('gameScreen');
    
    // 开始游戏循环
    lastTime = performance.now();
    gameLoop();
}

// 游戏主循环
function gameLoop(currentTime) {
    if (gameState !== GameState.PLAYING) return;
    
    const deltaTime = currentTime - lastTime;
    lastTime = currentTime;
    
    // 更新游戏时间
    gameTime += deltaTime / 1000;
    document.getElementById('timeDisplay').textContent = Math.floor(gameTime);
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制背景
    drawBackground();
    
    // 更新和绘制玩家
    player.update();
    player.draw();
    
    // 生成新障碍物
    if (Math.random() < 0.02 + gameTime / 1000) {
        obstacles.push(new Obstacle());
    }
    
    // 更新和绘制障碍物
    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].update();
        obstacles[i].draw();
        
        // 检测碰撞
        if (obstacles[i].collidesWith(player)) {
            // 创建爆炸效果
            for (let j = 0; j < 20; j++) {
                particles.push(new Particle(
                    player.x + player.width / 2,
                    player.y + player.height / 2
                ));
            }
            
            lives--;
            updateGameUI();
            
            // 移除碰撞的障碍物
            obstacles.splice(i, 1);
            
            // 检查游戏是否结束
            if (lives <= 0) {
                endGame();
                return;
            }
        } else if (obstacles[i].isOffScreen()) {
            // 移除屏幕外的障碍物
            obstacles.splice(i, 1);
        }
    }
    
    // 更新和绘制粒子
    for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].update();
        particles[i].draw();
        
        if (particles[i].isDead()) {
            particles.splice(i, 1);
        }
    }
    
    // 继续游戏循环
    animationId = requestAnimationFrame(gameLoop);
}

// 绘制背景
function drawBackground() {
    // 绘制移动的星星背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    for (let i = 0; i < 50; i++) {
        const