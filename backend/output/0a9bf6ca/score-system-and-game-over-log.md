# Score System and Game Over Logic

**Time**: 2026-02-25T16:46:52.117805

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
  }
  canvas {
    display: block;
  }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>
<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');

  // Set canvas size
  canvas.width = 800;
  canvas.height = 400;

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
    ctx.font = '75px fantasy';
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
    ctx.font = '75px fantasy';
    ctx.fillStyle = 'WHITE';
    ctx.fillText(user.score, canvas.width / 4, canvas.height - 20);
    ctx.fillText(ai.score, 3 * canvas.width / 4, canvas.height - 20);
  }

  function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Ball movement
    ball.x += ball.velocityX;
    ball.y += ball.velocityY;

    // AI paddle movement
    aiMovement();

    // User paddle movement
    if (rightPressed && user.y < canvas.height - user.height) {
      user.y += 5;
    } else if (leftPressed && user.y > 0) {
      user.y -= 5;
    }

    // Ball collision with top/bottom walls
    if (ball.y - ball.radius < 0 || ball.y + ball.radius > canvas.height) {
      ball.velocityY = -ball.velocityY;
    }

    // Ball collision with left paddle
    if (collision(ball, user) && ball.x - ball.radius < user.x + user.width && ball.y > user.y && ball.y < user.y + user.height) {
      ball.velocityX = -ball.velocityX;
      let collidePoint = (ball.y - user.y) / user.height;
      let angleRad = (Math.PI / 4) * collidePoint;
      let direction = ball.x < user.x ? 1 : -1;
      ball.velocityX = ball.speed * direction * Math.cos(angleRad);
      ball.velocityY = ball.speed * direction * Math.sin(angleRad);
    }

    // Ball collision with right paddle
    if (collision(ball, ai) && ball.x + ball.radius > ai.x && ball.y > ai.y && ball.y < ai.y + ai.height) {
      ball.velocityX = -ball.velocityX;
      let collidePoint = (ball.y - ai.y) / ai.height;
      let angleRad = (Math.PI / 4) * collidePoint;
      let direction = ball.x > ai.x ? 1 : -1;
      ball.velocityX = ball.speed * direction * Math.cos(angleRad);
      ball.velocityY = ball.speed * direction * Math.sin(angleRad);
    }

    // Ball goes past user paddle
    if (ball.x - ball.radius < 0) {
      ai.score++;
      resetBall();
    }

    // Ball goes past AI paddle
    if (ball.x + ball.radius > canvas.width) {
      user.score++;
      resetBall();
    }

    // Draw everything
    drawRect(user.x, user.y, user.width, user.height, user.color);
    drawRect(ai.x, ai.y, ai.width, ai.height, ai.color);
    drawArc(ball.x, ball.y, ball.radius, ball.color);
    drawScore(user, ai);

    // Check for game over
    if (user.score >= 10 || ai.score >= 10) {
      clearInterval(interval);
      drawText('Game Over', canvas.width / 2, canvas.height / 2, 'WHITE');
    }
  }

  let interval = setInterval(gameLoop, 10);

  window.onload = function() {
    document.addEventListener('keydown', function(e) {
      if (e.keyCode === 39) {
        rightPressed = true;
      } else if (e.keyCode === 37) {
        leftPressed = true;
      }
    });

    document.addEventListener('keyup', function(e) {
      if (e.keyCode === 39) {
        rightPressed = false;
      } else if (e.keyCode === 37) {
        leftPressed = false;
      }
    });
  };
</script>
</body>
</html>
```

In this code, the scoring system and game over logic are already implemented. The player's score is incremented when the ball passes through the right paddle, and the AI's score is incremented when the ball passes through the left paddle. The game ends when either player reaches a score of 10. The "Game Over" text is displayed in the center of the canvas when the game ends.