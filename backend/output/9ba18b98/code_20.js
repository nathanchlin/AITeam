class TetrisGame {
    constructor() {
        // ... 其他初始化代码 ...
        this.score = 0;
        this.linesCleared = 0;
        this.level = 1;
        this.scoreMultiplier = 100; // 基础分数倍数
    }
    
    // 更新分数
    updateLinesCleared(lines) {
        this.linesCleared += lines;
        
        // 根据一次消除的行数计算分数
        let points = 0;
        switch (lines) {
            case 1: // 单行消除
                points = this.scoreMultiplier * this.level;
                break;
            case 2: // 双行消除
                points = this.scoreMultiplier * 2 * this.level;
                break;
            case 3: // 三行消除
                points = this.scoreMultiplier * 3 * this.level;
                break;
            case 4: // 四行消除（Tetris）
                points = this.scoreMultiplier * 4 * this.level;
                break;
        }
        
        this.score += points;
        
        // 每消除10行升一级
        const newLevel = Math.floor(this.linesCleared / 10) + 1;
        if (newLevel > this.level) {
            this.level = newLevel;
            // 可以在这里增加游戏速度
        }
        
        return points;
    }
}