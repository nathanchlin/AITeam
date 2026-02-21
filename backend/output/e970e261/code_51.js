class PreloadScene extends Phaser.Scene {
    constructor() {
        super({ key: 'PreloadScene' });
    }

    preload() {
        // 显示加载进度条
        let loadingText = this.add.text(400, 300, '加载中...', { 
            fontSize: '24px', 
            fill: '#ffffff' 
        });
        this.load.on('progress', function (progress) {
            loadingText.setText(`加载中... ${Math.round(progress * 100)}%`);
        });

        // 加载精灵图集
        this.load.spritesheet('mario', 'assets/images/mario.png', {
            frameWidth: 32,
            frameHeight: 32
        });
        
        this.load.spritesheet('enemies', 'assets/images/enemies.png', {
            frameWidth: 32,
            frameHeight: 32
        });
        
        // 加载地图瓦片
        this.load.tilemapTiledJSON('map', 'assets/maps/level1.json');
        this.load.image('tiles', 'assets/images/tiles.png');
        
        // 加载音效
        this.load.audio('jump', 'assets/sounds/jump.wav');
        this.load.audio('coin', 'assets/sounds/coin.wav');
        this.load.audio('die', 'assets/sounds/die.wav');
    }

    create() {
        // 资源加载完成后的处理
        this.load.on('filecomplete', function (key, type, data) {
            console.log(`资源加载完成: ${key}`);
        });
        
        // 所有资源加载完成后切换到游戏场景
        this.scene.start('GameScene');
    }
}