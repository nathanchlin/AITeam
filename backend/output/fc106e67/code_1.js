// 游戏配置
const CONFIG = {
    canvasWidth: 800,
    canvasHeight: 400,
    gravity: 0.5,
    jumpForce: -12,
    gameSpeed: 5,
    groundHeight: 50,
    ninjaWidth: 30,
    ninjaHeight: 40,
    obstacleWidth: 30,
    obstacleHeight: 40,
    obstacleFrequency: 100,
    backgroundElements: []
};

// 游戏状态
let gameState = {
    isRunning: false,
    score: 0,
    lives: 3,
    frameCount: 0,
    keys: {}
};

// 获取DOM元素
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const livesElement = document.getElementById('lives');
const startScreen = document.getElementById('startScreen');
const startButton = document.getElementById('startButton');

// 设置画布尺寸
canvas.width = CONFIG.canvasWidth;
canvas.height = CONFIG.canvasHeight;

// 忍者对象
const ninja = {
    x: 100,
    y: CONFIG.canvasHeight - CONFIG.groundHeight - CONFIG.ninjaHeight,
    width: CONFIG.ninjaWidth,
    height: CONFIG.ninjaHeight,
    velocityY: 0,
    isJumping: false,
    color: '#4CAF50' // 绿色忍者
};

// 障碍物数组
let obstacles = [];

// 背景元素数组
let backgroundElements = [];

// 初始化背景元素
function initBackground() {
    // 添加云朵
    for (let i = 0; i < 5; i++) {
        backgroundElements.push({
            x: Math.random() * CONFIG.canvasWidth,
            y: Math.random() * (CONFIG.canvasHeight / 2),
            width: 60 + Math.random() * 40,
            height: 30 + Math.random() * 20,
            speed: 0.5 + Math.random() * 1.5,
            type: 'cloud'
        });
    }
    
    // 添加远山
    for (let i = 0; i < 3; i++) {
        backgroundElements.push({
            x: i * CONFIG.canvasWidth / 2,
            y: CONFIG.canvasHeight - CONFIG.groundHeight - 100,
            width: CONFIG.canvasWidth / 2,
            height: 100,
            speed: 1,
            type: 'mountain'
        });
    }
}

// 绘制背景
function drawBackground() {
    // 天空渐变
    const gradient = ctx.createLinearGradient(0, 0, 0, CONFIG.canvasHeight);
    gradient.addColorStop(0, '#87CEEB');
    gradient.addColorStop(1, '#E0F7FA');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
    
    // 绘制背景元素
    backgroundElements.forEach(element => {
        ctx.save();
        ctx.globalAlpha = element.type === 'cloud' ? 0.7 : 0.5;
        
        if (element.type === 'cloud') {
            // 绘制云朵
            ctx.fillStyle = '#FFFFFF';
            ctx.beginPath();
            ctx.arc(element.x, element.y, element.width / 3, 0, Math.PI * 2);
            ctx.arc(element.x + element.width / 3, element.y - 10, element.width / 3, 0, Math.PI * 2);
            ctx.arc(element.x + element.width * 2 / 3, element.y, element.width / 3, 0, Math.PI * 2);
            ctx.fill();
        } else if (element.type === 'mountain') {
            // 绘制远山
            ctx.fillStyle = '#8BC34A';
            ctx.beginPath();
            ctx.moveTo(element.x, CONFIG.canvasHeight - CONFIG.groundHeight);
            ctx.lineTo(element.x + element.width / 2, element.y);
            ctx.lineTo(element.x + element.width, CONFIG.canvasHeight - CONFIG.groundHeight);
            ctx.closePath();
            ctx.fill();
        }
        
        ctx.restore();
    });
}

// 绘制地面
function drawGround() {
    ctx.fillStyle = '#795548';
    ctx.fillRect(0, CONFIG.canvasHeight - CONFIG.groundHeight, CONFIG.canvasWidth, CONFIG.groundHeight);
    
    // 添加草地纹理
    ctx.fillStyle = '#4CAF50';
    for (let i = 0; i < CONFIG.canvasWidth; i += 20) {
        ctx.fillRect(i, CONFIG.canvasHeight - CONFIG.groundHeight, 10, 5);
    }
}

// 绘制忍者
function drawNinja() {
    ctx.fillStyle = ninja.color;
    ctx.fillRect(ninja.x, ninja.y, ninja.width, ninja.height);
    
    // 绘制忍者眼睛
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(ninja.x + 5, ninja.y + 10, 5, 5);
    ctx.fillRect(ninja.x + 20, ninja.y + 10, 5, 5);
    
    // 绘制忍者武器
    ctx.fillStyle = '#FF9800';
    ctx.fillRect(ninja.x + ninja.width, ninja.y + 15, 10, 5);
}

