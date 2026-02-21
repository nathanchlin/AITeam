class MatchFinder {
  findMatches(grid) {
    const matches = [];
    
    // 查找水平匹配
    for (let row = 0; row < grid.height; row++) {
      for (let col = 0; col < grid.width - 2; col++) {
        const match = this.checkHorizontalMatch(grid, row, col);
        if (match.length >= 3) {
          matches.push(match);
          col += match.length - 1; // 跳过已匹配的格子
        }
      }
    }
    
    // 查找垂直匹配
    for (let col = 0; col < grid.width; col++) {
      for (let row = 0; row < grid.height - 2; row++) {
        const match = this.checkVerticalMatch(grid, row, col);
        if (match.length >= 3) {
          matches.push(match);
          row += match.length - 1; // 跳过已匹配的格子
        }
      }
    }
    
    return matches;
  }
  
  checkHorizontalMatch(grid, row, col) {
    const type = grid[row][col];
    const match = [{ row, col }];
    
    for (let c = col + 1; c < grid.width; c++) {
      if (grid[row][c] === type) {
        match.push({ row, col: c });
      } else {
        break;
      }
    }
    
    return match;
  }
  
  checkVerticalMatch(grid, row, col) {
    const type = grid[row][col];
    const match = [{ row, col }];
    
    for (let r = row + 1; r < grid.height; r++) {
      if (grid[r][col] === type) {
        match.push({ row: r, col });
      } else {
        break;
      }
    }
    
    return match;
  }
}