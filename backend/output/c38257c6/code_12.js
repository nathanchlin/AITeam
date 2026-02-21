// 游戏配置
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const livesElement = document.getElementById('lives');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');

// 设置Canvas尺寸
canvas.width = 800;
canvas.height = 600;

// 游戏状态
let gameRunning = false;
let gamePaused = false;
let score = 0;
let lives = 3;

// 游戏对象
const paddle = {
    x: canvas.width / 2 - 50,
    y: canvas.height - 30,
    width: 100,
    height: 15,
    speed: 8,
    dx: 0
};

const ball = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    radius: 10,
    speed: 5,
    dx: 3,
    dy: -3
};

// 砖块配置
const brickRowCount = 5;
const brickColumnCount = 10;
const brickWidth = 70;
const brickHeight = 20;
const brickPadding = 10;
const brickOffsetTop = 60;
const brickOffsetLeft = 35;

// 初始化砖块
let bricks = [];
function initBricks() {
    bricks = [];
    for (let c = 0; c < brickColumnCount; c++) {
        bricks[c] = [];
        for (let r = 0; r < brickRowCount; r++) {
            const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
            const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
            bricks[c][r] = { x: brickX, y: brickY, status: 1 };
        }
    }
}

// 键盘控制
let rightPressed = false;
let leftPressed = false;

document.addEventListener('keydown', keyDownHandler);
document.addEventListener('keyup', keyUpHandler);

function keyDownHandler(e) {
    if (e.key === 'Right' || e.key === 'ArrowRight') {
        rightPressed = true;
    } else if (e.key === 'Left' || e.key === 'ArrowLeft') {
        leftPressed = true;
    }
}

function keyUpHandler(e) {
    if (e.key === 'Right' || e.key === 'ArrowRight') {
        rightPressed = false;
    } else if (e.key === 'Left' || e.key === 'ArrowLeft') {
        leftPressed = false;
    }
}

// 绘制挡板
function drawPaddle() {
    ctx.beginPath();
    ctx.rect(paddle.x, paddle.y, paddle.width, paddle.height);
    ctx.fillStyle = '#0095DD';
    ctx.fill();
    ctx.closePath();
}

// 绘制球
function drawBall() {
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = '#0095DD';
    ctx.fill();
    ctx.closePath();
}

// 绘制砖块
function drawBricks() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) {
                const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                bricks[c][r].x = brickX;
                bricks[c][r].y = brickY;
                
                ctx.beginPath();
                ctx.rect(brickX, brickY, brickWidth, brickHeight);
                ctx.fillStyle = `hsl(${r * 40}, 70%, 50%)`;
                ctx.fill();
                ctx.closePath();
            }
        }
    }
}

// 碰撞检测
function collisionDetection() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            const b = bricks[c][r];
            if (b.status === 1) {
                if (
                    ball.x > b.x &&
                    ball.x < b.x + brickWidth &&
                    ball.y > b.y &&
                    ball.y < b.y + brickHeight
                ) {
                    ball.dy = -ball.dy;
                    b.status = 0;
                    score += 10;
                    scoreElement.textContent = score;
                    
                    // 检查是否所有砖块都被消除
                    if (score === brickRowCount * brickColumnCount * 10) {
                        gameWin();
                    }
                }
            }
        }
    }
}

// 更新游戏状态
function update() {
    if (!gameRunning || gamePaused) return;
    
    // 移动挡板
    if (rightPressed && paddle.x < canvas.width - paddle.width) {
        paddle.x += paddle.speed;
    } else if (leftPressed && paddle.x > 0) {
        paddle.x -= paddle.speed;
    }
    
    // 移动球
    ball.x += ball.dx;
    ball.y += ball.dy;
    
    // 球碰到左右边界
    if (ball.x + ball.dx > canvas.width - ball.radius || ball.x + ball.dx < ball.radius) {
        ball.dx = -ball.dx;
    }
    
    // 球碰到上边界
    if (ball.y + ball.dy < ball.radius) {
        ball.dy = -ball.dy;
    }
    // 球碰到挡板
    else if (
        ball.y + ball.dy > paddle.y - ball.radius &&
        ball.x > paddle.x &&
        ball.x < paddle.x + paddle.width
    ) {
        ball.dy = -ball.dy;
        
        // 根据球击中挡板的位置改变反弹角度
        const hitPoint = (ball.x - paddle.x) / paddle.width;
        ball.dx = 5 * (hitPoint - 0.5);
    }
    // 球掉落到底部
    else if (ball.y + ball.dy > canvas.height - ball.radius) {
        lives--;
        livesElement.textContent = lives;
        
        if (lives === 0) {
            gameOver();
        } else {
            resetBall();
        }
    }
    
    collisionDetection();
}

// 重置球的位置
function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height - 50;
    ball.dx = 3;
    ball.dy = -3;
    paddle.x = canvas.width / 2 - 50;
}

// 渲染游戏画面
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBricks();
    drawPaddle();
    drawBall();
    
    if (!gameRunning) {
        ctx.font = '36px Arial';
        ctx.fillStyle = '#0095DD';
        ctx.textAlign = 'center';
        ctx.fillText('点击"开始游戏"开始', canvas.width / 2, canvas.height / 2);
    } else if (gamePaused) {
        ctx.font = '36px Arial';
        ctx.fillStyle = '#0095DD';
        ctx.textAlign = 'center';
        ctx.fillText('游戏暂停', canvas.width / 2, canvas.height / 2);
    }
}

// 游戏循环
function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// 开始游戏
function startGame() {
    if (!gameRunning) {
        gameRunning = true;
        gamePaused = false;
        score = 0;
        lives = 3;
        scoreElement.textContent = score;
        livesElement.textContent = lives;
        initBricks();
        resetBall();
        startBtn.textContent = '重新开始';
    } else {
        // 重新开始游戏
        gameRunning = true;
        gamePaused = false;
        score = 0;
        lives = 3;
        scoreElement.textContent = score;
        livesElement.textContent = lives;
        initBricks();
        resetBall();
    }
}

// 暂停/继续游戏
function togglePause() {
    if (gameRunning) {
        gamePaused = !gamePaused;
        pauseBtn.textContent = gamePaused ? '继续' : '暂停';
    }
}

// 游戏结束
function gameOver() {
    gameRunning = false;
    ctx.font = '36px Arial';
    ctx.fillStyle = '#FF0000';
    ctx.textAlign = 'center';
    ctx.fillText('游戏结束!', canvas.width / 2, canvas.height / 2);
    ctx.font = '24px Arial';
    ctx.fillText(`最终得分: ${score}`, canvas.width / 2, canvas.height / 2 + 40);
}

// 游戏胜利
function gameWin() {
    gameRunning = false;
    ctx.font = '36px Arial';
    ctx.fillStyle = '#00FF00';
    ctx.textAlign = 'center';
    ctx.fillText('恭喜你赢了!', canvas.width / 2, canvas.height / 2);
    ctx.font = '24px Arial';
    ctx.fillText(`最终得分: ${score}`, canvas.width / 2, canvas.height / 2 + 40);
}

// 事件监听
startBtn.addEventListener('click', startGame);
pauseBtn.addEventListener('click', togglePause);

// 初始化游戏
initBricks();
draw();
gameLoop();