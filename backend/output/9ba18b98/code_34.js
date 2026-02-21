// 优化前
for (let y = 0; y < gridHeight; y++) {
  for (let x = 0; x < gridWidth; x++) {
    if (grid[y][x]) {
      drawBlock(x, y, grid[y][x]);
    }
  }
}

// 优化后
ctx.beginPath();
for (let y = 0; y < gridHeight; y++) {
  for (let x = 0; x < gridWidth; x++) {
    if (grid[y][x]) {
      ctx.rect(x * blockSize, y * blockSize, blockSize, blockSize);
    }
  }
}
ctx.fillStyle = 'blue';
ctx.fill();