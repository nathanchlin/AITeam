class BootScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BootScene' });
    }

    preload() {
        // 加载启动画面资源
        this.load.image('boot-screen', 'assets/images/boot-screen.png');
    }

    create() {
        // 显示启动画面
        this.add.image(400, 300, 'boot-screen');
        
        // 添加错误处理
        this.load.on('loaderror', (file) => {
            console.error(`资源加载失败: ${file.key}`);
            // 使用默认资源或显示错误信息
        });
        
        // 初始化完成后切换到预加载场景
        this.time.delayedCall(1000, () => {
            this.scene.start('PreloadScene');
        });
    }
}