class GameMap {
  constructor(width, height, cellSize) {
    this.width = width;
    this.height = height;
    this.cellSize = cellSize;
    this.grid = [];
    this.walls = [];
    this.dots = [];
    
    this.initializeGrid();
  }

  initializeGrid() {
    for (let y = 0; y < this.height; y++) {
      this.grid[y] = [];
      for (let x = 0; x < this.width; x++) {
        this.grid[y][x] = 0; // 0 = 空地
      }
    }
  }

  // 设置墙壁
  setWall(x, y) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      this.grid[y][x] = 1; // 1 = 墙壁
      this.walls.push({ x: x * this.cellSize, y: y * this.cellSize });
    }
  }

  // 设置豆子
  setDot(x, y) {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height && this.grid[y][x] === 0) {
      this.grid[y][x] = 2; // 2 = 豆子
      this.dots.push({
        x: x * this.cellSize + this.cellSize / 2,
        y: y * this.cellSize + this.cellSize / 2,
        collected: false
      });
    }
  }

  // 获取地图数据
  getTile(x, y) {
    const tileX = Math.floor(x / this.cellSize);
    const tileY = Math.floor(y / this.cellSize);
    
    if (tileX >= 0 && tileX < this.width && tileY >= 0 && tileY < this.height) {
      return this.grid[tileY][tileX];
    }
    return 1; // 边界视为墙壁
  }
}