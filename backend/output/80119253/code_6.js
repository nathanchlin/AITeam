class Board {
  constructor(size) {
    this.size = size;
    this.grid = Array(size).fill(null).map(() => Array(size).fill(null));
  }

  placePiece(x, y, player) {
    this.grid[y][x] = player;
  }

  removePiece(x, y) {
    this.grid[y][x] = null;
  }

  isOccupied(x, y) {
    return this.grid[y][x] !== null;
  }

  hasPiece(x, y, player) {
    return this.grid[y][x] === player;
  }

  isValidPosition(x, y) {
    return x >= 0 && x < this.size && y >= 0 && y < this.size;
  }

  isFull() {
    for (let y = 0; y < this.size; y++) {
      for (let x = 0; x < this.size; x++) {
        if (this.grid[y][x] === null) {
          return false;
        }
      }
    }
    return true;
  }

  reset() {
    this.grid = Array(this.size).fill(null).map(() => Array(this.size).fill(null));
  }

  getState() {
    return {
      size: this.size,
      grid: this.grid
    };
  }
}