// 愤怒的小鸟 - 完整游戏实现
// 整合自多个模块

// ==================== 游戏配置 ====================
const CONFIG = {
    GRAVITY: 0.5,
    FRICTION: 0.99,
    BOUNCE_DAMPING: 0.7,
    MAX_POWER: 20,
    BIRD_RADIUS: 15,
    PIG_RADIUS: 20,
    BLOCK_WIDTH: 30,
    BLOCK_HEIGHT: 60,
    SLINGSHOT_X: 150,
    SLINGSHOT_Y: 400,
    GROUND_Y: 500,
    BIRD_START_X: 150,
    BIRD_START_Y: 350,
    MIN_VELOCITY: 0.1,
    MAX_VELOCITY: 30,
    BIRD_COUNT: 3
};

// ==================== 游戏状态 ====================
const GameState = {
    READY: 'ready',
    AIMING: 'aiming',
    LAUNCHED: 'launched',
    FLYING: 'flying',
    LEVEL_COMPLETE: 'level_complete',
    GAME_OVER: 'game_over'
};

// ==================== 游戏对象基类 ====================
class GameObject {
    constructor(x, y, width, height, type) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.type = type;
        this.vx = 0;
        this.vy = 0;
        this.rotation = 0;
        this.rotationSpeed = 0;
        this.destroyed = false;
        this.health = this.getMaxHealth();
        this.color = this.getDefaultColor();
    }

    getMaxHealth() {
        switch(this.type) {
            case 'pig': return 100;
            case 'wood': return 50;
            case 'stone': return 100;
            case 'ice': return 30;
            default: return 100;
        }
    }

    getDefaultColor() {
        switch(this.type) {
            case 'bird': return '#FF5722';
            case 'pig': return '#4CAF50';
            case 'wood': return '#8D6E63';
            case 'stone': return '#757575';
            case 'ice': return '#B3E5FC';
            default: return '#000';
        }
    }

    update(canvas) {
        if (this.destroyed) return;

        this.x += this.vx;
        this.y += this.vy;

        // 应用重力
        if (this.type === 'bird' || this.type === 'pig') {
            this.vy += CONFIG.GRAVITY;
        }

        // 应用摩擦力
        this.vx *= CONFIG.FRICTION;
        this.vy *= CONFIG.FRICTION;

        // 旋转
        if (this.type === 'bird') {
            this.rotation += this.rotationSpeed;
        }

        // 地面碰撞
        if (this.y + this.height/2 > CONFIG.GROUND_Y) {
            this.y = CONFIG.GROUND_Y - this.height/2;
            this.vy *= -CONFIG.BOUNCE_DAMPING;
            this.vx *= CONFIG.FRICTION;

            if (Math.abs(this.vy) < CONFIG.MIN_VELOCITY) {
                this.vy = 0;
            }
        }

        // 边界检查
        if (canvas) {
            if (this.x - this.width/2 < 0 || this.x + this.width/2 > canvas.width) {
                this.vx *= -CONFIG.BOUNCE_DAMPING;
                this.x = Math.max(this.width/2, Math.min(canvas.width - this.width/2, this.x));
            }
        }
    }

    draw(ctx) {
        if (this.destroyed) return;

        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);

        switch(this.type) {
            case 'bird':
                this.drawBird(ctx);
                break;
            case 'pig':
                this.drawPig(ctx);
                break;
            case 'wood':
                this.drawWood(ctx);
                break;
            case 'stone':
                this.drawStone(ctx);
                break;
            case 'ice':
                this.drawIce(ctx);
                break;
        }

        ctx.restore();
    }

    drawBird(ctx) {
        // 绘制小鸟身体
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(0, 0, CONFIG.BIRD_RADIUS, 0, Math.PI * 2);
        ctx.fill();

        // 绘制眼睛
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(-5, -5, 4, 0, Math.PI * 2);
        ctx.arc(5, -5, 4, 0, Math.PI * 2);
        ctx.fill();

        // 绘制瞳孔
        ctx.fillStyle = 'black';
        ctx.beginPath();
        ctx.arc(-5, -5, 2, 0, Math.PI * 2);
        ctx.arc(5, -5, 2, 0, Math.PI * 2);
        ctx.fill();

        // 绘制喙
        ctx.fillStyle = '#FF9800';
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(-8, 5);
        ctx.lineTo(8, 5);
        ctx.closePath();
        ctx.fill();

        // 绘制眉毛
        ctx.strokeStyle = '#8B0000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(-10, -10);
        ctx.lineTo(-3, -8);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(10, -10);
        ctx.lineTo(3, -8);
        ctx.stroke();
    }

    drawPig(ctx) {
        // 绘制猪身体
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(0, 0, CONFIG.PIG_RADIUS, 0, Math.PI * 2);
        ctx.fill();

        // 绘制鼻子
        ctx.fillStyle = '#388E3C';
        ctx.beginPath();
        ctx.ellipse(0, 5, 10, 8, 0, 0, Math.PI * 2);
        ctx.fill();

        // 绘制鼻孔
        ctx.fillStyle = '#1B5E20';
        ctx.beginPath();
        ctx.arc(-4, 5, 2, 0, Math.PI * 2);
        ctx.arc(4, 5, 2, 0, Math.PI * 2);
        ctx.fill();

        // 绘制眼睛
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(-8, -8, 5, 0, Math.PI * 2);
        ctx.arc(8, -8, 5, 0, Math.PI * 2);
        ctx.fill();

        // 绘制瞳孔
        ctx.fillStyle = 'black';
        ctx.beginPath();
        ctx.arc(-8, -8, 2, 0, Math.PI * 2);
        ctx.arc(8, -8, 2, 0, Math.PI * 2);
        ctx.fill();

        // 绘制耳朵
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.moveTo(-10, -15);
        ctx.lineTo(-15, -25);
        ctx.lineTo(-5, -20);
        ctx.closePath();
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(10, -15);
        ctx.lineTo(15, -25);
        ctx.lineTo(5, -20);
        ctx.closePath();
        ctx.fill();
    }

    drawWood(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);

        // 添加木纹
        ctx.strokeStyle = '#5D4037';
        ctx.lineWidth = 1;
        for (let i = -this.height/2; i < this.height/2; i += 5) {
            ctx.beginPath();
            ctx.moveTo(-this.width/2, i);
            ctx.lineTo(this.width/2, i);
            ctx.stroke();
        }

        // 边框
        ctx.strokeStyle = '#3E2723';
        ctx.lineWidth = 2;
        ctx.strokeRect(-this.width/2, -this.height/2, this.width, this.height);
    }

    drawStone(ctx) {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.moveTo(-this.width/2, -this.height/2);
        ctx.lineTo(this.width/2, -this.height/2);
        ctx.lineTo(this.width/2 + 3, 0);
        ctx.lineTo(this.width/2, this.height/2);
        ctx.lineTo(-this.width/2, this.height/2);
        ctx.lineTo(-this.width/2 - 3, 0);
        ctx.closePath();
        ctx.fill();

        // 添加石头纹理
        ctx.fillStyle = '#616161';
        ctx.beginPath();
        ctx.arc(-5, -5, 3, 0, Math.PI * 2);
        ctx.arc(5, 5, 4, 0, Math.PI * 2);
        ctx.arc(0, 10, 3, 0, Math.PI * 2);
        ctx.fill();
    }

    drawIce(ctx) {
        ctx.fillStyle = 'rgba(179, 229, 252, 0.8)';
        ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);

        // 添加冰晶效果
        ctx.strokeStyle = '#81D4FA';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, -this.height/2);
        ctx.lineTo(0, this.height/2);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(-this.width/2, 0);
        ctx.lineTo(this.width/2, 0);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(-this.width/4, -this.height/4);
        ctx.lineTo(this.width/4, this.height/4);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(this.width/4, -this.height/4);
        ctx.lineTo(-this.width/4, this.height/4);
        ctx.stroke();

        // 边框
        ctx.strokeStyle = '#4FC3F7';
        ctx.lineWidth = 2;
        ctx.strokeRect(-this.width/2, -this.height/2, this.width, this.height);
    }

    checkCollision(other) {
        if (this.destroyed || other.destroyed) return false;

        // 简单的AABB碰撞检测
        return Math.abs(this.x - other.x) < (this.width + other.width) / 2 &&
               Math.abs(this.y - other.y) < (this.height + other.height) / 2;
    }

    takeDamage(amount) {
        this.health -= amount;
        if (this.health <= 0) {
            this.destroyed = true;
        }
    }

    getMass() {
        switch(this.type) {
            case 'bird': return 1;
            case 'pig': return 1.5;
            case 'wood': return 2;
            case 'stone': return 3;
            case 'ice': return 1.2;
            default: return 1;
        }
    }
}

