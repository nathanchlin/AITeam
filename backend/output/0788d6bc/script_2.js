// 游戏主循环中的子弹处理
function gameLoop() {
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 更新游戏状态
    player.update();
    enemies.forEach(enemy => enemy.update());
    bulletManager.update();
    
    // 检查子弹碰撞
    const bulletCollisions = bulletManager.checkCollisions([...enemies, ...walls, player, base]);
    
    // 处理碰撞效果
    bulletCollisions.forEach(collision => {
        // 可以在这里添加碰撞效果，如爆炸动画等
    });
    
    // 绘制游戏元素
    drawMap();
    player.draw(ctx);
    enemies.forEach(enemy => enemy.draw(ctx));
    bulletManager.draw(ctx);
    
    // 继续游戏循环
    requestAnimationFrame(gameLoop);
}