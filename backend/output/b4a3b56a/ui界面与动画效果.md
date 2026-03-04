# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-24T17:48:29.495050

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>飞机大战游戏</title>
<style>
  canvas {
    border: 1px solid black;
  }
</style>
</head>
<body>
<canvas id="gameCanvas" width="800" height="600"></canvas>
<script>
// 游戏配置
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const gameWidth = canvas.width;
const gameHeight = canvas.height;
let score = 0;

// 飞机类
class Plane {
  constructor(x, y, width, height, color) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.color = color;
  }

  draw() {
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }

  move(x, y) {
    this.x = x;
    this.y = y;
  }
}

// 敌机类
class Enemy {
  constructor(x, y, width, height, color) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.color = color;
    this.speed = Math.random() * 2 + 1;
  }

  draw() {
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }

  move() {
    this.y += this.speed;
  }
}

// 爆炸动画类
class Explosion {
  constructor(x, y, frames) {
    this.x = x;
    this.y = y;
    this.frames = frames;
    this.currentFrame = 0;
  }

  draw() {
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(this.x, this.y, 10 * (this.currentFrame + 1), 0, Math.PI * 2, true);
    ctx.fill();
  }

  update() {
    if (this.currentFrame < this.frames) {
      this.currentFrame++;
    } else {
      this.currentFrame = 0;
    }
  }
}

// 创建飞机
const player = new Plane(gameWidth / 2, gameHeight - 50, 50, 50, 'blue');

// 敌机数组
const enemies = [];
for (let i = 0; i < 5; i++) {
  enemies.push(new Enemy(Math.random() * (gameWidth - 50), 0, 50, 50, 'red'));
}

// 子弹数组
const bullets = [];

// 爆炸数组
const explosions = [];

// 绘制得分板
function drawScore() {
  ctx.fillStyle = 'white';
  ctx.fillText('Score: ' + score, 10, 20);
}

// 游戏循环
function gameLoop() {
  ctx.clearRect(0, 0, gameWidth, gameHeight);
  player.draw();
  drawScore();

  // 敌机移动和绘制
  for (let enemy of enemies) {
    enemy.move();
    enemy.draw();
    if (enemy.y > gameHeight) {
      enemies.shift();
      score++;
    }
  }

  // 子弹移动和绘制
  for (let bullet of bullets) {
    bullet.move();
    bullet.draw();
    if (bullet.y < 0) {
      bullets.shift();
    }
  }

  // 爆炸动画
  for (let explosion of explosions) {
    explosion.draw();
    explosion.update();
    if (explosion.currentFrame === 0) {
      explosions.shift();
    }
  }

  // 检测碰撞
  for (let enemy of enemies) {
    for (let bullet of bullets) {
      if (bullet.x < enemy.x + enemy.width &&
          bullet.x + bullet.width > enemy.x &&
          bullet.y < enemy.y + enemy.height &&
          bullet.y + bullet.height > enemy.y) {
        enemies.shift();
        bullets.shift();
        score++;
        explosions.push(new Explosion(enemy.x, enemy.y, 5));
      }
    }
  }

  requestAnimationFrame(gameLoop);
}

// 键盘事件绑定
document.addEventListener('keydown', (e) => {
  let newX = player.x;
  let newY = player.y;
  switch (e.key) {
    case 'ArrowLeft':
      newX = Math.max(0, player.x - 10);
      break;
    case 'ArrowRight':
      newX = Math.min(player.x + 10, gameWidth - player.width);
      break;
    case 'ArrowUp':
      newY = Math.max(0, player.y - 10);
      break;
    case 'ArrowDown':
      newY = Math.min(player.y + 10, gameHeight - player.height);
      break;
    case ' ':
      bullets.push(new Bullet(player.x + player.width / 2, player.y, 5, 10, 'green'));
      break;
  }
  player.move(newX, newY);
});

// 初始化游戏
window.onload = gameLoop;
</script>
</body>
</html>
```

这段代码实现了一个简单的飞机大战游戏，包含飞机的移动、射击、敌机移动、得分板、以及敌机被击中后的爆炸动画效果。游戏使用原生Canvas API进行开发，不依赖任何外部库或框架。