// 地图单元格类型
const CELL_TYPES = {
  EMPTY: 0,      // 空通道
  WALL: 1,       // 墙壁
  DOT: 2,        // 可吃的豆子
  POWER_DOT: 3,  // 能量豆子
  PACMAN: 4,     // 吃豆人起始位置
  GHOST: 5       // 鬼魂起始位置
};

// 游戏地图类
class GameMap {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.grid = [];
    this.cellSize = 30; // 每个格子的大小(像素)
    this.initializeGrid();
  }

  // 初始化网格
  initializeGrid() {
    for (let y = 0; y < this.height; y++) {
      this.grid[y] = [];
      for (let x = 0; x < this.width; x++) {
        this.grid[y][x] = CELL_TYPES.EMPTY;
      }
    }
  }

  // 设置单元格类型
  setCell(x, y, type) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      this.grid[y][x] = type;
    }
  }

  // 获取单元格类型
  getCell(x, y) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      return this.grid[y][x];
    }
    return CELL_TYPES.WALL; // 边界外视为墙壁
  }

  // 创建一个简单的迷宫布局
  createSimpleMaze() {
    // 创建外墙
    for (let x = 0; x < this.width; x++) {
      this.setCell(x, 0, CELL_TYPES.WALL);
      this.setCell(x, this.height - 1, CELL_TYPES.WALL);
    }
    for (let y = 0; y < this.height; y++) {
      this.setCell(0, y, CELL_TYPES.WALL);
      this.setCell(this.width - 1, y, CELL_TYPES.WALL);
    }

    // 创建内部墙壁
    // 水平墙
    for (let x = 2; x < this.width - 2; x++) {
      if (x !== Math.floor(this.width / 2)) {
        this.setCell(x, 3, CELL_TYPES.WALL);
        this.setCell(x, this.height - 4, CELL_TYPES.WALL);
      }
    }
    
    // 垂直墙
    for (let y = 2; y < this.height - 2; y++) {
      if (y !== Math.floor(this.height / 2)) {
        this.setCell(3, y, CELL_TYPES.WALL);
        this.setCell(this.width - 4, y, CELL_TYPES.WALL);
      }
    }

    // 放置豆子
    for (let y = 1; y < this.height - 1; y++) {
      for (let x = 1; x < this.width - 1; x++) {
        if (this.getCell(x, y) === CELL_TYPES.EMPTY) {
          // 随机放置普通豆子和能量豆子
          if (Math.random() < 0.8) {
            this.setCell(x, y, CELL_TYPES.DOT);
          } else if (Math.random() < 0.1) {
            this.setCell(x, y, CELL_TYPES.POWER_DOT);
          }
        }
      }
    }

    // 设置吃豆人起始位置
    this.setCell(Math.floor(this.width / 2), Math.floor(this.height / 2), CELL_TYPES.PACMAN);
    
    // 设置鬼魂起始位置
    this.setCell(2, 2, CELL_TYPES.GHOST);
    this.setCell(this.width - 3, 2, CELL_TYPES.GHOST);
    this.setCell(2, this.height - 3, CELL_TYPES.GHOST);
    this.setCell(this.width - 3, this.height - 3, CELL_TYPES.GHOST);
  }

  // 检查位置是否可通行
  isWalkable(x, y) {
    return this.getCell(x, y) !== CELL_TYPES.WALL;
  }
}