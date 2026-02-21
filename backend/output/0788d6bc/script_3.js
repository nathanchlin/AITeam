// 初始化子弹管理器
const bulletManager = new BulletManager();

// 玩家发射子弹
function playerShoot() {
    bulletManager.fire(
        player.x, 
        player.y, 
        player.direction, 
        'player'
    );
}

// 敌人发射子弹
function enemyShoot(enemy) {
    bulletManager.fire(
        enemy.x, 
        enemy.y, 
        enemy.direction, 
        'enemy'
    );
}

// 设置键盘事件监听
document.addEventListener('keydown', (e) => {
    if (e.key === ' ' && !player.isShooting) { // 空格键发射子弹
        playerShoot();
        player.isShooting = true;
        setTimeout(() => player.isShooting = false, 300); // 射击冷却时间
    }
});