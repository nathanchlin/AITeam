class GameInputHandler {
    private gridSystem: GameGridSystem;
    private selectedGem: Gem | null = null;
    
    constructor(gridSystem: GameGridSystem) {
        this.gridSystem = gridSystem;
        this.setupEventListeners();
    }
    
    private setupEventListeners(): void {
        const canvas = this.gridSystem['renderer']['canvas'];
        
        // 鼠标事件
        canvas.addEventListener('click', (e) => this.handleClick(e));
        
        // 触摸事件
        canvas.addEventListener('touchstart', (e) => this.handleTouch(e));
    }
    
    private handleClick(event: MouseEvent): void {
        const rect = event.target.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const col = Math.floor(x / (this.gridSystem['renderer']['gemSize'] + this.gridSystem['renderer']['padding']));
        const row = Math.floor(y / (this.gridSystem['renderer']['gemSize'] + this.gridSystem['renderer']['padding']));
        
        this.handleGemSelection(row, col);
    }
    
    private handleTouch(event: TouchEvent): void {
        event.preventDefault();
        const rect = event.target.getBoundingClientRect();
        const touch = event.touches[0];
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        const col = Math.floor(x / (this.gridSystem['renderer']['gemSize'] + this.gridSystem['renderer']['padding']));
        const row = Math.floor(y / (this.gridSystem['renderer']['gemSize'] + this.gridSystem['renderer']['padding']));
        
        this.handleGemSelection(row, col);
    }
    
    private handleGemSelection(row: number, col: number): void {
        const gem = this.gridSystem.getGem(row, col);
        
        if (!gem) return;
        
        if (!this.selectedGem) {
            // 选择第一个宝石
            this.selectedGem = gem;
            this.highlightGem(gem, true);
        } else {
            // 尝试交换宝石
            const swapped = this.gridSystem.swapGems(this.selectedGem, gem);
            
            if (swapped) {
                // 检查是否有匹配
                setTimeout(() => {
                    const matches = this.gridSystem.findMatches();
                    
                    if (matches.length > 0) {
                        // 有匹配，移除宝石
                        setTimeout(() => {
                            this.gridSystem.removeMatchedGems();
                        }, 300);
                    } else {
                        // 没有匹配，交换回来
                        setTimeout(() => {
                            this.gridSystem.swapGems(this.selectedGem!, gem);
                        }, 300);
                    }
                }, 300);
            }
            
            // 取消选择
            this.highlightGem(this.selectedGem, false);
            this.selectedGem = null;
        }
    }
    
    private highlightGem(gem: Gem, highlight: boolean): void {
        // 这里可以实现高亮效果，例如改变宝石的缩放
        gem.scale = highlight ? 1.1 : 1;
        this.gridSystem.render();
    }
}