// ==================== 粒子类 ====================
class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 10;
        this.vy = (Math.random() - 0.5) * 10;
        this.color = color || '#FFA500';
        this.life = 1.0;
        this.decay = 0.02;
        this.size = Math.random() * 5 + 2;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += CONFIG.GRAVITY * 0.5;
        this.life -= this.decay;
        this.size *= 0.98;
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    isDead() {
        return this.life <= 0;
    }
}

// ==================== 弹弓类 ====================
class Slingshot {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 30;
        this.height = 100;
    }

    draw(ctx) {
        // 绘制弹弓支架
        ctx.fillStyle = '#5D4037';
        ctx.strokeStyle = '#3E2723';
        ctx.lineWidth = 3;

        // 左支架
        ctx.beginPath();
        ctx.moveTo(this.x - 15, this.y);
        ctx.lineTo(this.x - 20, this.y + this.height);
        ctx.lineTo(this.x - 10, this.y + this.height);
        ctx.lineTo(this.x - 5, this.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // 右支架
        ctx.beginPath();
        ctx.moveTo(this.x + 5, this.y);
        ctx.lineTo(this.x + 10, this.y + this.height);
        ctx.lineTo(this.x + 20, this.y + this.height);
        ctx.lineTo(this.x + 15, this.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // 橡皮筋挂点
        ctx.fillStyle = '#8B4513';
        ctx.beginPath();
        ctx.arc(this.x - 10, this.y + 5, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(this.x + 10, this.y + 5, 5, 0, Math.PI * 2);
        ctx.fill();
    }

    drawRubberBand(ctx, birdX, birdY) {
        // 绘制橡皮筋
        ctx.strokeStyle = '#4A2C00';
        ctx.lineWidth = 4;

        // 左橡皮筋
        ctx.beginPath();
        ctx.moveTo(this.x - 10, this.y + 5);
        ctx.lineTo(birdX, birdY);
        ctx.stroke();

        // 右橡皮筋
        ctx.beginPath();
        ctx.moveTo(this.x + 10, this.y + 5);
        ctx.lineTo(birdX, birdY);
        ctx.stroke();
    }
}

// ==================== 关卡数据 ====================
const LEVELS = [
    {
        id: 1,
        name: "第一关",
        pigs: [{ x: 600, y: CONFIG.GROUND_Y - 25 }],
        blocks: [
            { x: 550, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'wood' },
            { x: 650, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'wood' },
            { x: 600, y: CONFIG.GROUND_Y - 70, width: 120, height: 20, type: 'wood' }
        ]
    },
    {
        id: 2,
        name: "第二关",
        pigs: [
            { x: 600, y: CONFIG.GROUND_Y - 25 },
            { x: 700, y: CONFIG.GROUND_Y - 25 }
        ],
        blocks: [
            { x: 550, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'wood' },
            { x: 650, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'wood' },
            { x: 600, y: CONFIG.GROUND_Y - 70, width: 120, height: 20, type: 'wood' },
            { x: 700, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'stone' },
            { x: 750, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'stone' },
            { x: 725, y: CONFIG.GROUND_Y - 70, width: 70, height: 20, type: 'stone' }
        ]
    },
    {
        id: 3,
        name: "第三关",
        pigs: [
            { x: 550, y: CONFIG.GROUND_Y - 25 },
            { x: 650, y: CONFIG.GROUND_Y - 25 },
            { x: 600, y: CONFIG.GROUND_Y - 95 }
        ],
        blocks: [
            { x: 500, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'ice' },
            { x: 600, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'ice' },
            { x: 700, y: CONFIG.GROUND_Y - 30, width: 20, height: 60, type: 'wood' },
            { x: 550, y: CONFIG.GROUND_Y - 70, width: 120, height: 20, type: 'ice' },
            { x: 650, y: CONFIG.GROUND_Y - 70, width: 120, height: 20, type: 'wood' },
            { x: 600, y: CONFIG.GROUND_Y - 110, width: 220, height: 20, type: 'wood' }
        ]
    }
];

// ==================== 游戏主类 ====================
class AngryBirdsGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        this.state = GameState.READY;
        this.currentLevel = 1;
        this.score = 0;
        this.birdsLeft = CONFIG.BIRD_COUNT;

        this.bird = null;
        this.slingshot = null;
        this.pigs = [];
        this.blocks = [];
        this.particles = [];

        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };

        this.init();
    }

    init() {
        this.setupCanvas();
        this.slingshot = new Slingshot(CONFIG.SLINGSHOT_X, CONFIG.SLINGSHOT_Y);
        this.loadLevel(this.currentLevel);
        this.setupEventListeners();
        this.gameLoop();
    }

    setupCanvas() {
        this.canvas.width = 800;
        this.canvas.height = 600;
    }

    loadLevel(levelId) {
        const levelData = LEVELS[levelId - 1] || LEVELS[0];

        this.pigs = [];
        this.blocks = [];
        this.particles = [];

        // 创建猪
        for (const pigData of levelData.pigs) {
            const pig = new GameObject(pigData.x, pigData.y, CONFIG.PIG_RADIUS * 2, CONFIG.PIG_RADIUS * 2, 'pig');
            this.pigs.push(pig);
        }

        // 创建障碍物
        for (const blockData of levelData.blocks) {
            const block = new GameObject(blockData.x, blockData.y, blockData.width, blockData.height, blockData.type);
            this.blocks.push(block);
        }

        // 重置小鸟
        this.resetBird();
        this.birdsLeft = CONFIG.BIRD_COUNT;
        this.state = GameState.READY;
        this.updateUI();
    }

    resetBird() {
        this.bird = new GameObject(CONFIG.BIRD_START_X, CONFIG.BIRD_START_Y, CONFIG.BIRD_RADIUS * 2, CONFIG.BIRD_RADIUS * 2, 'bird');
        this.isDragging = false;
    }

    setupEventListeners() {
        // 鼠标事件
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));

        // 触摸事件
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e));

        // 按钮事件
        document.getElementById('resetBtn').addEventListener('click', () => this.restartLevel());
        document.getElementById('nextLevelBtn').addEventListener('click', () => this.nextLevel());
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    handleMouseDown(e) {
        const pos = this.getMousePos(e);

        if (this.state === GameState.READY && this.bird) {
            const dx = pos.x - this.bird.x;
            const dy = pos.y - this.bird.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < CONFIG.BIRD_RADIUS + 20) {
                this.isDragging = true;
                this.dragStart = { x: this.bird.x, y: this.bird.y };
                this.state = GameState.AIMING;
            }
        }
    }

    handleMouseMove(e) {
        const pos = this.getMousePos(e);

        if (this.isDragging && this.bird) {
            // 计算拖拽距离
            let dx = pos.x - this.slingshot.x;
            let dy = pos.y - this.slingshot.y;

            // 限制最大拉伸距离
            const maxStretch = 100;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > maxStretch) {
                dx = dx / dist * maxStretch;
                dy = dy / dist * maxStretch;
            }

            // 小鸟只能在弹弓左后方拉动
            this.bird.x = this.slingshot.x + dx;
            this.bird.y = this.slingshot.y + dy;

            // 确保小鸟在弹弓的左后方
            if (this.bird.x > this.slingshot.x) {
                this.bird.x = this.slingshot.x;
            }

            // 更新力度指示器
            this.updatePowerIndicator(dist / maxStretch);
        }
    }

    handleMouseUp(e) {
        if (this.isDragging && this.bird) {
            // 计算发射速度
            const dx = this.slingshot.x - this.bird.x;
            const dy = this.slingshot.y - this.bird.y;

            const power = Math.sqrt(dx * dx + dy * dy) / 100 * CONFIG.MAX_POWER;

            this.bird.vx = dx / 100 * CONFIG.MAX_POWER;
            this.bird.vy = dy / 100 * CONFIG.MAX_POWER;

            this.state = GameState.FLYING;
            this.isDragging = false;

            // 创建发射粒子
            this.createParticles(this.slingshot.x, this.slingshot.y, 10, '#8B4513');
        }
    }

    handleTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        this.handleMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
    }

    handleTouchMove(e) {
        e.preventDefault();
        const touch = e.touches[0];
        this.handleMouseMove({ clientX: touch.clientX, clientY: touch.clientY });
    }

    handleTouchEnd(e) {
        e.preventDefault();
        this.handleMouseUp({});
    }

    updatePowerIndicator(power) {
        const powerBar = document.getElementById('powerBar');
        if (powerBar) {
            powerBar.style.width = (power * 100) + '%';
            document.getElementById('powerIndicator').style.display = 'block';
        }
    }

    hidePowerIndicator() {
        const indicator = document.getElementById('powerIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    createParticles(x, y, count, color) {
        for (let i = 0; i < count; i++) {
            this.particles.push(new Particle(x, y, color));
        }
    }

    update() {
        // 更新小鸟
        if (this.bird && this.state === GameState.FLYING) {
            this.bird.update(this.canvas);

            // 检查是否停止
            if (Math.abs(this.bird.vx) < 0.5 && Math.abs(this.bird.vy) < 0.5 && this.bird.y >= CONFIG.GROUND_Y - CONFIG.BIRD_RADIUS - 5) {
                this.birdStopped();
            }

            // 检查是否出界
            if (this.bird.x > this.canvas.width + 100 || this.bird.y > this.canvas.height + 100) {
                this.birdStopped();
            }
        }

        // 更新障碍物
        for (const block of this.blocks) {
            if (!block.destroyed) {
                block.update(this.canvas);
            }
        }

        // 更新猪
        for (const pig of this.pigs) {
            if (!pig.destroyed) {
                pig.update(this.canvas);
            }
        }

        // 更新粒子
        for (let i = this.particles.length - 1; i >= 0; i--) {
            this.particles[i].update();
            if (this.particles[i].isDead()) {
                this.particles.splice(i, 1);
            }
        }

        // 碰撞检测
        this.checkCollisions();

        // 检查游戏状态
        this.checkGameState();
    }

    checkCollisions() {
        if (!this.bird || this.state !== GameState.FLYING) return;

        // 小鸟与障碍物碰撞
        for (const block of this.blocks) {
            if (!block.destroyed && this.bird.checkCollision(block)) {
                const speed = Math.sqrt(this.bird.vx * this.bird.vx + this.bird.vy * this.bird.vy);
                block.takeDamage(speed * 10);
                this.score += Math.floor(speed * 5);

                if (block.destroyed) {
                    this.createParticles(block.x, block.y, 15, block.color);
                    this.score += 50;
                }

                // 反弹
                this.bird.vx *= -0.5;
                this.bird.vy *= 0.5;
            }
        }

        // 小鸟与猪碰撞
        for (const pig of this.pigs) {
            if (!pig.destroyed && this.bird.checkCollision(pig)) {
                const speed = Math.sqrt(this.bird.vx * this.bird.vx + this.bird.vy * this.bird.vy);
                pig.takeDamage(speed * 15);

                if (pig.destroyed) {
                    this.createParticles(pig.x, pig.y, 20, '#4CAF50');
                    this.score += 100;
                }

                // 反弹
                this.bird.vx *= -0.3;
                this.bird.vy *= 0.3;
            }
        }
    }

    birdStopped() {
        this.birdsLeft--;
        this.hidePowerIndicator();
        this.updateUI();

        if (this.birdsLeft > 0) {
            this.resetBird();
            this.state = GameState.READY;
        } else {
            // 检查是否还有猪存活
            const alivePigs = this.pigs.filter(p => !p.destroyed);
            if (alivePigs.length > 0) {
                this.state = GameState.GAME_OVER;
                this.showGameOver();
            }
        }
    }

    checkGameState() {
        // 检查是否所有猪都被消灭
        const alivePigs = this.pigs.filter(p => !p.destroyed);

        if (alivePigs.length === 0) {
            this.state = GameState.LEVEL_COMPLETE;
            this.showLevelComplete();
        }
    }

    showLevelComplete() {
        const messageEl = document.getElementById('gameMessage');
        const levelComplete = document.getElementById('levelComplete');
        const gameOver = document.getElementById('gameOver');

        // 计算星级
        const stars = this.calculateStars();
        this.score += this.birdsLeft * 1000; // 剩余小鸟加分

        // 更新显示
        document.getElementById('finalScore').textContent = this.score;
        document.getElementById('starsDisplay').textContent = '★'.repeat(stars) + '☆'.repeat(3 - stars);

        messageEl.style.display = 'block';
        levelComplete.style.display = 'block';
        gameOver.style.display = 'none';

        document.getElementById('nextLevelBtn').style.display = 'inline-block';
        this.updateUI();
    }

    showGameOver() {
        const messageEl = document.getElementById('gameMessage');
        const levelComplete = document.getElementById('levelComplete');
        const gameOver = document.getElementById('gameOver');

        document.getElementById('gameOverScore').textContent = this.score;

        messageEl.style.display = 'block';
        levelComplete.style.display = 'none';
        gameOver.style.display = 'block';
    }

    calculateStars() {
        if (this.birdsLeft >= 2) return 3;
        if (this.birdsLeft >= 1) return 2;
        return 1;
    }

    showMessage(text, type) {
        const messageEl = document.getElementById('gameMessage');
        const levelComplete = document.getElementById('levelComplete');
        const gameOver = document.getElementById('gameOver');

        messageEl.style.display = 'block';

        if (type === 'complete') {
            levelComplete.style.display = 'block';
            gameOver.style.display = 'none';
        } else {
            levelComplete.style.display = 'none';
            gameOver.style.display = 'block';
        }
    }

    hideMessage() {
        const messageEl = document.getElementById('gameMessage');
        const levelComplete = document.getElementById('levelComplete');
        const gameOver = document.getElementById('gameOver');

        messageEl.style.display = 'none';
        levelComplete.style.display = 'none';
        gameOver.style.display = 'none';
    }

    restartLevel() {
        this.score = 0;
        this.hideMessage();
        document.getElementById('nextLevelBtn').style.display = 'none';
        this.loadLevel(this.currentLevel);
    }

    nextLevel() {
        this.currentLevel++;
        if (this.currentLevel > LEVELS.length) {
            this.currentLevel = 1;
        }
        this.hideMessage();
        document.getElementById('nextLevelBtn').style.display = 'none';
        this.loadLevel(this.currentLevel);
    }

    updateUI() {
        document.getElementById('scoreValue').textContent = this.score;
        document.getElementById('birdsValue').textContent = this.birdsLeft;

        // 更新关卡显示
        const levelEl = document.getElementById('levelValue');
        if (levelEl) {
            levelEl.textContent = this.currentLevel;
        }
    }

    render() {
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 绘制背景
        this.drawBackground();

        // 绘制地面
        this.drawGround();

        // 绘制障碍物
        for (const block of this.blocks) {
            block.draw(this.ctx);
        }

        // 绘制猪
        for (const pig of this.pigs) {
            pig.draw(this.ctx);
        }

        // 绘制弹弓
        if (this.slingshot) {
            this.slingshot.draw(this.ctx);

            // 绘制橡皮筋
            if (this.bird && (this.isDragging || this.state === GameState.READY)) {
                this.slingshot.drawRubberBand(this.ctx, this.bird.x, this.bird.y);
            }
        }

        // 绘制小鸟
        if (this.bird) {
            this.bird.draw(this.ctx);
        }

        // 绘制瞄准轨迹
        if (this.isDragging && this.bird) {
            this.drawTrajectory();
        }

        // 绘制粒子
        for (const particle of this.particles) {
            particle.draw(this.ctx);
        }
    }

    drawBackground() {
        // 天空渐变
        const gradient = this.ctx.createLinearGradient(0, 0, 0, CONFIG.GROUND_Y);
        gradient.addColorStop(0, '#87CEEB');
        gradient.addColorStop(0.5, '#98D8E8');
        gradient.addColorStop(1, '#B0E0E6');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, CONFIG.GROUND_Y);

        // 绘制云朵
        this.drawCloud(100, 80, 40);
        this.drawCloud(300, 60, 50);
        this.drawCloud(550, 90, 35);
        this.drawCloud(700, 70, 45);
    }

    drawCloud(x, y, size) {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        this.ctx.beginPath();
        this.ctx.arc(x, y, size * 0.5, 0, Math.PI * 2);
        this.ctx.arc(x + size * 0.4, y - size * 0.2, size * 0.4, 0, Math.PI * 2);
        this.ctx.arc(x + size * 0.8, y, size * 0.5, 0, Math.PI * 2);
        this.ctx.arc(x + size * 0.4, y + size * 0.1, size * 0.35, 0, Math.PI * 2);
        this.ctx.fill();
    }

    drawGround() {
        // 草地
        this.ctx.fillStyle = '#7CB342';
        this.ctx.fillRect(0, CONFIG.GROUND_Y, this.canvas.width, this.canvas.height - CONFIG.GROUND_Y);

        // 土地
        this.ctx.fillStyle = '#8D6E63';
        this.ctx.fillRect(0, CONFIG.GROUND_Y + 20, this.canvas.width, this.canvas.height - CONFIG.GROUND_Y - 20);

        // 草地纹理
        this.ctx.strokeStyle = '#558B2F';
        this.ctx.lineWidth = 2;
        for (let x = 0; x < this.canvas.width; x += 20) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, CONFIG.GROUND_Y);
            this.ctx.lineTo(x + 5, CONFIG.GROUND_Y - 10);
            this.ctx.stroke();
            this.ctx.beginPath();
            this.ctx.moveTo(x + 10, CONFIG.GROUND_Y);
            this.ctx.lineTo(x + 8, CONFIG.GROUND_Y - 8);
            this.ctx.stroke();
        }
    }

    drawTrajectory() {
        if (!this.bird) return;

        // 计算预测轨迹
        const dx = this.slingshot.x - this.bird.x;
        const dy = this.slingshot.y - this.bird.y;

        let vx = dx / 100 * CONFIG.MAX_POWER;
        let vy = dy / 100 * CONFIG.MAX_POWER;
        let x = this.bird.x;
        let y = this.bird.y;

        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);

        for (let i = 0; i < 30; i++) {
            x += vx;
            y += vy;
            vy += CONFIG.GRAVITY;
            vx *= CONFIG.FRICTION;

            if (y > CONFIG.GROUND_Y) break;

            this.ctx.lineTo(x, y);
        }

        this.ctx.stroke();
        this.ctx.setLineDash([]);
    }

    gameLoop() {
        this.update();
        this.render();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// ==================== 初始化游戏 ====================
window.onload = function() {
    window.game = new AngryBirdsGame();
};
