class CustomPhysics {
    constructor() {
        this.gravity = 0.5;
        this.maxVelocity = 15;
    }
    
    applyGravity(player) {
        if (player.body.velocity.y < this.maxVelocity) {
            player.body.velocity.y += this.gravity;
        }
    }
    
    handleJump(player) {
        // 处理跳跃逻辑，包括小跳、大跳等
    }
    
    // 其他物理方法...
}