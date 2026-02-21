rotate() {
    // 创建旋转后的形状
    const rotated = [];
    const rows = this.shape.length;
    const cols = this.shape[0].length;
    
    for (let i = 0; i < cols; i++) {
        rotated[i] = [];
        for (let j = rows - 1; j >= 0; j--) {
            rotated[i][rows - 1 - j] = this.shape[j][i];
        }
    }
    
    // 检查旋转后是否合法
    if (this.isValidMove(this.x, this.y, rotated)) {
        this.shape = rotated;
    }
}