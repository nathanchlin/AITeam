class TetrisGame {
    // ... 其他方法 ...
    
    update() {
        // ... 方块移动和旋转逻辑 ...
        
        // 检查是否有行需要消除
        const linesToClear = checkLines(this.board);
        
        if (linesToClear.length > 0) {
            // 开始消除动画
            this.startLineClearAnimation(linesToClear);
            
            // 等待动画完成后实际消除行
            setTimeout(() => {
                const clearedLines = clearLines(this.board, linesToClear);
                const points = this.updateLinesCleared(clearedLines);
                
                // 可以在这里添加得分提示
                console.log(`消除了 ${clearedLines} 行，获得 ${points} 分！`);
            }, this.animationDuration);
        }
    }
}