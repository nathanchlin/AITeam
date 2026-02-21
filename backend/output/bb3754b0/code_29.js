// 游戏变量
let canvas, ctx;
let bird, pipes, score, highScore, gameState;
let frameCount = 0;
const PIPE_GAP = 150; // 管道之间的间隙
const PIPE_WIDTH = 60;
const PIPE_SPEED = 2;

// 初始化游戏
function init() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    
    // 从localStorage加载最高分
    highScore = localStorage.getItem('flappyBirdHighScore') || 0;
    document.getElementById('highScore').textContent = `High Score: ${highScore}`;
    
    // 初始化游戏对象
    resetGame();
    
    // 添加事件监听
    document.addEventListener('keydown', handleKeyPress);
    canvas.addEventListener('touchstart', handleTouch);
    
    // 开始游戏循环
    gameLoop();
}

// 重置游戏
function resetGame() {
    bird = {
        x: 50,
        y: 250,
        width: 30,
        height: 30,
        velocity: 0,
        gravity: 0.5,
        jump: -8
    };
    
    pipes = [];
    score = 0;
    frameCount = 0;
    
    // 更新分数显示
    document.getElementById('score').textContent = `Score: ${score}`;
    document.getElementById('finalScore').textContent = score;
    
    gameState = 'start';
}

// 游戏主循环
function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// 更新游戏状态
function update() {
    if (gameState !== 'playing') return;
    
    frameCount++;
    
    // 更新小鸟位置
    bird.velocity += bird.gravity;
    bird.y += bird.velocity;
    
    // 生成管道
    if (frameCount % 100 === 0) {
        generatePipe();
    }
    
    // 更新管道位置
    pipes.forEach(pipe => {
        pipe.x -= PIPE_SPEED;
    });
    
    // 移除屏幕外的管道
    pipes = pipes.filter(pipe => pipe.x + PIPE_WIDTH > 0);
    
    // 碰撞检测
    checkCollisions();
    
    // 计分
    updateScore();
}

// 绘制游戏画面
function draw() {
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制背景
    drawBackground();
    
    // 绘制小鸟
    drawBird();
    
    // 绘制管道
    pipes.forEach(pipe => drawPipe(pipe));
    
    // 绘制分数
    drawScore();
    
    // 绘制游戏状态
    if (gameState === 'start') {
        drawStartScreen();
    } else if (gameState === 'gameOver') {
        drawGameOverScreen();
    }
}

// 绘制背景
function drawBackground() {
    // 天空渐变
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#87CEEB');
    gradient.addColorStop(1, '#98D8E8');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制地面
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(0, canvas.height - 20, canvas.width, 20);
    
    // 绘制草地
    ctx.fillStyle = '#2ECC40';
    ctx.fillRect(0, canvas.height - 20, canvas.width, 10);
}

// 绘制小鸟
function drawBird() {
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(bird.x, bird.y, bird.width, bird.height);
    
    // 绘制眼睛
    ctx.fillStyle = 'white';
    ctx.fillRect(bird.x + bird.width - 10, bird.y + 5, 8, 8);
    ctx.fillStyle = 'black';
    ctx.fillRect(bird.x + bird.width - 8, bird.y + 7, 4, 4);
    
    // 绘制嘴巴
    ctx.fillStyle = '#e67e22';
    ctx.beginPath();
    ctx.moveTo(bird.x + bird.width, bird.y + bird.height / 2);
    ctx.lineTo(bird.x + bird.width + 10, bird.y + bird.height / 2 - 5);
    ctx.lineTo(bird.x + bird.width + 10, bird.y + bird.height / 2 + 5);
    ctx.closePath();
    ctx.fill();
}

// 绘制管道
function drawPipe(pipe) {
    // 上管道
    ctx.fillStyle = '#27ae60';
    ctx.fillRect(pipe.x, 0, PIPE_WIDTH, pipe.y);
    
    // 上管道边缘
    ctx.fillStyle = '#229954';
    ctx.fillRect(pipe.x - 5, pipe.y - 30, PIPE_WIDTH + 10, 30);
    
    // 下管道
    ctx.fillStyle = '#27ae60';
    ctx.fillRect(pipe.x, pipe.y + PIPE_GAP, PIPE_WIDTH, canvas.height - pipe.y - PIPE_GAP);
    
    // 下管道边缘
    ctx.fillStyle = '#229954';
    ctx.fillRect(pipe.x - 5, pipe.y + PIPE_GAP, PIPE_WIDTH + 10, 30);
}

// 绘制分数
function drawScore() {
    ctx.fillStyle = 'white';
    ctx.font = '24px Arial';
    ctx.fillText(`Score: ${score}`, 20, 40);
}

// 绘制开始画面
function drawStartScreen() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = 'white';
    ctx.font = '36px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Flappy Bird', canvas.width / 2, canvas.height / 2 - 50);
    
    ctx.font = '20px Arial';
    ctx.fillText('Press Space or Tap to Start', canvas.width / 2, canvas.height / 2 + 20);
    ctx.textAlign = 'left';
}

// 绘制游戏结束画面
function drawGameOverScreen() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = 'white';
    ctx.font = '36px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Game Over', canvas.width / 2, canvas.height / 2 - 50);
    
    ctx.font = '20px Arial';
    ctx.fillText(`Your Score: ${score}`, canvas.width / 2, canvas.height / 2 + 20);
    ctx.fillText('Press Space or Tap to Restart', canvas.width / 2, canvas.height / 2 + 60);
    ctx.textAlign = 'left';
}

// 生成管道
function generatePipe() {
    const minHeight = 50;
    const maxHeight = canvas.height - PIPE_GAP - minHeight - 20; // 20是地面高度
    const height = Math.random() * (maxHeight - minHeight) + minHeight;
    
    pipes.push({
        x: canvas.width,
        y: height,
        width: PIPE_WIDTH,
        gap: PIPE_GAP,
        passed: false
    });
}

// 碰撞检测
function checkCollisions() {
    // 检查是否撞到上下边界
    if (bird.y < 0 || bird.y + bird.height > canvas.height - 20) { // 20是地面高度
        gameState = 'gameOver';
        updateHighScore();
        return;
    }
    
    // 检查是否撞到管道
    for (let pipe of pipes) {
        if (bird.x < pipe.x + pipe.width &&
            bird.x + bird.width > pipe.x &&
            (bird.y < pipe.y || bird.y + bird.height > pipe.y + pipe.gap)) {
            gameState = 'gameOver';
            updateHighScore();
            return;
        }
    }
}

// 更新分数
function updateScore() {
    pipes.forEach(pipe => {
        if (!pipe.passed && bird.x > pipe.x + pipe.width) {
            pipe.passed = true;
            score++;
            document.getElementById('score').textContent = `Score: ${score}`;
        }
    });
}

// 更新最高分
function updateHighScore() {
    if (score > highScore) {
        highScore = score;
        localStorage.setItem('flappyBirdHighScore', highScore);
        document.getElementById('highScore').textContent = `High Score: ${highScore}`;
    }
}

// 事件处理
function handleKeyPress(e) {
    if (e.code === 'Space') {
        e.preventDefault();
        if (gameState === 'start') {
            gameState = 'playing';
        } else if (gameState === 'playing') {
            bird.velocity = bird.jump;
        } else if (gameState === 'gameOver') {
            resetGame();
            gameState = 'playing';
        }
    }
}

function handleTouch(e) {
    e.preventDefault();
    handleKeyPress({code: 'Space'});
}

// 页面加载完成后初始化游戏
window.onload = function() {
    init();
};