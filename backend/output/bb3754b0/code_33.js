class Pipe {
    // ... 其他代码
    
    update() {
        this.x -= 3;
        
        // 检查是否通过管道
        if (!this.passed && this.x + this.width < bird.x) {
            this.passed = true;
            score++;
            currentScoreElement.textContent = score;
        }
    }
    
    // ... 其他代码
}