// 方块合并动画
function animateMerge(cell1, cell2, newValue) {
    const mergedCell = document.getElementById(`cell-${cell1.row}-${cell1.col}`);
    
    // 创建合并动画效果
    mergedCell.style.transform = 'scale(1.2)';
    mergedCell.style.backgroundColor = '#ffeb3b';
    
    setTimeout(() => {
        mergedCell.style.transform = 'scale(1)';
        mergedCell.textContent = newValue;
        updateCellColor(mergedCell, newValue);
    }, 200);
}

// 新方块出现动画
function animateNewTile(row, col) {
    const cell = document.getElementById(`cell-${row}-${col}`);
    cell.style.opacity = '0';
    cell.style.transform = 'scale(0)';
    
    setTimeout(() => {
        cell.style.transition = 'all 0.15s ease-in-out';
        cell.style.opacity = '1';
        cell.style.transform = 'scale(1)';
    }, 10);
}