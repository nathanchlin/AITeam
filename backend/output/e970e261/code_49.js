// 游戏配置
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-container',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 1000 },
            debug: false
        }
    },
    scene: [BootScene, PreloadScene, GameScene]
};

// 创建游戏实例
const game = new Phaser.Game(config);

// 性能监控变量
let frameCount = 0;
let lastFpsUpdate = 0;
let currentFps = 0;
let performanceMetrics = {
    fps: 0,
    memory: 0,
    enemies: 0,
    platforms: 0
};

// 引入Phaser命名空间
const Phaser = window.Phaser;