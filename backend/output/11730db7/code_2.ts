class GameGridSystem {
    private grid: GameGrid;
    private renderer: GemRenderer;
    
    constructor(rows: number, cols: number, renderer: GemRenderer) {
        this.renderer = renderer;
        this.grid = this.initializeGrid(rows, cols);
        this.renderer.resizeCanvas(this.grid);
        this.fillGrid();
        this.renderer.renderGrid(this.grid);
    }
    
    // 初始化网格
    private initializeGrid(rows: number, cols: number): GameGrid {
        const gems: Gem[][] = [];
        for (let row = 0; row < rows; row++) {
            gems[row] = [];
            for (let col = 0; col < cols; col++) {
                gems[row][col] = null;
            }
        }
        
        return {
            rows,
            cols,
            gems
        };
    }
    
    // 填充网格（确保没有初始匹配）
    private fillGrid(): void {
        const gemTypes = Object.values(GemType);
        
        for (let row = 0; row < this.grid.rows; row++) {
            for (let col = 0; col < this.grid.cols; col++) {
                let gemType: GemType;
                let attempts = 0;
                const maxAttempts = 50;
                
                // 确保不会创建初始匹配
                do {
                    gemType = gemTypes[Math.floor(Math.random() * gemTypes.length)];
                    attempts++;
                } while (this.wouldCreateMatch(row, col, gemType) && attempts < maxAttempts);
                
                this.grid.gems[row][col] = {
                    id: `${row}-${col}-${Date.now()}`,
                    type: gemType,
                    row,
                    col,
                    isMatched: false,
                    scale: 1
                };
            }
        }
    }
    
    // 检查是否会产生匹配
    private wouldCreateMatch(row: number, col: number, type: GemType): boolean {
        // 检查水平方向
        if (col >= 2 && 
            this.grid.gems[row][col-1]?.type === type && 
            this.grid.gems[row][col-2]?.type === type) {
            return true;
        }
        
        // 检查垂直方向
        if (row >= 2 && 
            this.grid.gems[row-1][col]?.type === type && 
            this.grid.gems[row-2][col]?.type === type) {
            return true;
        }
        
        return false;
    }
    
    // 获取指定位置的宝石
    public getGem(row: number, col: number): Gem | null {
        if (row >= 0 && row < this.grid.rows && col >= 0 && col < this.grid.cols) {
            return this.grid.gems[row][col];
        }
        return null;
    }
    
    // 交换两个宝石
    public swapGems(gem1: Gem, gem2: Gem): boolean {
        // 检查是否相邻
        const isAdjacent = 
            (Math.abs(gem1.row - gem2.row) === 1 && gem1.col === gem2.col) ||
            (Math.abs(gem1.col - gem2.col) === 1 && gem1.row === gem2.row);
            
        if (!isAdjacent) return false;
        
        // 交换位置
        const tempRow = gem1.row;
        const tempCol = gem1.col;
        
        gem1.row = gem2.row;
        gem1.col = gem2.col;
        gem2.row = tempRow;
        gem2.col = tempCol;
        
        // 更新网格
        this.grid.gems[gem1.row][gem1.col] = gem1;
        this.grid.gems[gem2.row][gem2.col] = gem2;
        
        // 重新渲染
        this.renderer.renderGrid(this.grid);
        
        return true;
    }
    
    // 查找并标记匹配的宝石
    public findMatches(): Gem[] {
        const matchedGems: Gem[] = [];
        
        // 检查水平匹配
        for (let row = 0; row < this.grid.rows; row++) {
            for (let col = 0; col < this.grid.cols - 2; col++) {
                const gem = this.grid.gems[row][col];
                if (gem && !gem.isMatched) {
                    const gem2 = this.grid.gems[row][col + 1];
                    const gem3 = this.grid.gems[row][col + 2];
                    
                    if (gem2 && gem3 && 
                        gem.type === gem2.type && 
                        gem.type === gem3.type) {
                        
                        // 标记匹配的宝石
                        gem.isMatched = true;
                        gem2.isMatched = true;
                        gem3.isMatched = true;
                        
                        matchedGems.push(gem, gem2, gem3);
                        
                        // 检查是否有更多匹配（4个或5个）
                        let k = col + 3;
                        while (k < this.grid.cols) {
                            const nextGem = this.grid.gems[row][k];
                            if (nextGem && nextGem.type === gem.type) {
                                nextGem.isMatched = true;
                                matchedGems.push(nextGem);
                                k++;
                            } else {
                                break;
                            }
                        }
                    }
                }
            }
        }
        
        // 检查垂直匹配
        for (let col = 0; col < this.grid.cols; col++) {
            for (let row = 0; row < this.grid.rows - 2; row++) {
                const gem = this.grid.gems[row][col];
                if (gem && !gem.isMatched) {
                    const gem2 = this.grid.gems[row + 1][col];
                    const gem3 = this.grid.gems[row + 2][col];
                    
                    if (gem2 && gem3 && 
                        gem.type === gem2.type && 
                        gem.type === gem3.type) {
                        
                        // 标记匹配的宝石
                        gem.isMatched = true;
                        gem2.isMatched = true;
                        gem3.isMatched = true;
                        
                        matchedGems.push(gem, gem2, gem3);
                        
                        // 检查是否有更多匹配（4个或5个）
                        let k = row + 3;
                        while (k < this.grid.rows) {
                            const nextGem = this.grid.gems[k][col];
                            if (nextGem && nextGem.type === gem.type) {
                                nextGem.isMatched = true;
                                matchedGems.push(nextGem);
                                k++;
                            } else {
                                break;
                            }
                        }
                    }
                }
            }
        }
        
        return matchedGems;
    }
    
    // 移除匹配的宝石
    public removeMatchedGems(): void {
        for (let row = 0; row < this.grid.rows; row++) {
            for (let col = 0; col < this.grid.cols; col++) {
                const gem = this.grid.gems[row][col];
                if (gem && gem.isMatched) {
                    this.grid.gems[row][col] = null;
                }
            }
        }
        
        // 应用重力效果
        this.applyGravity();
        
        // 填充空缺
        this.fillEmptySpaces();
        
        // 重新渲染
        this.renderer.renderGrid(this.grid);
    }
    
    // 应用重力效果
    private applyGravity(): void {
        for (let col = 0; col < this.grid.cols; col++) {
            // 从底部向上检查
            let emptyRow = this.grid.rows - 1;
            
            for (let row = this.grid.rows - 1; row >= 0; row--) {
                if (this.grid.gems[row][col] !== null) {
                    if (row !== emptyRow) {
                        // 移动宝石
                        this.grid.gems[emptyRow][col] = this.grid.gems[row][col];
                        this.grid.gems[emptyRow][col]!.row = emptyRow;
                        this.grid.gems[row][col] = null;
                    }
                    emptyRow--;
                }
            }
        }
    }
    
    // 填充空缺位置
    private fillEmptySpaces(): void {
        const gemTypes = Object.values(GemType);
        
        for (let col = 0; col < this.grid.cols; col++) {
            for (let row = 0; row < this.grid.rows; row++) {
                if (this.grid.gems[row][col] === null) {
                    this.grid.gems[row][col] = {
                        id: `${row}-${col}-${Date.now()}`,
                        type: gemTypes[Math.floor(Math.random() * gemTypes.length)],
                        row,
                        col,
                        isMatched: false,
                        scale: 1
                    };
                }
            }
        }
    }
    
    // 渲染网格
    public render(): void {
        this.renderer.renderGrid(this.grid);
    }
}