// 游戏主类
class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        
        this.player = null;
        this.platforms = [];
        this.camera = { y: 0 };
        this.gameState = 'menu'; // menu, playing, paused, gameover
        this.score = 0;
        this.floor = 1;
        
        this.init();
    }
    
    init() {
        // 初始化玩家
        this.player = new Player(
            this.width / 2 - 25,
            this.height - 100,
            50,
            50
        );
        
        // 创建初始平台
        this.createInitialPlatforms();
        
        // 设置事件监听
        this.setupEventListeners();
    }
    
    createInitialPlatforms() {
        // 起始平台
        this.platforms.push(new Platform(
            this.width / 2 - 100,
            this.height - 50,
            200,
            20
        ));
        
        // 生成初始平台
        for (let i = 1; i < 20; i++) {
            this.createPlatform(-i * 100);
        }
    }
    
    createPlatform(y) {
        const platformWidth = Utils.randomInt(80, 150);
        const platformX = Utils.randomInt(0, this.width - platformWidth);
        const platformType = Math.random() < 0.1 ? 'moving' : 'normal';
        
        this.platforms.push(new Platform(
            platformX,
            y,
            platformWidth,
            20,
            platformType
        ));
    }
    
    setupEventListeners() {
        // 键盘事件
        window.addEventListener('keydown', (e) => {
            if (this.gameState !== 'playing') return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    this.player.moveLeft();
                    break;
                case 'ArrowRight':
                    this.player.moveRight();
                    break;
                case ' ':
                case 'ArrowUp':
                    this.player.jump();
                    break;
            }
        });
        
        // 触摸事件（移动设备支持）
        this.canvas.addEventListener('touchstart', (e) => {
            if (this.gameState !== 'playing') return;
            
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            const x = touch.clientX - rect.left;
            
            if (x < this.width / 2) {
                this.player.moveLeft();
            } else {
                this.player.moveRight();
            }
        });
        
        this.canvas.addEventListener('touchend', () => {
            this.player.velocityX = 0;
        });
    }
    
    update() {
        if (this.gameState !== 'playing') return;
        
        // 更新玩家
        this.player.update();
        
        // 检测平台碰撞
        let onPlatform = false;
        for (let platform of this.platforms) {
            if (this.player.onPlatform(platform)) {
                this.player.y = platform.y - this.player.height;
                this.player.velocityY = 0;
                this.player.isJumping = false;
                onPlatform = true;
                
                // 计分
                if (!platform.passed && platform.y < this.player.y) {
                    platform.passed = true;
                    this.score += 10;
                    this.updateScore();
                }
            }
        }
        
        // 更新相机位置
        if (this.player.y < this.height / 2) {
            this.camera.y = this.height / 2 - this.player.y;
        }
        
        // 更新平台
        for (let platform of this.platforms) {
            platform.update();
        }
        
        // 移除屏幕外的平台并生成新的
        this.platforms = this.platforms.filter(platform => {
            return platform.y - this.camera.y < this.height + 100;
        });
        
        // 生成新平台
        const highestPlatform = Math.min(...this.platforms.map(p => p.y));
        if (highestPlatform > this.camera.y - 200) {
            for (let i = 0; i < 5; i++) {
                this.createPlatform(highestPlatform - (i + 1) * 100);
            }
        }
        
        // 检测游戏结束条件
        if (this.player.y - this.camera.y > this.height) {
            this.gameOver();
        }
        
        // 更新楼层
        this.floor = Math.floor((this.camera.y / 100) + 1);
        document.getElementById('floor').textContent = this.floor;
    }
    
    draw() {
        // 清空画布
        this.ctx.fillStyle = '#ecf0f1';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // 保存当前状态
        this.ctx.save();
        
        // 应用相机变换
        this.ctx.translate(0, this.camera.y);
        
        // 绘制平台
        for (let platform of this.platforms) {
            platform.draw(this.ctx);
        }
        
        // 绘制玩家
        this.player.draw(this.ctx);
        
        // 恢复状态
        this.ctx.restore();
        
        // 绘制UI
        this.drawUI();
    }
    
    drawUI() {
        // 绘制游戏状态
        if (this.gameState === 'menu') {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.width, this.height);
            
            this.ctx.fillStyle = 'white';
            this.ctx.font = '48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('是男人就下100层', this.width / 2, this.height / 2 - 50);
            
            this.ctx.font = '24px Arial';
            this.ctx.fillText('点击"开始游戏"按钮开始', this.width / 2, this.height / 2 + 20);
        } else if (this.gameState === 'paused') {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(0, 0, this.width, this.height);
            
            this.ctx.fillStyle = 'white';
            this.ctx.font = '48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('游戏暂停', this.width / 2, this.height / 2);
        } else if (this.gameState === 'gameover') {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.width, this.height);
            
            this.ctx.fillStyle = 'white';
            this.ctx.font = '48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('游戏结束', this.width / 2, this.height / 2 - 50);
            
            this.ctx.font = '24px Arial';
            this.ctx.fillText(`最终得分: ${this.score}`, this.width / 2, this.height / 2 + 20);
            this.ctx.fillText('点击"重新开始"按钮再试一次', this.width / 2, this.height / 2 + 60);
        }
    }
    
    updateScore() {
        document.getElementById('score').textContent = this.score;
    }
    
    start() {
        this.gameState = 'playing';
    }
    
    pause() {
        if (this.gameState === 'playing') {
            this.gameState = 'paused';
        } else if (this.gameState === 'paused') {
            this.gameState = 'playing';
        }
    }
    
    restart() {
        this.gameState = 'menu';
        this.score = 0;
        this.floor = 1;
        this.camera.y = 0;
        this.platforms = [];
        this.player = null;
        this.init();
        this.updateScore();
        document.getElementById('floor').textContent = this.floor;
        document.getElementById('lives').textContent = this.player.lives;
    }
    
    gameOver() {
        this.gameState = 'gameover';
        this.player.lives--;
        document.getElementById('lives').textContent = this.player.lives;
        
        if (this.player.lives <= 0) {
            // 游戏真正结束
            this.gameState = 'gameover';
        } else {
            // 重置玩家位置
            this.player.x = this.width / 2 - 25;
            this.player.y = this.height - 100;
            this.player.velocityX = 0;
            this.player.velocityY = 0;
            this.camera.y = 0;
        }
    }
    
    gameLoop() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}