class Snake {
  constructor(initialLength = 3) {
    // 初始化蛇的位置，从屏幕中央开始
    this.body = [];
    this.direction = 'right'; // 初始方向向右
    this.nextDirection = 'right'; // 用于存储下一个方向，防止180度转向
    
    // 初始化蛇身
    const startX = Math.floor(GRID_WIDTH / 2);
    const startY = Math.floor(GRID_HEIGHT / 2);
    
    for (let i = 0; i < initialLength; i++) {
      this.body.push({ x: startX - i, y: startY });
    }
  }
  
  // 处理键盘输入，改变方向
  changeDirection(newDirection) {
    // 防止180度转向（例如当前向右不能立即向左）
    const opposites = {
      'up': 'down',
      'down': 'up',
      'left': 'right',
      'right': 'left'
    };
    
    if (newDirection !== opposites[this.direction]) {
      this.nextDirection = newDirection;
    }
  }
  
  // 移动蛇
  move() {
    // 更新当前方向
    this.direction = this.nextDirection;
    
    // 获取当前头部位置
    const head = { ...this.body[0] };
    
    // 根据方向计算新头部位置
    switch (this.direction) {
      case 'up':
        head.y -= 1;
        break;
      case 'down':
        head.y += 1;
        break;
      case 'left':
        head.x -= 1;
        break;
      case 'right':
        head.x += 1;
        break;
    }
    
    // 将新头部添加到蛇身前面
    this.body.unshift(head);
    
    // 如果没有吃到食物，移除尾部（保持长度不变）
    // 如果吃到食物，不移除尾部（蛇变长）
    // 这个逻辑需要在游戏主循环中处理
  }
  
  // 检查是否撞墙
  checkWallCollision() {
    const head = this.body[0];
    return (
      head.x < 0 || 
      head.x >= GRID_WIDTH || 
      head.y < 0 || 
      head.y >= GRID_HEIGHT
    );
  }
  
  // 检查是否撞到自己
  checkSelfCollision() {
    const head = this.body[0];
    
    // 检查头部是否与身体其他部分碰撞
    for (let i = 1; i < this.body.length; i++) {
      if (head.x === this.body[i].x && head.y === this.body[i].y) {
        return true;
      }
    }
    
    return false;
  }
  
  // 吃到食物，蛇变长
  eat() {
    // 不移除尾部，蛇会变长
    // 在游戏主循环中调用此方法
  }
  
  // 获取蛇的当前位置（用于渲染）
  getBody() {
    return this.body;
  }
}