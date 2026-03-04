# UI Elements and Animation

**Time**: 2026-02-25T16:56:43.927927

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pong Game</title>
<style>
  body {
    margin: 0;
    overflow: hidden;
    background-color: #000;
  }
  canvas {
    display: block;
    width: 100vw; /* Full viewport width */
    height: 100vh; /* Full viewport height */
  }
  #scoreBoard {
    position: absolute;
    top: 10px;
    left: 10px;
    color: white;
    font-size: 24px;
  }
  #gameOver {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 48px;
    font-family: fantasy;
    display: none; /* Hide game over text initially */
  }
</style>
</head>
<body>
<div id="scoreBoard">
  <div>Player: <span id="playerScore">0</span></div>
  <div>AI: <span id="aiScore">0</span></div>
</div>
<canvas id="gameCanvas"></canvas>
<div id="gameOver">Game Over</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreBoard = document.getElementById('scoreBoard');
const gameOver = document.getElementById('gameOver');

// Set canvas size to cover the entire window
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Game variables
let ball = {
  x: canvas.width / 2,
  y: canvas.height / 2,
  radius: 10,
  velocityX: 5,
  velocityY: 5,
  speed: 7,
  color: 'WHITE'
};

let user = {
  x: 0,
  y: (canvas.height - 100) / 2,
  width: 10,
  height: 100,
  score: 0,
  color: 'WHITE'
};

let ai = {
  x: canvas.width - 10,
  y: (canvas.height - 100) / 2,
  width: 10,
  height: 100,
  score: 0,
  color: 'WHITE'
};

let rightPressed = false;
let leftPressed = false;

function drawRect(x, y, w, h, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
}

function drawArc(x, y, r, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI*2, true);
  ctx.closePath();
  ctx.fill();
}

function collision(b, p) {
  p.top = p.y;
  p.bottom = p.y + p.height;
  p.left = p.x;
  p.right = p.x + p.width;

  b.top = b.y - b.radius;
  b.bottom = b.y + b.radius;
  b.left = b.x - b.radius;
  b.right = b.x + b.radius;

  return p.left < b.right && p.top < b.bottom && p.right > b.left && p.bottom > b.top;
}

function resetBall() {
  ball.x = canvas.width / 2;
  ball.y = canvas.height / 2;
  ball.velocityX = -ball.velocityX;
  ball.speed = 7;
}

function drawText(text, x, y, color) {
  ctx.fillStyle = color;
  ctx.font = '24px fantasy';
  ctx.fillText(text, x, y);
}

function aiMovement() {
  if (ai.y < ball.y) {
    ai.y += 5;
  } else if (ai.y > ball.y) {
    ai.y -= 5;
  }
}

function drawScore(user, ai) {
  scoreBoard.querySelector('#playerScore').textContent = user.score;
  scoreBoard.querySelector('#aiScore').textContent = ai.score;
}

function gameLoop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Ball movement
  ball.x += ball.velocityX;
  ball.y += ball.velocityY;

  // Ball collision with top/bottom walls
  if (ball.y - ball.radius < 0 || ball.y + ball.radius > canvas.height) {
    ball.velocityY = -ball.velocityY;
  }

  // AI paddle movement
  aiMovement();

  // User paddle movement
  if (rightPressed && user.y < canvas.height - user.height) {
    user.y += 5;
  } else if (leftPressed && user.y > 0) {
    user.y -= 5;
  }

  // Ball collision with left paddle
 