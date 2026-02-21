class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }
    
    preload() {
        // 加载玩家精灵图（假设是4x3的精灵表）
        this.load.spritesheet('player', 'assets/player.png', {
            frameWidth: 32,
            frameHeight: 48
        });
        
        // 加载平台纹理
        this.load.image('platform', 'assets/platform.png');
        
        // 加载音效
        this.load.audio('jump', 'assets/jump.mp3');
        this.load.audio('break', 'assets/break.mp3');
        this.load.audio('gameOver', 'assets/gameOver.mp3');
    }
    
    create() {
        // 初始化游戏状态
        this.floor = 1;
        this.lives = 3;
        this.gameOver = false;
        this.platforms = [];
        this.platformGroup = this.physics.add.group();
        this.cameraSpeed = 2;
        this.lastPlatformY = 600;
        this.platformGap = 120;
        this.minPlatformWidth = 80;
        this.maxPlatformWidth = 150;
        this.platformTypes = ['normal', 'moving', 'breakable', 'spring'];
        this.platformTypeWeights = [50, 20, 20, 10]; // 平台类型权重
        
        // 设置相机
        this.cameras.main.setBounds(0, 0, 400, 3000);
        this.cameras.main.startFollow(this.player);
        
        // 创建玩家
        this.player = new Player(this, 200, 100);
        this.add.existing(this.player);
        
        // 创建初始平台
        this.createInitialPlatforms();
        
        // 设置碰撞检测
        this.physics.add.collider(this.player, this.platformGroup, this.handleCollision, null, this);
        
        // 设置键盘控制
        this.cursors = this.input.keyboard.createCursorKeys();
        this.spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
        
        // 设置游戏事件
        this.events.on('playerFall', this.handlePlayerFall, this);
        
        // 更新UI
        this.updateUI();
    }
    
    createInitialPlatforms() {
        // 创建起始平台
        const startPlatform = new Platform(this, 125, 550, 150, 'normal');
        this.platformGroup.add(startPlatform);
        this.platforms.push(startPlatform);
        this.lastPlatformY = 550;
        
        // 创建初始平台组
        for (let i = 0; i < 10; i++) {
            this.generatePlatform();
        }
    }
    
    generatePlatform() {
        // 随机平台宽度
        const width = Utils.randomInt(this.minPlatformWidth, this.maxPlatformWidth);
        
        // 随机平台类型
        const platformType = this.getRandomPlatformType();
        
        // 随机平台位置
        const x = Utils.randomInt(0, 400 - width);
        const y = this.lastPlatformY - this.platformGap;
        
        // 创建平台
        const platform = new Platform(this, x, y, width, platformType);
        this.platformGroup.add(platform);
        this.platforms.push(platform);
        
        // 更新最后平台Y坐标
        this.lastPlatformY = y;
    }
    
    getRandomPlatformType() {
        // 根据权重随机选择平台类型
        const totalWeight = this.platformTypeWeights.reduce((a, b) => a + b, 0);
        let random = Utils.randomInt(1, totalWeight);
        
        for (let i = 0; i < this.platformTypes.length; i++) {
            random -= this.platformTypeWeights[i];
            if (random <= 0) {
                return this.platformTypes[i];
            }
        }
        
        return 'normal'; // 默认返回普通平台
    }
    
    handleCollision(player, platform) {
        // 处理玩家与平台的碰撞
        if (player.body.touching.down) {
            // 根据平台类型执行不同动作
            switch(platform.type) {
                case 'normal':
                case 'moving':
                    player.land();
                    break;
                    
                case 'spring':
                    player.setVelocityY(platform.springPower);
                    player.isJumping = true;
                    player.jumpCount = 1;
                    this.sound.play('jump');
                    break;
                    
                case 'breakable':
                    // 重置破碎计时器
                    platform.breakTimer = 0;
                    break;
            }
        }
    }
    
    handlePlayerFall() {
        // 玩家掉落处理
        if (this.lives > 0) {
            this.lives--;
            this.updateUI();
            
            if (this.lives > 0) {
                // 重置玩家位置
                this.player.reset();
                
                // 清理下方平台
                this.cleanupPlatforms();
                
                // 调整相机位置
                this.adjustCamera();
            } else {
                this.endGame();
            }
        }
    }
    
    cleanupPlatforms() {
        // 清理玩家下方的平台
        const playerY = this.player.y;
        
        this.platforms = this.platforms.filter(platform => {
            if (platform.y > playerY + 600) {
                platform.destroy();
                return false;
            }
            return true;
        });
    }
    
    adjustCamera() {
        // 调整相机位置，确保玩家在视野中央
        const targetY = this.player.y - 300;
        const currentY = this.cameras.main.scrollY;
        
        // 平滑移动相机
        this.tweens.add({
            targets: this.cameras.main,
            scrollY: targetY,
            duration: 1000,
            ease: 'Power2'
        });
    }
    
    update(time, delta) {
        if (this.gameOver) return;
        
        // 移动相机
        this.cameras.main.scrollY -= this.cameraSpeed;
        
        // 更新楼层
        const newFloor = Math.floor((600 - this.cameras.main.scrollY) / 10) + 1;
        if (newFloor > this.floor) {
            this.floor = newFloor;
            this.updateUI();
            
            // 随着楼层增加，游戏难度提高
            this.increaseDifficulty();
        }
        
        // 检查玩家是否掉出屏幕
        if (this.player.y > this.cameras.main.scrollY + 650) {
            this.events.emit('playerFall');
        }
        
        // 生成新平台
        if (this.lastPlatformY - this.cameras.main.scrollY > 600) {
            this.generatePlatform();
        }
        
        // 更新所有平台
        this.platforms.forEach(platform => {
            platform.update(time, delta);
        });
    }
    
    increaseDifficulty() {
        // 随着楼层增加，提高游戏难度
        this.cameraSpeed = Math.min(this.cameraSpeed + 0.05, 5);
        this.platformGap = Math.min(this.platformGap + 1, 150);
        
        // 随着楼层增加，减少易碎平台比例
        if (this.floor % 10 === 0) {
            this.platformTypeWeights = [60, 20, 10, 10];
        }
        
        // 随着楼层增加，增加移动平台速度
        this.platforms.forEach(platform => {
            if (platform.moving) {
                platform.moveSpeed = Math.min(platform.moveSpeed + 10, 300);
            }
        });
    }
    
    updateUI() {
        document.getElementById('floor').textContent = this.floor;
        document.getElementById('lives').textContent = this.lives;
    }
    
    endGame() {
        this.gameOver = true;
        this.sound.play('gameOver');
        
        // 显示游戏结束界面
        document.getElementById('finalFloor').textContent = this.floor;
        document.getElementById('gameOver').style.display = 'block';
        
        // 设置重新开始按钮
        document.getElementById('restartBtn').onclick = () => {
            this.scene.restart();
            document.getElementById('gameOver').style.display = 'none';
        };
    }
}