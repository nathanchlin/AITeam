class Enemy {
    constructor(x, y, type, difficulty = 1) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.difficulty = difficulty;
        this.active = true;
        this.shootCooldown = 0;
        this.pathIndex = 0;
        this.pathProgress = 0;
        
        // 根据敌机类型设置属性
        this.setEnemyProperties();
        
        // 初始化移动路径
        this.initializePath();
    }
    
    setEnemyProperties() {
        switch(this.type) {
            case 'basic':
                this.width = 40;
                this.height = 40;
                this.speed = 2 + this.difficulty * 0.2;
                this.health = 1 + Math.floor(this.difficulty / 3);
                this.shootRate = 60 - this.difficulty * 2; // 帧数
                this.scoreValue = 10;
                this.color = '#FF5555';
                break;
                
            case 'fast':
                this.width = 30;
                this.height = 30;
                this.speed = 4 + this.difficulty * 0.3;
                this.health = 1;
                this.shootRate = 80 - this.difficulty * 3;
                this.scoreValue = 20;
                this.color = '#55FF55';
                break;
                
            case 'heavy':
                this.width = 60;
                this.height = 50;
                this.speed = 1 + this.difficulty * 0.1;
                this.health = 3 + Math.floor(this.difficulty / 2);
                this.shootRate = 40 - this.difficulty;
                this.scoreValue = 50;
                this.color = '#5555FF';
                break;
                
            case 'zigzag':
                this.width = 35;
                this.height = 35;
                this.speed = 2.5 + this.difficulty * 0.2;
                this.health = 2;
                this.shootRate = 50 - this.difficulty * 2;
                this.scoreValue = 30;
                this.color = '#FFFF55';
                this.zigzagAmplitude = 50 + this.difficulty * 10;
                this.zigzagFrequency = 0.05 + this.difficulty * 0.005;
                break;
                
            case 'boss':
                this.width = 120;
                this.height = 100;
                this.speed = 0.8 + this.difficulty * 0.05;
                this.health = 20 + this.difficulty * 5;
                this.shootRate = 30 - this.difficulty;
                this.scoreValue = 500;
                this.color = '#FF00FF';
                this.bossPattern = 0;
                this.patternTimer = 0;
                break;
        }
    }
    
    initializePath() {
        // 默认路径：从上方随机位置进入，直线向下
        this.path = [
            { x: this.x, y: this.y },
            { x: this.x, y: this.y + 600 }
        ];
        
        // 根据类型设置特殊路径
        if (this.type === 'zigzag') {
            this.path = this.generateZigzagPath();
        } else if (this.type === 'boss') {
            this.path = this.generateBossPath();
        }
    }
    
    generateZigzagPath() {
        const points = [];
        const startX = this.x;
        const startY = this.y;
        const amplitude = this.zigzagAmplitude;
        const frequency = this.zigzagFrequency;
        
        for (let y = 0; y <= 600; y += 20) {
            const x = startX + Math.sin(y * frequency) * amplitude;
            points.push({ x, y: startY + y });
        }
        
        return points;
    }
    
    generateBossPath() {
        const points = [];
        // Boss会先从上方进入，然后左右移动，最后俯冲
        points.push({ x: 400, y: -100 }); // 从上方进入
        points.push({ x: 200, y: 100 });  // 左移
        points.push({ x: 600, y: 100 });  // 右移
        points.push({ x: 400, y: 200 });  // 回到中间
        points.push({ x: 400, y: 400 });  // 向下移动
        points.push({ x: 400, y: 600 });  // 继续向下
        
        return points;
    }
    
    update(player, bullets) {
        if (!this.active) return;
        
        // 更新位置
        this.updatePosition();
        
        // 更新射击冷却
        if (this.shootCooldown > 0) {
            this.shootCooldown--;
        }
        
        // 根据类型执行不同的AI行为
        switch(this.type) {
            case 'basic':
                this.basicAI(player, bullets);
                break;
            case 'fast':
                this.fastAI(player, bullets);
                break;
            case 'heavy':
                this.heavyAI(player, bullets);
                break;
            case 'zigzag':
                this.zigzagAI(player, bullets);
                break;
            case 'boss':
                this.bossAI(player, bullets);
                break;
        }
        
        // 检查是否超出屏幕
        if (this.y > 650 || this.x < -100 || this.x > 900) {
            this.active = false;
        }
    }
    
    updatePosition() {
        // 沿路径移动
        if (this.pathIndex < this.path.length - 1) {
            const currentPoint = this.path[this.pathIndex];
            const nextPoint = this.path[this.pathIndex + 1];
            
            const dx = nextPoint.x - currentPoint.x;
            const dy = nextPoint.y - currentPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0) {
                this.pathProgress += this.speed / distance;
                
                if (this.pathProgress >= 1) {
                    this.pathIndex++;
                    this.pathProgress = 0;
                } else {
                    this.x = currentPoint.x + dx * this.pathProgress;
                    this.y = currentPoint.y + dy * this.pathProgress;
                }
            }
        }
    }
    
    basicAI(player, bullets) {
        // 基本敌机：简单地向玩家射击
        if (this.shootCooldown <= 0 && this.y > 0) {
            // 计算朝向玩家的角度
            const angle = Math.atan2(player.y - this.y, player.x - this.x);
            bullets.push(new Bullet(
                this.x + this.width / 2,
                this.y + this.height,
                Math.cos(angle) * 5,
                Math.sin(angle) * 5,
                'enemy'
            ));
            this.shootCooldown = this.shootRate;
        }
    }
    
    fastAI(player, bullets) {
        // 快速敌机：快速移动，偶尔射击
        if (Math.random() < 0.02 && this.shootCooldown <= 0) {
            bullets.push(new Bullet(
                this.x + this.width / 2,
                this.y + this.height,
                0,
                5,
                'enemy'
            ));
            this.shootCooldown = this.shootRate;
        }
    }
    
    heavyAI(player, bullets) {
        // 重型敌机：缓慢移动，密集射击
        if (this.shootCooldown <= 0) {
            // 扇形射击
            for (let i = -1; i <= 1; i++) {
                bullets.push(new Bullet(
                    this.x + this.width / 2,
                    this.y + this.height,
                    i * 2,
                    4,
                    'enemy'
                ));
            }
            this.shootCooldown = this.shootRate;
        }
    }
    
    zigzagAI(player, bullets) {
        // 之字形敌机：之字形移动，瞄准射击
        if (this.shootCooldown <= 0 && this.y > 0) {
            // 计算朝向玩家的角度
            const angle = Math.atan2(player.y - this.y, player.x - this.x);
            bullets.push(new Bullet(
                this.x + this.width / 2,
                this.y + this.height,
                Math.cos(angle) * 4,
                Math.sin(angle) * 4,
                'enemy'
            ));
            this.shootCooldown = this.shootRate;
        }
    }
    
    bossAI(player, bullets) {
        // Boss AI：复杂的行为模式
        this.patternTimer++;
        
        // 根据模式切换行为
        if (this.health > 15) {
            // 模式1：扇形射击
            if (this.patternTimer % 40 === 0) {
                for (let i = -3; i <= 3; i++) {
                    bullets.push(new Bullet(
                        this.x + this.width / 2,
                        this.y + this.height,
                        i * 3,
                        5,
                        'enemy'
                    ));
                }
            }
        } else if (this.health > 5) {
            // 模式2：环形射击
            if (this.patternTimer % 30 === 0) {
                for (let i = 0; i < 8; i++) {
                    const angle = (i / 8) * Math.PI * 2;
                    bullets.push(new Bullet(
                        this.x + this.width / 2,
                        this.y + this.height / 2,
                        Math.cos(angle) * 4,
                        Math.sin(angle) * 4,
                        'enemy'
                    ));
                }
            }
        } else {
            // 模式3：密集射击
            if (this.patternTimer % 20 === 0) {
                for (let i = -5; i <= 5; i++) {
                    bullets.push(new Bullet(
                        this.x + this.width / 2 + i * 10,
                        this.y + this.height,
                        0,
                        6,
                        'enemy'
                    ));
                }
            }
        }
    }
    
    draw(ctx) {
        if (!this.active) return;
        
        ctx.fillStyle = this.color;
        
        // 根据类型绘制不同的敌机形状
        switch(this.type) {
            case 'basic':
                this.drawBasicEnemy(ctx);
                break;
            case 'fast':
                this.drawFastEnemy(ctx);
                break;
            case 'heavy':
                this.drawHeavyEnemy(ctx);
                break;
            case 'zigzag':
                this.drawZigzagEnemy(ctx);
                break;
            case 'boss':
                this.drawBossEnemy(ctx);
                break;
        }
        
        // 绘制血条
        if (this.health > 1) {
            ctx.fillStyle = '#FF0000';
            ctx.fillRect(this.x, this.y - 10, this.width, 5);
            ctx.fillStyle = '#00FF00';
            ctx.fillRect(this.x, this.y - 10, this.width * (this.health / this.maxHealth), 5);
        }
    }
    
    drawBasicEnemy(ctx) {
        // 基本敌机：三角形
        ctx.beginPath();
        ctx.moveTo(this.x + this.width / 2, this.y);
        ctx.lineTo(this.x, this.y + this.height);
        ctx.lineTo(this.x + this.width, this.y + this.height);
        ctx.closePath();
        ctx.fill();
    }
    
    drawFastEnemy(ctx) {
        // 快速敌机：菱形
        ctx.beginPath();
        ctx.moveTo(this.x + this.width / 2, this.y);
        ctx.lineTo(this.x, this.y + this.height / 2);
        ctx.lineTo(this.x + this.width / 2, this.y + this.height);
        ctx.lineTo(this.x + this.width, this.y + this.height / 2);
        ctx.closePath();
        ctx.fill();
    }
    
    drawHeavyEnemy(ctx) {
        // 重型敌机：矩形
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.fillStyle = '#AAAAAA';
        ctx.fillRect(this.x + 5, this.y + 5, this.width - 10, this.height - 10);
    }
    
    drawZigzagEnemy(ctx) {
        // 之字形敌机：Z字形
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.width / 3, this.y + this.height / 2);
        ctx.lineTo(this.x, this.y + this.height);
        ctx.lineTo(this.x + this.width, this.y + this.height);
        ctx.lineTo(this.x + this.width * 2 / 3, this.y + this.height / 2);
        ctx.lineTo(this.x + this.width, this.y);
        ctx.closePath();
        ctx.fill();
    }
    
    drawBossEnemy(ctx) {
        // Boss敌机：复杂形状
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y + 20, this.width, this.height - 20);
        
        // 机翼
        ctx.fillRect(this.x - 20, this.y + 40, 40, 20);
        ctx.fillRect(this.x + this.width - 20, this.y + 40, 40, 20);
        
        // 驾驶舱
        ctx.fillStyle = '#00FFFF';
        ctx.fillRect(this.x + this.width / 2 - 15, this.y + 30, 30, 20);
        
        // 引擎
        ctx.fillStyle = '#FFAA00';
        ctx.fillRect(this.x + 10, this.y + this.height - 10, 20, 10);
        ctx.fillRect(this.x + this.width - 30, this.y + this.height - 10, 20, 10);
    }
    
    takeDamage(damage) {
        this.health -= damage;
        if (this.health <= 0) {
            this.active = false;
            return true; // 敌机被摧毁
        }
        return false;
    }
}