// 生成障碍物
function generateObstacle() {
    if (gameState.frameCount % CONFIG.obstacleFrequency === 0) {
        obstacles.push({
            x: CONFIG.canvasWidth,
            y: CONFIG.canvasHeight - CONFIG.groundHeight - CONFIG.obstacleHeight,
            width: CONFIG.obstacleWidth,
            height: CONFIG.obstacleHeight,
            color: '#F44336'
        });
    }
}

// 绘制障碍物
function drawObstacles() {
    obstacles.forEach(obstacle => {
        ctx.fillStyle = obstacle.color;
        ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        
        // 添加障碍物细节
        ctx.fillStyle = '#D32F2F';
        ctx.fillRect(obstacle.x + 5, obstacle.y + 5, obstacle.width - 10, 5);
    });
}

// 更新游戏状态
function update() {
    if (!gameState.isRunning) return;
    
    // 更新背景元素
    backgroundElements.forEach(element => {
        element.x -= element.speed;
        if (element.x + element.width < 0) {
            element.x = CONFIG.canvasWidth;
        }
    });
    
    // 更新忍者位置
    ninja.velocityY += CONFIG.gravity;
    ninja.y += ninja.velocityY;
    
    // 地面碰撞检测
    if (ninja.y > CONFIG.canvasHeight - CONFIG.groundHeight - ninja.height) {
        ninja.y = CONFIG.canvasHeight - CONFIG.groundHeight - ninja.height;
        ninja.velocityY = 0;
        ninja.isJumping = false;
    }
    
    // 生成和更新障碍物
    generateObstacle();
    
    obstacles = obstacles.filter(obstacle => {
        obstacle.x -= CONFIG.gameSpeed;
        
        // 碰撞检测
        if (
            ninja.x < obstacle.x + obstacle.width &&
            ninja.x + ninja.width > obstacle.x &&
            ninja.y < obstacle.y + obstacle.height &&
            ninja.y + ninja.height > obstacle.y
        ) {
            // 碰撞发生
            gameState.lives--;
            livesElement.textContent = gameState.lives;
            
            if (gameState.lives <= 0) {
                gameOver();
            }
            
            return false; // 移除障碍物
        }
        
        // 成功躲避障碍物加分
        if (obstacle.x + obstacle.width < ninja.x && !obstacle.scored) {
            obstacle.scored = true;
            gameState.score += 10;
            scoreElement.textContent = gameState.score;
        }
        
        return obstacle.x + obstacle.width > 0;
    });
    
    gameState.frameCount++;
}

// 渲染游戏画面
function render() {
    // 清空画布
    ctx.clearRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
    
    // 绘制游戏元素
    drawBackground();
    drawGround();
    drawNinja();
    drawObstacles();
}

// 游戏循环
function gameLoop() {
    update();
    render();
    requestAnimationFrame(gameLoop);
}

// 处理键盘输入
document.addEventListener('keydown', (e) => {
    gameState.keys[e.key] = true;
    
    if (e.key === ' ' && !ninja.isJumping && gameState.isRunning) {
        ninja.velocityY = CONFIG.jumpForce;
        ninja.isJumping = true;
    }
});

document.addEventListener('keyup', (e) => {
    gameState.keys[e.key] = false;
});

// 开始游戏
function startGame() {
    gameState.isRunning = true;
    gameState.score = 0;
    gameState.lives = 3;
    gameState.frameCount = 0;
    
    scoreElement.textContent = gameState.score;
    livesElement.textContent = gameState.lives;
    
    // 重置忍者位置
    ninja.y = CONFIG.canvasHeight - CONFIG.groundHeight - ninja.height;
    ninja.velocityY = 0;
    ninja.isJumping = false;
    
    // 清空障碍物
    obstacles = [];
    
    // 隐藏开始界面
    startScreen.style.display = 'none';
}

// 游戏结束
function gameOver() {
    gameState.isRunning = false;
    startScreen.style.display = 'flex';
    document.querySelector('#startScreen h1').textContent = '游戏结束';
    document.querySelector('#startScreen p').textContent = `最终得分: ${gameState.score}`;
    startButton.textContent = '重新开始';
}

// 初始化游戏
function init() {
    initBackground();
    startButton.addEventListener('click', startGame);
    gameLoop();
}

// 启动游戏
init();