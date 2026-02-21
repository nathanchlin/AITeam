// 游戏主类
class Game {
  constructor(canvasId) {
    this.renderer = new Renderer(canvasId);
    this.stateMachine = new GameStateMachine();
    this.inputManager = new InputManager();
    this.audioManager = new AudioManager();
    this.entities = [];
    this.map = null;
    this.player = null;
    
    this.lastTime = 0;
    this.running = false;
    
    this.initializeStates();
    this.initializeMap();
    this.initializeEntities();
  }

  initializeStates() {
    this.stateMachine.addState('menu', new MenuState());
    this.stateMachine.addState('play', new PlayState());
    this.stateMachine.addState('pause', new PauseState());
    this.stateMachine.addState('gameOver', new GameOverState());
    
    this.stateMachine.changeState('menu');
  }

  initializeMap() {
    this.map = new GameMap(19, 19, 30);
    
    // 创建经典吃豆子地图
    // 这里简化了实际地图生成逻辑
    for (let y = 0; y < this.map.height; y++) {
      for (let x = 0; x < this.map.width; x++) {
        if (x === 0 || x === this.map.width - 1 || 
            y === 0 || y === this.map.height - 1 ||
            (x % 2 === 0 && y % 2 === 0)) {
          this.map.setWall(x, y);
        } else if (Math.random() > 0.3) {
          this.map.setDot(x, y);
        }
      }
    }
  }

  initializeEntities() {
    // 创建玩家
    this.player = new Entity(15 * this.map.cellSize, 15 * this.map.cellSize);
    this.player.addComponent(new MovementComponent(150))
              .addComponent(new CollisionComponent(this.map.cellSize, this.map.cellSize))
              .addComponent(new PlayerComponent());
    
    // 创建敌人
    const enemyPositions = [
      { x: 1 * this.map.cellSize, y: 1 * this.map.cellSize },
      { x: 17 * this.map.cellSize, y: 1 * this.map.cellSize },
      { x: 1 * this.map.cellSize, y: 17 * this.map.cellSize },
      { x: 17 * this.map.cellSize, y: 17 * this.map.cellSize }
    ];
    
    enemyPositions.forEach(pos => {
      const enemy = new Entity(pos.x, pos.y);
      enemy.addComponent(new MovementComponent(100))
            .addComponent(new CollisionComponent(this.map.cellSize, this.map.cellSize))
            .addComponent(new EnemyAIComponent());
      this.entities.push(enemy);
    });
    
    this.entities.push(this.player);
  }

  start() {
    this.running = true;
    this.lastTime = performance.now();
    this.gameLoop();
  }

  gameLoop() {
    if (!this.running) return;
    
    const currentTime = performance.now();
    const deltaTime = (currentTime - this.lastTime) / 1000;
    this.lastTime = currentTime;
    
    this.update(deltaTime);
    this.render();
    
    requestAnimationFrame(() => this.gameLoop());
  }

  update(deltaTime) {
    this.inputManager.update();
    this.stateMachine.update(deltaTime);
    
    // 更新所有实体
    this.entities.forEach(entity => {
      entity.update(deltaTime);
    });
    
    // 碰撞检测
    this.checkCollisions();
  }

  render() {
    this.renderer.clear();
    
    // 渲染地图
    this.renderMap();
    
    // 渲染实体
    this.entities.forEach(entity => {
      this.renderer.render(entity);
    });
    
    // 渲染UI
    this.renderUI();
  }

  renderMap() {
    const ctx = this.renderer.ctx;
    
    // 渲染墙壁
    ctx.fillStyle = '#0000FF';
    this.map.walls.forEach(wall => {
      ctx.fillRect(wall.x, wall.y, this.map.cellSize, this.map.cellSize);
    });
    
    // 渲染豆子
    ctx.fillStyle = '#FFFF00';
    this.map.dots.forEach(dot => {
      if (!dot.collected) {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  }

  renderUI() {
    // 渲染分数
    const score = this.player ? this.player.getComponent('PlayerComponent').score : 0;
    this.renderer.renderText(`Score: ${score}`, 10, 30);
  }

  checkCollisions() {
    // 检查玩家与豆子的碰撞
    const playerCollision = this.player.getComponent('CollisionComponent');
    
    this.map.dots.forEach(dot => {
      if (!dot.collected) {
        const dotEntity = { entity: { x: dot.x - this.map.cellSize/2, y: dot.y - this.map.cellSize/2, width: this.map.cellSize, height: this.map.cellSize } };
        if (playerCollision.checkCollision(dotEntity)) {
          dot.collected = true;
          const playerComponent = this.player.getComponent('PlayerComponent');
          playerComponent.score += 10;
          
          // 检查是否收集完所有豆子
          if (this.map.dots.every(d => d.collected)) {
            this.stateMachine.changeState('gameWin');
          }
        }
      }
    });
    
    // 检查玩家与敌人的碰撞
    this.entities.forEach(entity => {
      if (entity !== this.player) {
        const enemyCollision = entity.getComponent('CollisionComponent');
        if (enemyCollision && enemyCollision.checkCollision(playerCollision)) {
          this.stateMachine.changeState('gameOver');
        }
      }
    });
  }
}