class Player extends Phaser.Physics.Arcade.Sprite {
    constructor(scene, x, y) {
        super(scene, x, y, 'mario-sprite');
        
        // 初始化物理属性
        scene.physics.add.existing(this);
        this.setBounce(0.2);
        this.setCollideWorldBounds(true);
        
        // 动画
        this.anims.create({
            key: 'left',
            frames: this.anims.generateFrameNumbers('mario-sprite', { start: 0, end: 3 }),
            frameRate: 10,
            repeat: -1
        });
        // 其他动画...
        
        // 输入处理
        this.cursors = scene.input.keyboard.createCursorKeys();
    }
    
    update() {
        // 玩家移动逻辑
        if (this.cursors.left.isDown) {
            this.setVelocityX(-160);
            this.anims.play('left', true);
        } else if (this.cursors.right.isDown) {
            this.setVelocityX(160);
            this.anims.play('right', true);
        } else {
            this.setVelocityX(0);
        }
        
        if (this.cursors.up.isDown && this.body.touching.down) {
            this.setVelocityY(-330);
        }
    }
    
    // 其他方法...
}