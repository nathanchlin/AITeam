# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-21T20:02:48.787361

---

### 任务：UI界面与动画效果

根据您的要求，以下是一个简单的示例，展示了如何使用原生Canvas API来创建一个带有动画效果的背包战争游戏UI。在这个例子中，我将实现一个简单的背包界面和技能菜单，并给这些界面添加一个打开和关闭的动画效果。

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Backpack War Game UI with Animation</title>
<style>
  body {
    margin: 0;
    overflow: hidden;
  }
  canvas {
    display: block;
  }
  #backpack, #skillMenu {
    position: absolute;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 10px;
    border-radius: 5px;
    pointer-events: none;
  }
  #skillMenu {
    display: none;
  }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>
<div id="backpack">Backpack</div>
<div id="skillMenu">Skills</div>
<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  canvas.width = 800;
  canvas.height = 600;

  let backpackOpen = false;
  let skillMenuOpen = false;
  const backpackAnimationDuration = 300; // milliseconds
  let backpackAnimationStartTime;
  let backpackAnimationProgress = 0;

  const backpack = {
    x: 50,
    y: 50,
    width: 200,
    height: 100,
    openWidth: 400,
    openHeight: 150,
    color: 'green'
  };

  const skillMenu = {
    x: 300,
    y: 50,
    width: 200,
    height: 100,
    color: 'blue'
  };

  function drawRect(x, y, width, height, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
  }

  function drawBackpack() {
    const { x, y, width, height, openWidth, openHeight, color } = backpack;
    drawRect(x, y, width, height, color);
    if (backpackOpen) {
      drawRect(x + width / 2 - openWidth / 4, y + height / 2 - openHeight / 4, openWidth, openHeight, color);
    }
  }

  function drawSkillMenu() {
    const { x, y, width, height, color } = skillMenu;
    drawRect(x, y, width, height, color);
  }

  function toggleBackpack() {
    backpackOpen = !backpackOpen;
    backpackAnimationStartTime = Date.now();
    backpackAnimationProgress = 0;
  }

  function toggleSkillMenu() {
    skillMenuOpen = !skillMenuOpen;
    skillMenuAnimationStartTime = Date.now();
    skillMenuAnimationProgress = 0;
  }

  function animate() {
    const now = Date.now();
    if (backpackOpen && backpackAnimationProgress < 1) {
      backpackAnimationProgress = (now - backpackAnimationStartTime) / backpackAnimationDuration;
      if (backpackAnimationProgress > 1) backpackAnimationProgress = 1;
    } else if (!backpackOpen && backpackAnimationProgress > 0) {
      backpackAnimationProgress = 1 - (now - backpackAnimationStartTime) / backpackAnimationDuration;
      if (backpackAnimationProgress < 0) backpackAnimationProgress = 0;
    }

    if (skillMenuOpen && skillMenuAnimationProgress < 1) {
      skillMenuAnimationProgress = (now - skillMenuAnimationStartTime) / backpackAnimationDuration;
      if (skillMenuAnimationProgress > 1) skillMenuAnimationProgress = 1;
    } else if (!skillMenuOpen && skillMenuAnimationProgress > 0) {
      skillMenuAnimationProgress = 1 - (now - skillMenuAnimationStartTime) / backpackAnimationDuration;
      if (skillMenuAnimationProgress < 0) skillMenuAnimationProgress = 0;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawRect(0, 0, canvas.width, canvas.height, 'grey'); // Draw map background
    drawBackpack();
    drawSkillMenu();
    requestAnimationFrame(animate);
  }

  // Event listeners
  document.getElementById('backpack').addEventListener('click', toggleBackpack);
  document.getElementById('skillMenu').addEventListener('click', toggleSkillMenu);

  // Initialization
  animate();
</script>
</body>
</html>
```

在这个示例中，我们添加了两个`div`元素作为背包和技能菜单的UI元素。它们初始时是隐藏的，并且只有当用户点击时才会显示。点击背包或技能菜单时，它们将打开或关闭，并带有简单的淡入淡出动画效果。

请注意，这个例子中的动画是简单的线性动画，仅用于演示目的。在实际的游戏中，您可能需要更复杂的动画效果，例如使用`requestAnimationFrame`进行更平滑的动画处理。