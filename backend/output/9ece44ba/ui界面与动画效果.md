# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-23T10:53:36.327445

---

为了完成这个任务，我们需要对原始代码进行扩展，以包含得分板和生命值，并添加动画效果。以下是一个更新后的代码示例，它包含了得分板、生命值和简单的动画效果：

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bullet Dodging Game</title>
<style>
  body {
    margin: 0;
    overflow: hidden;
  }
  canvas {
    display: block;
  }
  #lives {
    position: absolute;
    top: 10px;
    left: 10px;
  }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>
<div id="lives">Lives: 3</div>
<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const width = canvas.width = window.innerWidth;
  const height = canvas.height = window.innerHeight;
  let player = {
    x: width / 2,
    y: height - 50,
    width: 30,
    height: 50,
    color: 'blue'
  };
  let bullets = [];
  let score = 0;
  let lives = 3;

  function drawPlayer() {
    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.width, player.height);
  }

  function drawBullet() {
    ctx.fillStyle = 'red';
    for (let bullet of bullets) {
      ctx.fillRect(bullet.x, bullet.y, 5, 10);
      bullet.x += 5;
    }
    bullets = bullets.filter(bullet => bullet.x < width);
  }

  function drawScore() {
    ctx.fillStyle = 'black';
    ctx.fillText(`Score: ${score}`, 10, 30);
  }

  function drawLives() {
    ctx.fillStyle = 'green';
    for (let i = 0; i < lives; i++) {
      ctx.fillRect(10 + i * 20, 40, 10, 10);
    }
  }

  function collisionCheck() {
    for (let bullet of bullets) {
      if (player.x < bullet.x + 5 && player.x + player.width > bullet.x &&
          player.y < bullet.y + 10 && player.y + player.height > bullet.y) {
        lives--;
        if (lives <= 0) {
          alert('Game Over! Score: ' + score);
          score = 0;
          lives = 3;
          player.x = width / 2;
          player.y = height - 50;
          bullets = [];
        }
        return true;
      }
    }
    return false;
  }

  function gameLoop() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);
    drawPlayer();
    drawBullet();
    drawScore();
    drawLives();

    if (collisionCheck()) {
      // Simple animation effect: player shakes when hit
      player.x += (player.x < width / 2 ? 1 : -1);
      player.y += (player.y < height - 50 ? 1 : -1);
    }

    requestAnimationFrame(gameLoop);
  }

  window.onload = function() {
    gameLoop();
    document.addEventListener('keydown', function(event) {
      if (event.key === 'ArrowLeft') {
        player.x -= 10;
      } else if (event.key === 'ArrowRight') {
        player.x += 10;
      }
      if (player.x < 0) player.x = 0;
      if (player.x > width - player.width) player.x = width - player.width;
    });

    setInterval(function() {
      bullets.push({
        x: Math.random() * (width - 5),
        y: 0
      });
    }, 500);
  };
</script>
</body>
</html>
```

在这个代码中，我做了以下修改和添加：

1. 添加了一个`div`元素来显示生命值（`#lives`）。
2. 创建了一个`drawLives`函数来绘制生命值，每个生命值用一个绿色的方块表示。
3. 修改了`collisionCheck`函数，当玩家被击中时，生命值会减少，并在生命值耗尽时结束游戏。
4. 在`gameLoop`函数中添加了一个简单的动画效果：当玩家被击中时，会轻微地抖动。

这段代码提供了一个带有得分板、生命值和简单动画效果的躲避弹幕游戏。玩家可以通过左右箭头键控制角色移动，躲避不断下落的弹幕。如果玩家被弹幕击中，生命值会减少，并在生命值耗尽时游戏结束。