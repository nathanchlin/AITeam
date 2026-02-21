class Player extends Phaser.Physics.Arcade.Sprite {
    constructor(scene, x, y) {
        super(scene, x, y, 'player');
        
        // 添加物理属性
        scene.physics.world.enable(this);
        this.setBounce(0.2);
        this.setCollideWorldBounds(true);
        this.body.setGravityY(500);
        
        // 玩家属性
        this.isJumping = false;
        this.jumpCount = 0;
        this.maxJumps = 2; // 允许二段跳
        this.speed = 200;
        this.jumpPower = -400;
        
        // 添加动画
        this.anims.create({
            key: 'idle',
            frames: this.anims.generateFrameNumbers('player', { start: 0, end: 3 }),
            frameRate: 10,
            repeat: -1
        });
        
        this.anims.create({
            key: 'walk',
            frames: this.anims.generateFrameNumbers('player', { start: 4, end: 7 }),
            frameRate: 10,
            repeat: -1
        });
        
        this.anims.create({
            key: 'jump',
            frames: this.anims.generateFrameNumbers('player', { start: 8, end: 11 }),
            frameRate: 10,
            repeat: -1
        });
        
        this.play('idle');
    }
    
    update() {
        // 水平移动
        if (this.scene.cursors.left.isDown) {
            this.setVelocityX(-this.speed);
            this.flipX = true;
            if (this.body.touching.down) {
                this.play('walk');
            }
        } else if (this.scene.cursors.right.isDown) {
            this.setVelocityX(this.speed);
            this.flipX = false;
            if (this.body.touching.down) {
                this.play('walk');
            }
        } else {
            this.setVelocityX(0);
            if (this.body.touching.down) {
                this.play('idle');
            }
        }
        
        // 跳跃
        if (this.scene.cursors.space.isDown && this.jumpCount < this.maxJumps) {
            this.jump();
        }
        
        // 在空中时播放跳跃动画
        if (!this.body.touching.down) {
            this.play('jump');
        }
    }
    
    jump() {
        if (!this.isJumping) {
            this.setVelocityY(this.jumpPower);
            this.jumpCount++;
            this.isJumping = true;
            this.scene.sound.play('jump');
        }
    }
    
    land() {
        this.isJumping = false;
        this.jumpCount = 0;
    }
    
    reset() {
        this.setPosition(200, 100);
        this.setVelocity(0, 0);
        this.jumpCount = 0;
        this.isJumping = false;
        this.play('idle');
    }
}