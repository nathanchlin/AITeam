// 游戏状态对象
const gameState = {
    score: 0,
    isGameOver: false,
    player: {
        x: 400,
        y: 500,
        width: 30,
        height: 30,
        speed: 3,
        direction: 'up',
        lastShot: 0,
        shotCooldown: 300
    },
    enemies: [],
    bullets: [],
    obstacles: [],
    keys: {}
};