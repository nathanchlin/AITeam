// 分裂系统
class SplitSystem {
    constructor() {
        this.splitCooldown = 3000; // 3秒冷却
        this.maxSplits = 16; // 最大分裂数量
        this.mergeSpeed = 0.5; // 合并速度
    }
    
    canSplit(player) {
        // 检查冷却时间
        if (player.lastSplit && Date.now() - player.lastSplit < this.splitCooldown) {
            return false;
        }
        
        // 检查分裂数量
        if (player.balls.length >= this.maxSplits) {
            return false;
        }
        
        // 检查球体大小是否足够分裂
        if (player.balls.length > 0 && player.balls[0].size < 20) {
            return false;
        }
        
        return true;
    }
    
    split(player) {
        if (!this.canSplit(player)) return;
        
        // 记录分裂时间
        player.lastSplit = Date.now();
        
        // 分裂逻辑
        const newBalls = [];
        const originalBalls = [...player.balls];
        
        originalBalls.forEach(ball => {
            if (ball.size > 20) {
                // 创建两个小球
                const newSize = ball.size * 0.6; // 分裂后大小为原来的60%
                
                // 第一个球
                const ball1 = {
                    ...ball,
                    size: newSize,
                    x: ball.x - 10,
                    y: ball.y,
                    targetX: ball.x - 10,
                    targetY: ball.y
                };
                
                // 第二个球
                const ball2 = {
                    ...ball,
                    size: newSize,
                    x: ball.x + 10,
                    y: ball.y,
                    targetX: ball.x + 10,
                    targetY: ball.y
                };
                
                newBalls.push(ball1, ball2);
            } else {
                // 太小的球不分裂
                newBalls.push(ball);
            }
        });
        
        player.balls = newBalls;
    }
    
    updateMerge(player) {
        // 更新球体合并逻辑
        player.balls.forEach(ball => {
            if (ball.size < player.originalSize) {
                // 缓慢恢复到原始大小
                ball.size = Math.min(ball.size + this.mergeSpeed, player.originalSize);
            }
        });
    }
}