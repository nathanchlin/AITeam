class Game {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.state = new GameState();
    this.lastTime = 0;
    this.init();
  }
  
  init() {
    // 初始化游戏
    this.setupEventListeners();
    this.loadLevel(1);
    this.gameLoop();
  }
  
  setupEventListeners() {
    // 设置键盘事件监听
    document.addEventListener('keydown', (e) => {
      this.state.keys[e.key] = true;
    });
    
    document.addEventListener('keyup', (e) => {
      this.state.keys[e.key] = false;
    });
  }
  
  loadLevel(level) {
    // 加载关卡
    // 初始化地图、敌人和玩家
  }
  
  gameLoop(currentTime = 0) {
    const deltaTime = currentTime - this.lastTime;
    this.lastTime = currentTime;
    
    // 更新游戏状态
    this.update(deltaTime);
    
    // 渲染游戏
    this.render();
    
    // 继续循环
    requestAnimationFrame((time) => this.gameLoop(time));
  }
  
  update(deltaTime) {
    // 更新所有实体
    // 处理输入
    // 检测碰撞
    // 更新游戏状态
  }
  
  render() {
    // 清空画布
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // 渲染地图
    this.renderMap();
    
    // 渲染所有实体
    this.state.entities.forEach(entity => {
      this.renderEntity(entity);
    });
    
    // 渲染UI
    this.renderUI();
  }
  
  renderEntity(entity) {
    // 根据实体类型渲染
    if (entity instanceof Tank) {
      this.renderTank(entity);
    } else if (entity instanceof Bullet) {
      this.renderBullet(entity);
    } else if (entity instanceof Headquarters) {
      this.renderHeadquarters(entity);
    }
  }
  
  // 其他渲染方法...
}