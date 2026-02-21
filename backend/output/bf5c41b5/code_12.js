// 游戏配置
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const livesElement = document.getElementById('lives');
const gameOverElement = document.getElementById('gameOver');
const gameOverText = document.getElementById('gameOverText');
const finalScoreElement = document.getElementById('finalScore');
const restartBtn = document.getElementById('restartBtn');

// 游戏状态
let gameRunning = true;
let score = 0;
let lives = 3;

// 挡板对象
const paddle = {
    x: canvas.width / 2 - 50,
    y: canvas.height - 20,
    width: 100,
    height: 10,
    speed: 8,
    dx: 0
};

// 球对象
const ball = {
    x: canvas.width / 2,
    y: canvas.height - 30,
    radius: 8,
    speed: 4,
    dx: 4,
    dy: -4
};

// 砖块配置
const brickRowCount = 5;
const brickColumnCount = 8;
const brickWidth = 75;
const brickHeight = 20;
const brickPadding = 10;
const brickOffsetTop = 60;
const brickOffsetLeft = 30;

// 砖块数组
let bricks = [];

// 初始化砖块
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
                ctx.beginPath();
                ctx.rect(brickX, brickY, brickWidth, brickHeight);
                ctx.fillStyle = '#0095DD';
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
    else if (ball.y + ball.dy > paddle.y - ball.radius) {
        if (ball.x > paddle.x && ball.x < paddle.x + paddle.width) {
            // 根据球击中挡板的位置改变反弹角度
            const hitPos = (ball.x - paddle.x) / paddle.width;
            ball.dx = 8 * (hitPos - 0.5);
            ball.dy = -ball.dy;
        }
        // 球掉落
        else if (ball.y + ball.dy > canvas.height - ball.radius) {
            lives--;
            livesElement.textContent = lives;
            if (lives === 0) {
                gameOver();
            } else {
                resetBall();
            }
        }
    }
}

// 重置球的位置
function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height - 30;
    ball.dx = 4;
    ball.dy = -4;
    paddle.x = canvas.width / 2 - 50;
}

// 游戏结束
function gameOver() {
    gameRunning = false;
    gameOverText.textContent = '游戏结束';
    finalScoreElement.textContent = score;
    gameOverElement.style.display = 'block';
}

// 游戏胜利
function gameWin() {
    gameRunning = false;
    gameOverText.textContent = '恭喜你赢了！';
    finalScoreElement.textContent = score;
    gameOverElement.style.display = 'block';
}

// 重新开始游戏
function restartGame() {
    gameRunning = true;
    score = 0;
    lives = 3;
    scoreElement.textContent = score;
    livesElement.textContent = lives;
    gameOverElement.style.display = 'none';
    initBricks();
    resetBall();
}

// 游戏主循环
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBricks();
    drawBall();
    drawPaddle();
    collisionDetection();
    
    if (gameRunning) {
        update();
        requestAnimationFrame(draw);
    }
}

// 重新开始按钮事件
restartBtn.addEventListener('click', restartGame);

// 初始化游戏
initBricks();
draw();