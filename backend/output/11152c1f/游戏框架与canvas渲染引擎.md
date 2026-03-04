# 游戏框架与Canvas渲染引擎

**Time**: 2026-03-01T13:25:39.731016

---

好的，我来为你构建一个完整的打僵尸游戏框架，包含Canvas渲染引擎、游戏循环、视口管理和输入系统。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zombie Slayer - 游戏框架演示</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0c0f;
            --bg-dark: #050607;
            --fg: #e8ebe4;
            --muted: #5a6a5f;
            --accent: #ff3d3d;
            --accent-glow: rgba(255, 61, 61, 0.4);
            --player: #4ecdc4;
            --zombie: #7a9e5a;
            --bullet: #ffd93d;
            --ground: #1a1d21;
            --grid: rgba(255,255,255,0.03);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--bg);
            overflow: hidden;
            font-family: 'Share Tech Mono', monospace;
            color: var(--fg);
        }

        #gameCanvas {
            display: block;
            background: var(--bg-dark);
        }

        #ui-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }

        .hud {
            position: absolute;
            top: 20px;
            left: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .hud-item {
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 20px;
            border-radius: 4px;
            font-size: 14px;
            letter-spacing: 1px;
        }

        .hud-item span {
            color: var(--accent);
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
        }

        .fps-counter {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            color: var(--muted);
        }

        .fps-counter span {
            color: var(--player);
            font-weight: bold;
        }

        .controls-hint {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 13px;
            color: var(--muted);
            display: flex;
            gap: 24px;
        }

        .controls-hint kbd {
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 3px;
            color: var(--fg);
            margin: 0 4px;
        }

        .debug-panel {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(10, 12, 15, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 16px;
            border-radius: 4px;
            font-size: 11px;
            color: var(--muted);
            line-height: 1.8;
        }

        .debug-panel .label {
            color: var(--muted);
        }

        .debug-panel .value {
            color: var(--player);
            font-family: 'Orbitron', sans-serif;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div id="ui-overlay">
        <div class="hud">
            <div class="hud-item">SCORE: <span id="score">0</span></div>
            <div class="hud-item">HEALTH: <span id="health">100</span></div>
            <div class="hud-item">WAVE: <span id="wave">1</span></div>
        </div>
        
        <div class="fps-counter">
            FPS: <span id="fpsValue">60</span> | Objects: <span id="objectCount">0</span>
        </div>
        
        <div class="controls-hint">
            <span><kbd>WASD</kbd> Move</span>
            <span><kbd>Mouse</kbd> Aim</span>
            <span><kbd>Click</kbd> Shoot</span>
            <span><kbd>Space</kbd> Dash</span>
        </div>
        
        <div class="debug-panel">
            <div><span class="label">Viewport:</span> <span class="value" id="viewportPos">0, 0</span></div>
            <div><span class="label">Player:</span> <span class="value" id="playerPos">0, 0</span></div>
            <div><span class="label">World:</span> <span class="value" id="worldSize">2000 x 2000</span></div>
        </div>
    </div>

    <script>
    // ============================================
    // 游戏配置常量
    // ============================================
    const CONFIG = {
        WORLD_WIDTH: 2000,
        WORLD_HEIGHT: 2000,
        PLAYER_SPEED: 280,
        PLAYER_DASH_SPEED: 600,
        PLAYER_SIZE: 24,
        BULLET_SPEED: 600,
        BULLET_SIZE: 6,
        ZOMBIE_SPEED: 80,
        ZOMBIE_SIZE: 28,
        SPAWN_RATE: 2000,
        MAX_ZOMBIES: 30,
        GRID_SIZE: 50
    };

    // ============================================
    // 工具函数
    // ============================================
    const Utils = {
        lerp(a, b, t) {
            return a + (b - a) * t;
        },
        
        clamp(val, min, max) {
            return Math.max(min, Math.min(max, val));
        },
        
        distance(x1, y1, x2, y2) {
            const dx = x2 - x1;
            const dy = y2 - y1;
            return Math.sqrt(dx * dx + dy * dy);
        },
        
        angle(x1, y1, x2, y2) {
            return Math.atan2(y2 - y1, x2 - x1);
        },
        
        randomRange(min, max) {
            return min + Math.random() * (max - min);
        },
        
        randomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }
    };

    // ============================================
    // 向量类
    // ============================================
    class Vector2 {
        constructor(x = 0, y = 0) {
            this.x = x;
            this.y = y;
        }
        
        set(x, y) {
            this.x = x;
            this.y = y;
            return this;
        }
        
        copy(v) {
            this.x = v.x;
            this.y = v.y;
            return this;
        }
        
        clone() {
            return new Vector2(this.x, this.y);
        }
        
        add(v) {
            this.x += v.x;
            this.y += v.y;
            return this;
        }
        
        sub(v) {
            this.x -= v.x;
            this.y -= v.y;
            return this;
        }
        
        scale(s) {
            this.x *= s;
            this.y *= s;
            return this;
        }
        
        normalize() {
            const len = this.length();
            if (len > 0) {
                this.x /= len;
                this.y /= len;
            }
            return this;
        }
        
        length() {
            return Math.sqrt(this.x * this.x + this.y * this.y);
        }
        
        dot(v) {
            return this.x * v.x + this.y * v.y;
        }
    }

    // ============================================
    // 输入管理器
    // ============================================
    class InputManager {
        constructor(canvas) {
            this.canvas = canvas;
            this.keys = {};
            this.mouse = {
                x: 0,
                y: 0,
                worldX: 0,
                worldY: 0,
                leftDown: false,
                rightDown: false
            };
            
            this.bindEvents();
        }
        
        bindEvents() {
            window.addEventListener('keydown', (e) => {
                this.keys[e.code] = true;
                if (['Space', 'KeyW', 'KeyA', 'KeyS', 'KeyD'].includes(e.code)) {
                    e.preventDefault();
                }
            });
            
            window.addEventListener('keyup', (e) => {
                this.keys[e.code] = false;
            });
            
            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = e.clientX - rect.left;
                this.mouse.y = e.clientY - rect.top;
            });
            
            this.canvas.addEventListener('mousedown', (e) => {
                if (e.button === 0) this.mouse.leftDown = true;
                if (e.button === 2) this.mouse.rightDown = true;
            });
            
            this.canvas.addEventListener('mouseup', (e) => {
                if (e.button === 0) this.mouse.leftDown = false;
                if (e.button === 2) this.mouse.rightDown = false;
            });
            
            this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        }
        
        isKeyDown(code) {
            return this.keys[code] === true;
        }
        
        updateWorldMouse(viewport) {
            this.mouse.worldX = this.mouse.x + viewport.x;
            this.mouse.worldY = this.mouse.y + viewport.y;
        }
    }

    // ============================================
    // 视口管理器
    // ============================================
    class Viewport {
        constructor(canvas, worldWidth, worldHeight) {
            this.canvas = canvas;
            this.worldWidth = worldWidth;
            this.worldHeight = worldHeight;
            this.x = 0;
            this.y = 0;
            this.targetX = 0;
            this.targetY = 0;
            this.smoothing = 0.08;
            this.shakeAmount = 0;
            this.shakeDecay = 0.9;
        }
        
        follow(target, dt) {
            const targetCenterX = target.x - this.canvas.width / 2 + target.width / 2;
            const targetCenterY = target.y - this.canvas.height / 2 + target.height / 2;
            
            this.targetX = Utils.clamp(targetCenterX, 0, this.worldWidth - this.canvas.width);
            this.targetY = Utils.clamp(targetCenterY, 0, this.worldHeight - this.canvas.height);
            
            this.x = Utils.lerp(this.x, this.targetX, this.smoothing);
            this.y = Utils.lerp(this.y, this.targetY, this.smoothing);
            
            // 屏幕震动
            if (this.shakeAmount > 0.5) {
                this.x += Utils.randomRange(-this.shakeAmount, this.shakeAmount);
                this.y += Utils.randomRange(-this.shakeAmount, this.shakeAmount);
                this.shakeAmount *= this.shakeDecay;
            } else {
                this.shakeAmount = 0;
            }
        }
        
        shake(amount) {
            this.shakeAmount = amount;
        }
        
        worldToScreen(worldX, worldY) {
            return {
                x: worldX - this.x,
                y: worldY - this.y
            };
        }
        
        screenToWorld(screenX, screenY) {
            return {
                x: screenX + this.x,
                y: screenY + this.y
            };
        }
        
        isVisible(x, y, width, height) {
            return x + width > this.x && 
                   x < this.x + this.canvas.width &&
                   y + height > this.y &&
                   y < this.y + this.canvas.height;
        }
    }

    // ============================================
    // 实体基类
    // ============================================
    class Entity {
        constructor(x, y, width, height) {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
            this.vx = 0;
            this.vy = 0;
            this.active = true;
            this.rotation = 0;
            this.layer = 0;
        }
        
        get centerX() {
            return this.x + this.width / 2;
        }
        
        get centerY() {
            return this.y + this.height / 2;
        }
        
        update(dt, game) {
            // 子类实现
        }
        
        render(ctx, viewport) {
            // 子类实现
        }
        
        collidesWith(other) {
            return this.x < other.x + other.width &&
                   this.x + this.width > other.x &&
                   this.y < other.y + other.height &&
                   this.y + this.height > other.y;
        }
    }

    // ============================================
    // 玩家类
    // ============================================
    class Player extends Entity {
        constructor(x, y) {
            super(x, y, CONFIG.PLAYER_SIZE, CONFIG.PLAYER_SIZE);
            this.speed = CONFIG.PLAYER_SPEED;
            this.health = 100;
            this.maxHealth = 100;
            this.score = 0;
            this.dashCooldown = 0;
            this.dashDuration = 0;
            this.isDashing = false;
            this.dashDir = new Vector2();
            this.shootCooldown = 0;
            this.invincibleTime = 0;
            this.animTime = 0;
        }
        
        update(dt, game) {
            this.animTime += dt;
            
            // 移动输入
            const moveDir = new Vector2();
            if (game.input.isKeyDown('KeyW') || game.input.isKeyDown('ArrowUp')) moveDir.y -= 1;
            if (game.input.isKeyDown('KeyS') || game.input.isKeyDown('ArrowDown')) moveDir.y += 1;
            if (game.input.isKeyDown('KeyA') || game.input('ArrowLeft')) moveDir.x -= 1;
            if (game.input.isKeyDown('KeyD') || game.input.isKeyDown('ArrowRight')) moveDir.x += 1;
            
            // 冲刺
            if (this.dashCooldown > 0) this.dashCooldown -= dt;
            if (this.dashDuration > 0) {
                this.dashDuration -= dt;
                this.vx = this.dashDir.x * CONFIG.PLAYER_DASH_SPEED;
                this.vy = this.dashDir.y * CONFIG.PLAYER_DASH_SPEED;
                if (this.dashDuration <= 0) this.isDashing = false;
            } else {
                if (moveDir.length() > 0) {
                    moveDir.normalize();
                    this.vx = moveDir.x * this.speed;
                    this.vy = moveDir.y * this.speed;
                } else {
                    this.vx *= 0.85;
                    this.vy *= 0.85;
                }
                
                // 冲刺触发
                if (game.input.isKeyDown('Space') && this.dashCooldown <= 0 && moveDir.length() > 0) {
                    this.isDashing = true;
                    this.dashDuration = 0.15;
                    this.dashCooldown = 1.0;
                    this.dashDir.copy(moveDir);
                    this.invincibleTime = 0.2;
                }
            }
            
            // 更新位置
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            // 世界边界
            this.x = Utils.clamp(this.x, 0, CONFIG.WORLD_WIDTH - this.width);
            this.y = Utils.clamp(this.y, 0, CONFIG.WORLD_HEIGHT - this.height);
            
            // 朝向鼠标
            this.rotation = Utils.angle(
                this.centerX, this.centerY,
                game.input.mouse.worldX, game.input.mouse.worldY
            );
            
            // 射击
            if (this.shootCooldown > 0) this.shootCooldown -= dt;
            if (game.input.mouse.leftDown && this.shootCooldown <= 0) {
                this.shoot(game);
            }
            
            // 无敌时间
            if (this.invincibleTime > 0) this.invincibleTime -= dt;
        }
        
        shoot(game) {
            this.shootCooldown = 0.12;
            
            const bulletX = this.centerX + Math.cos(this.rotation) * 20;
            const bulletY = this.centerY + Math.sin(this.rotation) * 20;
            
            game.addBullet(bulletX, bulletY, this.rotation);
            game.viewport.shake(3);
        }
        
        takeDamage(amount, game) {
            if (this.invincibleTime > 0 || this.isDashing) return;
            
            this.health -= amount;
            this.invincibleTime = 0.5;
            game.viewport.shake(8);
            
            if (this.health <= 0) {
                this.health = 0;
                this.active = false;
            }
        }
        
        render(ctx, viewport) {
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const centerX = screenPos.x + this.width / 2;
            const centerY = screenPos.y + this.height / 2;
            
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(this.rotation);
            
            // 冲刺特效
            if (this.isDashing) {
                ctx.shadowColor = '#4ecdc4';
                ctx.shadowBlur = 20;
            }
            
            // 闪烁效果（受伤无敌）
            const alpha = this.invincibleTime > 0 ? (Math.sin(this.animTime * 30) > 0 ? 1 : 0.3) : 1;
            ctx.globalAlpha = alpha;
            
            // 身体
            ctx.fillStyle = '#2a9d8f';
            ctx.beginPath();
            ctx.arc(0, 0, this.width / 2, 0, Math.PI * 2);
            ctx.fill();
            
            // 外环
            ctx.strokeStyle = '#4ecdc4';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(0, 0, this.width / 2 + 2, 0, Math.PI * 2);
            ctx.stroke();
            
            // 武器
            ctx.fillStyle = '#264653';
            ctx.fillRect(8, -4, 18, 8);
            ctx.fillStyle = '#e76f51';
            ctx.fillRect(22, -3, 6, 6);
            
            ctx.restore();
        }
    }

    // ============================================
    // 子弹类
    // ============================================
    class Bullet extends Entity {
        constructor(x, y, angle) {
            super(x - CONFIG.BULLET_SIZE / 2, y - CONFIG.BULLET_SIZE / 2, CONFIG.BULLET_SIZE, CONFIG.BULLET_SIZE);
            this.vx = Math.cos(angle) * CONFIG.BULLET_SPEED;
            this.vy = Math.sin(angle) * CONFIG.BULLET_SPEED;
            this.rotation = angle;
            this.damage = 25;
            this.trail = [];
        }
        
        update(dt, game) {
            // 记录轨迹
            this.trail.push({ x: this.x, y: this.y, alpha: 1 });
            if (this.trail.length > 8) this.trail.shift();
            this.trail.forEach(t => t.alpha *= 0.8);
            
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            // 超出边界
            if (this.x < -50 || this.x > CONFIG.WORLD_WIDTH + 50 ||
                this.y < -50 || this.y > CONFIG.WORLD_HEIGHT + 50) {
                this.active = false;
            }
        }
        
        render(ctx, viewport) {
            // 轨迹
            this.trail.forEach((t, i) => {
                const screenPos = viewport.worldToScreen(t.x, t.y);
                ctx.fillStyle = `rgba(255, 217, 61, ${t.alpha * 0.5})`;
                ctx.beginPath();
                ctx.arc(screenPos.x + this.width / 2, screenPos.y + this.height / 2, 
                       this.width / 2 * (i / this.trail.length), 0, Math.PI * 2);
                ctx.fill();
            });
            
            const screenPos = viewport.worldToScreen(this.x, this.y);
            
            ctx.save();
            ctx.shadowColor = '#ffd93d';
            ctx.shadowBlur = 10;
            
            ctx.fillStyle = '#ffd93d';
            ctx.beginPath();
            ctx.arc(screenPos.x + this.width / 2, screenPos.y + this.height / 2, this.width / 2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(screenPos.x + this.width / 2, screenPos.y + this.height / 2, this.width / 4, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
        }
    }

    // ============================================
    // 僵尸类
    // ============================================
    class Zombie extends Entity {
        constructor(x, y) {
            super(x, y, CONFIG.ZOMBIE_SIZE, CONFIG.ZOMBIE_SIZE);
            this.speed = CONFIG.ZOMBIE_SPEED + Utils.randomRange(-20, 20);
            this.health = 50;
            this.maxHealth = 50;
            this.damage = 10;
            this.attackCooldown = 0;
            this.animTime = Math.random() * Math.PI * 2;
            this.wobble = 0;
        }
        
        update(dt, game) {
            if (!this.active) return;
            
            this.animTime += dt * 4;
            this.wobble = Math.sin(this.animTime) * 0.1;
            
            // 追踪玩家
            const dx = game.player.centerX - this.centerX;
            const dy = game.player.centerY - this.centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            if (dist > 0) {
                this.vx = (dx / dist) * this.speed;
                this.vy = (dy / dist) * this.speed;
            }
            
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            // 边界
            this.x = Utils.clamp(this.x, 0, CONFIG.WORLD_WIDTH - this.width);
            this.y = Utils.clamp(this.y, 0, CONFIG.WORLD_HEIGHT - this.height);
            
            // 攻击冷却
            if (this.attackCooldown > 0) this.attackCooldown -= dt;
            
            // 碰撞玩家
            if (this.collidesWith(game.player) && this.attackCooldown <= 0) {
                game.player.takeDamage(this.damage, game);
                this.attackCooldown = 0.8;
            }
        }
        
        takeDamage(amount, game) {
            this.health -= amount;
            
            if (this.health <= 0) {
                this.active = false;
                game.player.score += 10;
                game.viewport.shake(4);
            }
        }
        
        render(ctx, viewport) {
            if (!viewport.isVisible(this.x, this.y, this.width, this.height)) return;
            
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const centerX = screenPos.x + this.width / 2;
            const centerY = screenPos.y + this.height / 2;
            
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(this.wobble);
            
            // 身体
            ctx.fillStyle = '#5a7a4a';
            ctx.beginPath();
            ctx.arc(0, 0, this.width / 2, 0, Math.PI * 2);
            ctx.fill();
            
            // 腐斑
            ctx.fillStyle = '#3a5a3a';
            ctx.beginPath();
            ctx.arc(-5, -5, 6, 0, Math.PI * 2);
            ctx.arc(6, 3, 4, 0, Math.PI * 2);
            ctx.fill();
            
            // 眼睛
            ctx.fillStyle = '#ff6b6b';
            ctx.shadowColor = '#ff6b6b';
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.arc(-5, -2, 3, 0, Math.PI * 2);
            ctx.arc(5, -2, 3, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.shadowBlur = 0;
            
            // 血条
            const healthPercent = this.health / this.maxHealth;
            const barWidth = 30;
            const barHeight = 4;
            
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(-barWidth / 2, -this.height / 2 - 12, barWidth, barHeight);
            
            ctx.fillStyle = healthPercent > 0.3 ? '#4ecdc4' : '#ff3d3d';
            ctx.fillRect(-barWidth / 2, -this.height / 2 - 12, barWidth * healthPercent, barHeight);
            
            ctx.restore();
        }
    }

    // ============================================
    // 粒子类
    // ============================================
    class Particle extends Entity {
        constructor(x, y, vx, vy, color, size, life) {
            super(x, y, size, size);
            this.vx = vx;
            this.vy = vy;
            this.color = color;
            this.life = life;
            this.maxLife = life;
            this.gravity = 200;
        }
        
        update(dt, game) {
            this.vy += this.gravity * dt;
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            this.life -= dt;
            
            if (this.life <= 0) {
                this.active = false;
            }
        }
        
        render(ctx, viewport) {
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const alpha = this.life / this.maxLife;
            const scale = alpha;
            
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(screenPos.x + this.width / 2, screenPos.y + this.height / 2, 
                   (this.width / 2) * scale, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    // ============================================
    // 渲染器
    // ============================================
    class Renderer {
        constructor(canvas, ctx) {
            this.canvas = canvas;
            this.ctx = ctx;
            this.layers = new Map();
        }
        
        clear() {
            this.ctx.fillStyle = '#050607';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        }
        
        renderBackground(viewport) {
            const gridSize = CONFIG.GRID_SIZE;
            const offsetX = -viewport.x % gridSize;
            const offsetY = -viewport.y % gridSize;
            
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
            this.ctx.lineWidth = 1;
            
            // 网格
            for (let x = offsetX; x < this.canvas.width; x += gridSize) {
                this.ctx.beginPath();
                this.ctx.moveTo(x, 0);
                this.ctx.lineTo(x, this.canvas.height);
                this.ctx.stroke();
            }
            
            for (let y = offsetY; y < this.canvas.height; y += gridSize) {
                this.ctx.beginPath();
                this.ctx.moveTo(0, y);
                this.ctx.lineTo(this.canvas.width, y);
                this.ctx.stroke();
            }
            
            // 世界边界
            const borderScreen = viewport.worldToScreen(0, 0);
            this.ctx.strokeStyle = '#ff3d3d';
            this.ctx.lineWidth = 3;
            this.ctx.strokeRect(borderScreen.x, borderScreen.y, CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT);
        }
        
        renderEntities(entities, viewport) {
            // 按层级排序
            const sorted = [...entities].sort((a, b) => a.layer - b.layer);
            
            for (const entity of sorted) {
                if (entity.active) {
                    entity.render(this.ctx, viewport);
                }
            }
        }
        
        renderCrosshair(input) {
            const x = input.mouse.x;
            const y = input.mouse.y;
            
            this.ctx.save();
            this.ctx.strokeStyle = '#ff3d3d';
            this.ctx.lineWidth = 2;
            
            // 十字准心
            this.ctx.beginPath();
            this.ctx.moveTo(x - 12, y);
            this.ctx.lineTo(x - 4, y);
            this.ctx.moveTo(x + 4, y);
            this.ctx.lineTo(x + 12, y);
            this.ctx.moveTo(x, y - 12);
            this.ctx.lineTo(x, y - 4);
            this.ctx.moveTo(x, y + 4);
            this.ctx.lineTo(x, y + 12);
            this.ctx.stroke();
            
            // 中心点
            this.ctx.fillStyle = '#ff3d3d';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 2, 0, Math.PI * 2);
            this.ctx.fill();
            
            this.ctx.restore();
        }
        
        renderMinimap(player, zombies, viewport) {
            const mapSize = 120;
            const mapX = this.canvas.width - mapSize - 20;
            const mapY = this.canvas.height - mapSize - 80;
            const scale = mapSize / CONFIG.WORLD_WIDTH;
            
            // 背景
            this.ctx.fillStyle = 'rgba(10, 12, 15, 0.8)';
            this.ctx.fillRect(mapX, mapY, mapSize, mapSize);
            
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(mapX, mapY, mapSize, mapSize);
            
            // 视口范围
            this.ctx.strokeStyle = 'rgba(78, 205, 196, 0.3)';
            this.ctx.strokeRect(
                mapX + viewport.x * scale,
                mapY + viewport.y * scale,
                this.canvas.width * scale,
                this.canvas.height * scale
            );
            
            // 僵尸
            this.ctx.fillStyle = '#7a9e5a';
            for (const zombie of zombies) {
                if (zombie.active) {
                    this.ctx.beginPath();
                    this.ctx.arc(
                        mapX + zombie.centerX * scale,
                        mapY + zombie.centerY * scale,
                        2, 0, Math.PI * 2
                    );
                    this.ctx.fill();
                }
            }
            
            // 玩家
            this.ctx.fillStyle = '#4ecdc4';
            this.ctx.beginPath();
            this.ctx.arc(
                mapX + player.centerX * scale,
                mapY + player.centerY * scale,
                4, 0, Math.PI * 2
            );
            this.ctx.fill();
        }
    }

    // ============================================
    // 游戏主类
    // ============================================
    class Game {
        constructor() {
            this.canvas = document.getElementById('gameCanvas');
            this.ctx = this.canvas.getContext('2d');
            
            this.resize();
            window.addEventListener('resize', () => this.resize());
            
            this.input = new InputManager(this.canvas);
            this.viewport = new Viewport(this.canvas, CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT);
            this.renderer = new Renderer(this.canvas, this.ctx);
            
            this.player = null;
            this.bullets = [];
            this.zombies = [];
            this.particles = [];
            
            this.wave = 1;
            this.spawnTimer = 0;
            this.lastTime = 0;
            this.fpsTime = 0;
            this.fpsCount = 0;
            this.fps = 60;
            
            this.init();
        }
        
        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
        
        init() {
            // 创建玩家
            this.player = new Player(CONFIG.WORLD_WIDTH / 2, CONFIG.WORLD_HEIGHT / 2);
            
            // 初始僵尸
            for (let i = 0; i < 5; i++) {
                this.spawnZombie();
            }
            
            // 开始游戏循环
            this.lastTime = performance.now();
            requestAnimationFrame((time) => this.gameLoop(time));
        }
        
        gameLoop(currentTime) {
            const dt = Math.min((currentTime - this.lastTime) / 1000, 0.05);
            this.lastTime = currentTime;
            
            // FPS计算
            this.fpsCount++;
            this.fpsTime += dt;
            if (this.fpsTime >= 1) {
                this.fps = this.fpsCount;
                this.fpsCount = 0;
                this.fpsTime = 0;
            }
            
            this.update(dt);
            this.render();
            
            requestAnimationFrame((time) => this.gameLoop(time));
        }
        
        update(dt) {
            // 更新输入
            this.input.updateWorldMouse(this.viewport);
            
            // 更新玩家
            if (this.player.active) {
                this.player.update(dt, this);
            }
            
            // 更新视口
            this.viewport.follow(this.player, dt);
            
            // 更新子弹
            for (const bullet of this.bullets) {
                if (bullet.active) {
                    bullet.update(dt, this);
                    
                    // 子弹与僵尸碰撞
                    for (const zombie of this.zombies) {
                        if (zombie.active && bullet.collidesWith(zombie)) {
                            zombie.takeDamage(bullet.damage, this);
                            bullet.active = false;
                            
                            // 粒子效果
                            this.spawnHitParticles(bullet.centerX, bullet.centerY);
                            break;
                        }
                    }
                }
            }
            
            // 更新僵尸
            for (const zombie of this.zombies) {
                if (zombie.active) {
                    zombie.update(dt, this);
                }
            }
            
            // 更新粒子
            for (const particle of this.particles) {
                if (particle.active) {
                    particle.update(dt, this);
                }
            }
            
            // 清理非活动实体
            this.bullets = this.bullets.filter(b => b.active);
            this.zombies = this.zombies.filter(z => z.active);
            this.particles = this.particles.filter(p => p.active);
            
            // 僵尸生成
            this.spawnTimer += dt * 1000;
            const spawnRate = Math.max(500, CONFIG.SPAWN_RATE - this.wave * 150);
            
            if (this.spawnTimer >= spawnRate && this.zombies.length < CONFIG.MAX_ZOMBIES) {
                this.spawnZombie();
                this.spawnTimer = 0;
            }
            
            // 波次升级
            if (this.player.score > 0 && this.player.score % 100 === 0) {
                this.wave = Math.floor(this.player.score / 100) + 1;
            }
            
            // 更新UI
            this.updateUI();
        }
        
        render() {
            // 清除画布
            this.renderer.clear();
            
            // 渲染背景
            this.renderer.renderBackground(this.viewport);
            
            // 收集所有实体
            const entities = [
                ...this.particles,
                ...this.zombies,
                ...this.bullets,
                this.player
            ];
            
            // 渲染实体
            this.renderer.renderEntities(entities, this.viewport);
            
            // 渲染十字准心
            this.renderer.renderCrosshair(this.input);
            
            // 渲染小地图
            this.renderer.renderMinimap(this.player, this.zombies, this.viewport);
        }
        
        addBullet(x, y, angle) {
            const bullet = new Bullet(x, y, angle);
            this.bullets.push(bullet);
        }
        
        spawnZombie() {
            // 在玩家周围生成，但不在视野内
            let x, y;
            const minDist = 400;
            const maxDist = 600;
            
            do {
                const angle = Math.random() * Math.PI * 2;
                const dist = Utils.randomRange(minDist, maxDist);
                x = this.player.centerX + Math.cos(angle) * dist;
                y = this.player.centerY + Math.sin(angle) * dist;
            } while (
                x < 50 || x > CONFIG.WORLD_WIDTH - 50 ||
                y < 50 || y > CONFIG.WORLD_HEIGHT - 50
            );
            
            const zombie = new Zombie(x - CONFIG.ZOMBIE_SIZE / 2, y - CONFIG.ZOMBIE_SIZE / 2);
            this.zombies.push(zombie);
        }
        
        spawnHitParticles(x, y) {
            for (let i = 0; i < 8; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Utils.randomRange(100, 250);
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed - 100;
                const size = Utils.randomRange(3, 6);
                const life = Utils.randomRange(0.3, 0.6);
                const color = Math.random() > 0.5 ? '#7a9e5a' : '#5a7a4a';
                
                this.particles.push(new Particle(x, y, vx, vy, color, size, life));
            }
        }
        
        updateUI() {
            document.getElementById('score').textContent = this.player.score;
            document.getElementById('health').textContent = this.player.health;
            document.getElementById('wave').textContent = this.wave;
            document.getElementById('fpsValue').textContent = this.fps;
            document.getElementById('objectCount').textContent = 
                this.bullets.length + this.zombies.length + this.particles.length;
            document.getElementById('viewportPos').textContent = 
                `${Math.round(this.viewport.x)}, ${Math.round(this.viewport.y)}`;
            document.getElementById('playerPos').textContent = 
                `${Math.round(this.player.x)}, ${Math.round(this.player.y)}`;
        }
    }

    // ============================================
    // 游戏初始化
    // ============================================
    window.addEventListener('DOMContentLoaded', () => {
        new Game();
    });
    </script>
</body>
</html>
```

## 框架架构说明

### 1. 核心模块结构

| 模块 | 职责 |
|------|------|
| `Game` | 游戏主类，协调所有子系统，管理游戏循环 |
| `Viewport` | 视口管理，实现摄像机跟随和坐标转换 |
| `InputManager` | 输入处理，统一管理键盘和鼠标事件 |
| `Renderer` | 渲染管线，分层绘制背景/实体/UI |

### 2. 游戏循环特性

- **60FPS 主循环**：使用 `requestAnimationFrame` 实现
- **时间步长**：deltaTime 约束在 50ms 内防止跳帧
- **帧率计数**：每秒统计实际 FPS

### 3. 渲染管线顺序

```
清除画布 → 绘制背景网格 → 绘制粒子(底层) 
         → 绘制僵尸 → 绘制子弹 → 绘制玩家(顶层)
         → 绘制十字准心 → 绘制小地图
```

### 4. 坐标系统

- **世界坐标**：2000×2000 的游戏世界
- **屏幕坐标**：Canvas 视口内的相对位置
- **视口跟随**：带平滑插值和边界约束

### 5. 实体系统

- `Entity` 基类包含位置/速度/碰撞检测
- 所有游戏对象继承 Entity 并实现 `update()` / `render()`
- 支持分层渲染 (`layer` 属性)

### 6. 交互功能

| 按键 | 功能 |
|------|------|
| WASD / 方向键 | 移动玩家 |
| 鼠标移动 | 瞄准方向 |
| 左键点击 | 射击 |
| Space | 冲刺（带冷却） |

这是一个完整的、可扩展的游戏框架，你可以在此基础上继续添加更多游戏内容（武器系统、道具、波次系统等）。