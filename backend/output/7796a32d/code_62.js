class Platform extends Phaser.Physics.Arcade.Sprite {
    constructor(scene, x, y, width, type = 'normal') {
        super(scene, x, y, 'platform');
        
        // 设置物理属性
        scene.physics.world.enable(this);
        this.body.setImmovable(true);
        this.body.allowGravity = false;
        
        // 设置平台尺寸
        this.setDisplaySize(width, 20);
        
        // 平台类型
        this.type = type;
        
        // 根据类型设置不同属性
        switch(type) {
            case 'normal':
                this.tint = 0x00ff00; // 绿色普通平台
                this.breakable = false;
                this.moving = false;
                break;
                
            case 'moving':
                this.tint = 0x0000ff; // 蓝色移动平台
                this.breakable = false;
                this.moving = true;
                this.moveSpeed = Utils.randomInt(50, 150);
                this.moveRange = Utils.randomInt(100, 200);
                this.startX = x;
                this.direction = 1;
                break;
                
            case 'breakable':
                this.tint = 0xff0000; // 红色易碎平台
                this.breakable = true;
                this.moving = false;
                this.breakTimer = 0;
                this.breakDelay = 2000; // 站上去2秒后破碎
                break;
                
            case 'spring':
                this.tint = 0xffff00; // 黄色弹簧平台
                this.breakable = false;
                this.moving = false;
                this.springPower = -800; // 弹跳力度
                break;
        }
    }
    
    update(time, delta) {
        // 移动平台逻辑
        if (this.moving) {
            this.x += this.moveSpeed * this.direction * (delta / 1000);
            
            // 检查移动范围
            if (Math.abs(this.x - this.startX) > this.moveRange) {
                this.direction *= -1;
            }
            
            // 确保平台不超出边界
            if (this.x < 0) {
                this.x = 0;
                this.direction = 1;
            } else if (this.x + this.width > this.scene.cameras.main.width) {
                this.x = this.scene.cameras.main.width - this.width;
                this.direction = -1;
            }
        }
        
        // 易碎平台逻辑
        if (this.breakable && this.body.touching.down) {
            this.breakTimer += delta;
            
            // 平台开始闪烁
            if (this.breakTimer > this.breakDelay * 0.7) {
                this.alpha = 0.5 + 0.5 * Math.sin(this.breakTimer * 0.01);
            }
            
            // 平台破碎
            if (this.breakTimer >= this.breakDelay) {
                this.break();
            }
        }
    }
    
    break() {
        this.scene.sound.play('break');
        this.destroy();
    }
}