# 僵尸AI与群体行为

**Time**: 2026-03-01T13:37:02.400840

---

我来为你实现完整的僵尸AI与群体行为系统。这将包括波次式生成器、不同僵尸类型、追踪AI、攻击判定和死亡动画。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zombie Slayer - 僵尸AI系统</title>
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
            --player-glow: rgba(78, 205, 196, 0.5);
            --zombie: #7a9e5a;
            --zombie-fast: #c4a35a;
            --zombie-tank: #5a7a9e;
            --bullet: #ffd93d;
            --bullet-glow: rgba(255, 217, 61, 0.6);
            --ground: #1a1d21;
            --grid: rgba(255,255,255,0.03);
            --muzzle: #ff9500;
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

        .health-bar {
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 20px;
            border-radius: 4px;
        }

        .health-bar-label {
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 6px;
        }

        .health-bar-track {
            width: 200px;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }

        .health-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), #ff6b6b);
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        .dash-indicator {
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 20px;
            border-radius: 4px;
        }

        .dash-indicator-label {
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 6px;
        }

        .dash-bar-track {
            width: 120px;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
        }

        .dash-bar-fill {
            height: 100%;
            background: var(--player);
            border-radius: 3px;
            transition: width 0.1s ease;
        }

        .ammo-display {
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 20px;
            border-radius: 4px;
        }

        .ammo-label {
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 6px;
        }

        .ammo-count {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            font-weight: 700;
        }

        .ammo-current {
            color: var(--bullet);
        }

        .ammo-separator {
            color: var(--muted);
            margin: 0 4px;
        }

        .ammo-reserve {
            color: var(--fg);
            font-size: 18px;
        }

        .ammo-reloading {
            color: var(--accent);
            font-size: 14px;
            animation: blink 0.5s infinite;
        }

        .wave-display {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 12, 15, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 30px;
            border-radius: 4px;
            text-align: center;
        }

        .wave-label {
            font-size: 11px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .wave-number {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 900;
            color: var(--accent);
        }

        .wave-info {
            font-size: 12px;
            color: var(--muted);
            margin-top: 4px;
        }

        .zombie-counter {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(10, 12, 15, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 20px;
            border-radius: 4px;
            text-align: right;
        }

        .zombie-counter-label {
            font-size: 11px;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .zombie-count {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: var(--zombie);
        }

        .fps-counter {
            position: absolute;
            bottom: 20px;
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
            gap: 20px;
        }

        .controls-hint kbd {
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 3px;
            color: var(--fg);
            font-family: inherit;
        }

        .wave-announcement {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .wave-announcement.active {
            opacity: 1;
        }

        .wave-announcement-text {
            font-family: 'Orbitron', sans-serif;
            font-size: 48px;
            font-weight: 900;
            color: var(--accent);
            text-shadow: 0 0 30px var(--accent-glow);
            letter-spacing: 4px;
        }

        .wave-announcement-sub {
            font-size: 16px;
            color: var(--muted);
            margin-top: 10px;
            letter-spacing: 2px;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .damage-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            background: radial-gradient(ellipse at center, transparent 50%, rgba(255, 61, 61, 0.3) 100%);
            opacity: 0;
            transition: opacity 0.1s ease;
        }

        .damage-overlay.active {
            opacity: 1;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <div id="ui-overlay">
        <div class="hud">
            <div class="health-bar">
                <div class="health-bar-label">HEALTH</div>
                <div class="health-bar-track">
                    <div class="health-bar-fill" id="healthFill" style="width: 100%"></div>
                </div>
            </div>
            <div class="dash-indicator">
                <div class="dash-indicator-label">DASH</div>
                <div class="dash-bar-track">
                    <div class="dash-bar-fill" id="dashFill" style="width: 100%"></div>
                </div>
            </div>
            <div class="ammo-display">
                <div class="ammo-label">AMMO</div>
                <div class="ammo-count" id="ammoDisplay">
                    <span class="ammo-current">12</span>
                    <span class="ammo-separator">/</span>
                    <span class="ammo-reserve">60</span>
                </div>
            </div>
            <div class="hud-item">
                KILLS: <span id="killCount">0</span>
            </div>
        </div>
        
        <div class="wave-display">
            <div class="wave-label">WAVE</div>
            <div class="wave-number" id="waveNumber">1</div>
            <div class="wave-info" id="waveInfo">Preparing...</div>
        </div>
        
        <div class="zombie-counter">
            <div class="zombie-counter-label">ZOMBIES</div>
            <div class="zombie-count" id="zombieCount">0</div>
        </div>
        
        <div class="fps-counter">FPS: <span id="fpsValue">60</span></div>
        
        <div class="controls-hint">
            <span><kbd>WASD</kbd> Move</span>
            <span><kbd>SHIFT</kbd> Dash</span>
            <span><kbd>LMB</kbd> Shoot</span>
            <span><kbd>R</kbd> Reload</span>
        </div>
        
        <div class="wave-announcement" id="waveAnnouncement">
            <div class="wave-announcement-text" id="announcementText">WAVE 1</div>
            <div class="wave-announcement-sub">INCOMING</div>
        </div>
        
        <div class="damage-overlay" id="damageOverlay"></div>
    </div>

    <script>
    // ============================================
    // 游戏配置常量
    // ============================================
    const CONFIG = {
        WORLD_WIDTH: 2000,
        WORLD_HEIGHT: 2000,
        PLAYER_SPEED: 280,
        PLAYER_DASH_SPEED: 650,
        PLAYER_SIZE: 24,
        PLAYER_ACCELERATION: 2000,
        PLAYER_FRICTION: 12,
        PLAYER_MAX_HEALTH: 100,
        BULLET_SPEED: 700,
        BULLET_SIZE: 6,
        BULLET_TRAIL_LENGTH: 8,
        GRID_SIZE: 50,
        // 弹药系统配置
        MAGAZINE_SIZE: 12,
        RESERVE_AMMO: 60,
        RELOAD_TIME: 1.8,
        FIRE_RATE: 150,
        MUZZLE_FLASH_DURATION: 0.08,
        // 僵尸配置
        ZOMBIE_BASE_SPEED: 85,
        ZOMBIE_BASE_SIZE: 28,
        ZOMBIE_BASE_HEALTH: 50,
        ZOMBIE_ATTACK_RANGE: 40,
        ZOMBIE_ATTACK_DAMAGE: 10,
        ZOMBIE_ATTACK_COOLDOWN: 1.0,
        MAX_ZOMBIES: 50,
        // 波次配置
        WAVE_BASE_ZOMBIES: 5,
        WAVE_ZOMBIE_INCREMENT: 3,
        WAVE_DELAY: 3.0,
        SPAWN_INTERVAL: 0.5
    };

    // ============================================
    // 僵尸类型定义
    // ============================================
    const ZOMBIE_TYPES = {
        NORMAL: {
            name: 'Normal',
            color: '#7a9e5a',
            glowColor: 'rgba(122, 158, 90, 0.4)',
            speed: 1.0,
            health: 1.0,
            size: 1.0,
            damage: 1.0,
            weight: 60
        },
        FAST: {
            name: 'Fast',
            color: '#c4a35a',
            glowColor: 'rgba(196, 163, 90, 0.4)',
            speed: 1.6,
            health: 0.5,
            size: 0.85,
            damage: 0.7,
            weight: 25
        },
        TANK: {
            name: 'Tank',
            color: '#5a7a9e',
            glowColor: 'rgba(90, 122, 158, 0.4)',
            speed: 0.5,
            health: 3.0,
            size: 1.5,
            damage: 1.5,
            weight: 15
        }
    };

    // ============================================
    // 僵尸状态枚举
    // ============================================
    const ZOMBIE_STATE = {
        SPAWNING: 'spawning',
        IDLE: 'idle',
        CHASE: 'chase',
        ATTACK: 'attack',
        DYING: 'dying',
        DEAD: 'dead'
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
        },
        
        weightedRandom(items) {
            const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);
            let random = Math.random() * totalWeight;
            for (const item of items) {
                random -= item.weight;
                if (random <= 0) return item;
            }
            return items[items.length - 1];
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
                if (['Space', 'KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyR', 
                     'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
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
            
            if (this.shakeAmount > 0.5) {
                this.x += Utils.randomRange(-this.shakeAmount, this.shakeAmount);
                this.y += Utils.randomRange(-this.shakeAmount, this.shakeAmount);
                this.shakeAmount *= this.shakeDecay;
            } else {
                this.shakeAmount = 0;
            }
        }
        
        shake(amount) {
            this.shakeAmount = Math.max(this.shakeAmount, amount);
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
            const margin = 100;
            return x + width + margin > this.x && 
                   x - margin < this.x + this.canvas.width &&
                   y + height + margin > this.y &&
                   y - margin < this.y + this.canvas.height;
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
        
        update(dt, game) {}
        render(ctx, viewport) {}
        
        collidesWith(other) {
            const dx = this.centerX - other.centerX;
            const dy = this.centerY - other.centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const combinedRadius = (this.width + other.width) / 2;
            return dist < combinedRadius;
        }
    }

    // ============================================
    // 子弹类
    // ============================================
    class Bullet extends Entity {
        constructor(x, y, angle, damage = 25) {
            super(x - CONFIG.BULLET_SIZE / 2, y - CONFIG.BULLET_SIZE / 2, 
                  CONFIG.BULLET_SIZE, CONFIG.BULLET_SIZE);
            this.angle = angle;
            this.speed = CONFIG.BULLET_SPEED;
            this.damage = damage;
            this.vx = Math.cos(angle) * this.speed;
            this.vy = Math.sin(angle) * this.speed;
            this.lifeTime = 2;
            this.trail = [];
            this.maxTrailLength = CONFIG.BULLET_TRAIL_LENGTH;
            this.hitEntities = new Set();
        }
        
        update(dt, game) {
            this.trail.unshift({ x: this.centerX, y: this.centerY });
            if (this.trail.length > this.maxTrailLength) {
                this.trail.pop();
            }
            
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            this.lifeTime -= dt;
            if (this.lifeTime <= 0) {
                this.active = false;
            }
            
            if (this.x < -50 || this.x > CONFIG.WORLD_WIDTH + 50 ||
                this.y < -50 || this.y > CONFIG.WORLD_HEIGHT + 50) {
                this.active = false;
            }
        }
        
        render(ctx, viewport) {
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const screenCenterX = screenPos.x + this.width / 2;
            const screenCenterY = screenPos.y + this.height / 2;
            
            if (this.trail.length > 1) {
                ctx.save();
                ctx.lineCap = 'round';
                
                for (let i = 0; i < this.trail.length - 1; i++) {
                    const t = this.trail[i];
                    const t2 = this.trail[i + 1];
                    const screenT = viewport.worldToScreen(t.x - this.width / 2, t.y - this.height / 2);
                    const screenT2 = viewport.worldToScreen(t2.x - this.width / 2, t2.y - this.height / 2);
                    
                    const alpha = 1 - (i / this.trail.length);
                    const width = Utils.lerp(1, CONFIG.BULLET_SIZE * 0.8, alpha);
                    
                    ctx.beginPath();
                    ctx.moveTo(screenT.x + this.width / 2, screenT.y + this.height / 2);
                    ctx.lineTo(screenT2.x + this.width / 2, screenT2.y + this.height / 2);
                    ctx.strokeStyle = `rgba(255, 217, 61, ${alpha * 0.6})`;
                    ctx.lineWidth = width;
                    ctx.stroke();
                }
                
                ctx.restore();
            }
            
            ctx.save();
            ctx.translate(screenCenterX, screenCenterY);
            
            const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, CONFIG.BULLET_SIZE * 2);
            gradient.addColorStop(0, 'rgba(255, 217, 61, 0.8)');
            gradient.addColorStop(0.5, 'rgba(255, 180, 50, 0.3)');
            gradient.addColorStop(1, 'rgba(255, 150, 50, 0)');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(0, 0, CONFIG.BULLET_SIZE * 2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#ffd93d';
            ctx.beginPath();
            ctx.arc(0, 0, CONFIG.BULLET_SIZE / 2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-CONFIG.BULLET_SIZE / 4, -CONFIG.BULLET_SIZE / 4, CONFIG.BULLET_SIZE / 6, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
        }
    }

    // ============================================
    // 玩家类
    // ============================================
    class Player extends Entity {
        constructor(x, y) {
            super(x - CONFIG.PLAYER_SIZE / 2, y - CONFIG.PLAYER_SIZE / 2, 
                  CONFIG.PLAYER_SIZE, CONFIG.PLAYER_SIZE);
            
            this.health = CONFIG.PLAYER_MAX_HEALTH;
            this.maxHealth = CONFIG.PLAYER_MAX_HEALTH;
            this.speed = CONFIG.PLAYER_SPEED;
            this.dashSpeed = CONFIG.PLAYER_DASH_SPEED;
            
            this.vx = 0;
            this.vy = 0;
            this.acceleration = CONFIG.PLAYER_ACCELERATION;
            this.friction = CONFIG.PLAYER_FRICTION;
            
            this.isDashing = false;
            this.dashDuration = 0.15;
            this.dashTimer = 0;
            this.dashCooldown = 1.0;
            this.dashCooldownTimer = 0;
            this.dashDirection = new Vector2();
            
            this.aimAngle = 0;
            this.muzzleFlash = 0;
            
            // 弹药系统
            this.currentAmmo = CONFIG.MAGAZINE_SIZE;
            this.reserveAmmo = CONFIG.RESERVE_AMMO;
            this.isReloading = false;
            this.reloadTimer = 0;
            this.lastFireTime = 0;
            
            this.invincible = false;
            this.invincibleTimer = 0;
        }
        
        update(dt, game) {
            // 无敌时间
            if (this.invincible) {
                this.invincibleTimer -= dt;
                if (this.invincibleTimer <= 0) {
                    this.invincible = false;
                }
            }
            
            // 冲刺逻辑
            if (this.isDashing) {
                this.dashTimer -= dt;
                if (this.dashTimer <= 0) {
                    this.isDashing = false;
                }
            } else {
                this.dashCooldownTimer = Math.max(0, this.dashCooldownTimer - dt);
            }
            
            // 移动处理
            if (!this.isDashing) {
                this.handleMovement(dt, game.input);
            } else {
                this.vx = this.dashDirection.x * this.dashSpeed;
                this.vy = this.dashDirection.y * this.dashSpeed;
            }
            
            // 应用速度
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            // 边界限制
            this.x = Utils.clamp(this.x, 0, CONFIG.WORLD_WIDTH - this.width);
            this.y = Utils.clamp(this.y, 0, CONFIG.WORLD_HEIGHT - this.height);
            
            // 更新瞄准角度
            this.aimAngle = Utils.angle(this.centerX, this.centerY, 
                                        game.input.mouse.worldX, game.input.mouse.worldY);
            
            // 射击
            if (game.input.mouse.leftDown && !this.isReloading) {
                this.tryShoot(game);
            }
            
            // 换弹
            if (this.isReloading) {
                this.reloadTimer -= dt;
                if (this.reloadTimer <= 0) {
                    this.finishReload();
                }
            }
            
            // R键换弹
            if (game.input.isKeyDown('KeyR') && !this.isReloading && 
                this.currentAmmo < CONFIG.MAGAZINE_SIZE && this.reserveAmmo > 0) {
                this.startReload();
            }
            
            // 枪口闪光衰减
            if (this.muzzleFlash > 0) {
                this.muzzleFlash -= dt / CONFIG.MUZZLE_FLASH_DURATION;
            }
        }
        
        handleMovement(dt, input) {
            const moveDir = new Vector2();
            
            if (input.isKeyDown('KeyW') || input.isKeyDown('ArrowUp')) moveDir.y -= 1;
            if (input.isKeyDown('KeyS') || input.isKeyDown('ArrowDown')) moveDir.y += 1;
            if (input.isKeyDown('KeyA') || input.isKeyDown('ArrowLeft')) moveDir.x -= 1;
            if (input.isKeyDown('KeyD') || input.isKeyDown('ArrowRight')) moveDir.x += 1;
            
            // 冲刺
            if (input.isKeyDown('ShiftLeft') && moveDir.length() > 0 && 
                this.dashCooldownTimer <= 0 && !this.isDashing) {
                this.startDash(moveDir);
            }
            
            if (moveDir.length() > 0) {
                moveDir.normalize();
                this.vx += moveDir.x * this.acceleration * dt;
                this.vy += moveDir.y * this.acceleration * dt;
                
                const currentSpeed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (currentSpeed > this.speed) {
                    const scale = this.speed / currentSpeed;
                    this.vx *= scale;
                    this.vy *= scale;
                }
            } else {
                this.vx *= (1 - this.friction * dt);
                this.vy *= (1 - this.friction * dt);
                
                if (Math.abs(this.vx) < 1) this.vx = 0;
                if (Math.abs(this.vy) < 1) this.vy = 0;
            }
        }
        
        startDash(direction) {
            this.isDashing = true;
            this.dashTimer = this.dashDuration;
            this.dashCooldownTimer = this.dashCooldown;
            this.dashDirection.copy(direction).normalize();
            this.invincible = true;
            this.invincibleTimer = this.dashDuration;
        }
        
        tryShoot(game) {
            const now = performance.now();
            if (now - this.lastFireTime < CONFIG.FIRE_RATE) return;
            if (this.currentAmmo <= 0) {
                this.startReload();
                return;
            }
            
            this.lastFireTime = now;
            this.currentAmmo--;
            this.muzzleFlash = 1;
            
            // 创建子弹
            const bulletX = this.centerX + Math.cos(this.aimAngle) * (CONFIG.PLAYER_SIZE / 2 + 10);
            const bulletY = this.centerY + Math.sin(this.aimAngle) * (CONFIG.PLAYER_SIZE / 2 + 10);
            
            // 轻微散布
            const spread = Utils.randomRange(-0.03, 0.03);
            const bullet = new Bullet(bulletX, bulletY, this.aimAngle + spread, 25);
            game.addEntity(bullet);
            
            game.viewport.shake(3);
        }
        
        startReload() {
            if (this.reserveAmmo <= 0) return;
            this.isReloading = true;
            this.reloadTimer = CONFIG.RELOAD_TIME;
        }
        
        finishReload() {
            const needed = CONFIG.MAGAZINE_SIZE - this.currentAmmo;
            const available = Math.min(needed, this.reserveAmmo);
            this.currentAmmo += available;
            this.reserveAmmo -= available;
            this.isReloading = false;
        }
        
        takeDamage(amount, game) {
            if (this.invincible || this.isDashing) return;
            
            this.health -= amount;
            this.invincible = true;
            this.invincibleTimer = 0.5;
            game.viewport.shake(8);
            
            // 显示受伤效果
            const overlay = document.getElementById('damageOverlay');
            overlay.classList.add('active');
            setTimeout(() => overlay.classList.remove('active'), 100);
            
            if (this.health <= 0) {
                this.health = 0;
                game.gameOver();
            }
        }
        
        getDashCooldownPercent() {
            return 1 - (this.dashCooldownTimer / this.dashCooldown);
        }
        
        render(ctx, viewport) {
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const screenCenterX = screenPos.x + this.width / 2;
            const screenCenterY = screenPos.y + this.height / 2;
            
            ctx.save();
            ctx.translate(screenCenterX, screenCenterY);
            
            // 无敌闪烁
            if (this.invincible && Math.floor(performance.now() / 50) % 2 === 0) {
                ctx.globalAlpha = 0.5;
            }
            
            // 发光效果
            const glowGradient = ctx.createRadialGradient(0, 0, 0, 0, 0, CONFIG.PLAYER_SIZE * 1.5);
            glowGradient.addColorStop(0, 'rgba(78, 205, 196, 0.3)');
            glowGradient.addColorStop(1, 'rgba(78, 205, 196, 0)');
            ctx.fillStyle = glowGradient;
            ctx.beginPath();
            ctx.arc(0, 0, CONFIG.PLAYER_SIZE * 1.5, 0, Math.PI * 2);
            ctx.fill();
            
            // 身体
            ctx.fillStyle = '#4ecdc4';
            ctx.beginPath();
            ctx.arc(0, 0, CONFIG.PLAYER_SIZE / 2, 0, Math.PI * 2);
            ctx.fill();
            
            // 边框
            ctx.strokeStyle = '#3db8af';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // 武器
            ctx.save();
            ctx.rotate(this.aimAngle);
            ctx.fillStyle = '#2a3a38';
            ctx.fillRect(CONFIG.PLAYER_SIZE / 2 - 4, -3, 20, 6);
            ctx.fillStyle = '#1a2826';
            ctx.fillRect(CONFIG.PLAYER_SIZE / 2 + 10, -2, 8, 4);
            ctx.restore();
            
            // 枪口闪光
            if (this.muzzleFlash > 0) {
                const muzzleX = Math.cos(this.aimAngle) * (CONFIG.PLAYER_SIZE / 2 + 18);
                const muzzleY = Math.sin(this.aimAngle) * (CONFIG.PLAYER_SIZE / 2 + 18);
                
                const muzzleGradient = ctx.createRadialGradient(muzzleX, muzzleY, 0, muzzleX, muzzleY, 15);
                muzzleGradient.addColorStop(0, `rgba(255, 149, 0, ${this.muzzleFlash})`);
                muzzleGradient.addColorStop(0.5, `rgba(255, 100, 0, ${this.muzzleFlash * 0.5})`);
                muzzleGradient.addColorStop(1, 'rgba(255, 50, 0, 0)');
                
                ctx.fillStyle = muzzleGradient;
                ctx.beginPath();
                ctx.arc(muzzleX, muzzleY, 15, 0, Math.PI * 2);
                ctx.fill();
            }
            
            ctx.restore();
        }
    }

    // ============================================
    // 僵尸类 - 带状态机
    // ============================================
    class Zombie extends Entity {
        constructor(x, y, type = ZOMBIE_TYPES.NORMAL) {
            const size = CONFIG.ZOMBIE_BASE_SIZE * type.size;
            super(x - size / 2, y - size / 2, size, size);
            
            this.type = type;
            this.health = CONFIG.ZOMBIE_BASE_HEALTH * type.health;
            this.maxHealth = this.health;
            this.speed = CONFIG.ZOMBIE_BASE_SPEED * type.speed;
            this.damage = CONFIG.ZOMBIE_ATTACK_DAMAGE * type.damage;
            this.attackRange = CONFIG.ZOMBIE_ATTACK_RANGE + size / 2;
            this.attackCooldown = CONFIG.ZOMBIE_ATTACK_COOLDOWN;
            this.attackTimer = 0;
            
            // 状态机
            this.state = ZOMBIE_STATE.SPAWNING;
            this.stateTimer = 0;
            
            // 生成动画
            this.spawnProgress = 0;
            this.spawnDuration = 0.5;
            
            // 死亡动画
            this.deathProgress = 0;
            this.deathDuration = 0.4;
            
            // 移动
            this.targetAngle = 0;
            this.wobbleOffset = Math.random() * Math.PI * 2;
            this.wobbleSpeed = Utils.randomRange(3, 5);
            
            // 群体行为
            this.separationForce = new Vector2();
            this.alignmentForce = new Vector2();
            this.cohesionForce = new Vector2();
            
            this.layer = 1;
        }
        
        update(dt, game) {
            this.stateTimer += dt;
            
            switch (this.state) {
                case ZOMBIE_STATE.SPAWNING:
                    this.updateSpawning(dt);
                    break;
                case ZOMBIE_STATE.CHASE:
                    this.updateChase(dt, game);
                    break;
                case ZOMBIE_STATE.ATTACK:
                    this.updateAttack(dt, game);
                    break;
                case ZOMBIE_STATE.DYING:
                    this.updateDying(dt);
                    break;
                case ZOMBIE_STATE.DEAD:
                    this.active = false;
                    break;
            }
            
            // 攻击冷却
            if (this.attackTimer > 0) {
                this.attackTimer -= dt;
            }
        }
        
        updateSpawning(dt) {
            this.spawnProgress += dt / this.spawnDuration;
            if (this.spawnProgress >= 1) {
                this.spawnProgress = 1;
                this.setState(ZOMBIE_STATE.CHASE);
            }
        }
        
        updateChase(dt, game) {
            const player = game.player;
            if (!player) return;
            
            const dist = Utils.distance(this.centerX, this.centerY, 
                                        player.centerX, player.centerY);
            
            // 攻击范围检测
            if (dist < this.attackRange) {
                this.setState(ZOMBIE_STATE.ATTACK);
                return;
            }
            
            // 计算朝向玩家的方向
            const dirX = player.centerX - this.centerX;
            const dirY = player.centerY - this.centerY;
            const dist2 = Math.sqrt(dirX * dirX + dirY * dirY);
            
            if (dist2 > 0) {
                // 群体行为
                this.calculateFlocking(game);
                
                // 组合移动方向
                let moveX = dirX / dist2 + this.separationForce.x * 0.5;
                let moveY = dirY / dist2 + this.separationForce.y * 0.5;
                
                // 摇摆效果
                const wobble = Math.sin(performance.now() / 1000 * this.wobbleSpeed + this.wobbleOffset);
                const perpX = -moveY;
                const perpY = moveX;
                moveX += perpX * wobble * 0.2;
                moveY += perpY * wobble * 0.2;
                
                // 归一化并应用速度
                const moveLen = Math.sqrt(moveX * moveX + moveY * moveY);
                if (moveLen > 0) {
                    this.vx = (moveX / moveLen) * this.speed;
                    this.vy = (moveY / moveLen) * this.speed;
                }
                
                this.targetAngle = Math.atan2(dirY, dirX);
            }
            
            // 应用速度
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            // 边界限制
            this.x = Utils.clamp(this.x, 0, CONFIG.WORLD_WIDTH - this.width);
            this.y = Utils.clamp(this.y, 0, CONFIG.WORLD_HEIGHT - this.height);
        }
        
        updateAttack(dt, game) {
            const player = game.player;
            if (!player) return;
            
            const dist = Utils.distance(this.centerX, this.centerY, 
                                        player.centerX, player.centerY);
            
            // 如果玩家离开攻击范围，返回追逐
            if (dist > this.attackRange * 1.5) {
                this.setState(ZOMBIE_STATE.CHASE);
                return;
            }
            
            // 执行攻击
            if (this.attackTimer <= 0 && dist < this.attackRange) {
                player.takeDamage(this.damage, game);
                this.attackTimer = this.attackCooldown;
            }
            
            // 仍然缓慢移动
            const dirX = player.centerX - this.centerX;
            const dirY = player.centerY - this.centerY;
            const dist2 = Math.sqrt(dirX * dirX + dirY * dirY);
            
            if (dist2 > 0) {
                this.vx = (dirX / dist2) * this.speed * 0.3;
                this.vy = (dirY / dist2) * this.speed * 0.3;
            }
            
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            
            this.targetAngle = Math.atan2(dirY, dirX);
        }
        
        updateDying(dt) {
            this.deathProgress += dt / this.deathDuration;
            if (this.deathProgress >= 1) {
                this.setState(ZOMBIE_STATE.DEAD);
            }
        }
        
        calculateFlocking(game) {
            this.separationForce.set(0, 0);
            let neighborCount = 0;
            
            for (const entity of game.entities) {
                if (entity === this || !(entity instanceof Zombie)) continue;
                if (entity.state === ZOMBIE_STATE.DYING || entity.state === ZOMBIE_STATE.DEAD) continue;
                
                const dist = Utils.distance(this.centerX, this.centerY, 
                                           entity.centerX, entity.centerY);
                
                if (dist < 60 && dist > 0) {
                    // 分离力 - 避免重叠
                    const force = (60 - dist) / 60;
                    this.separationForce.x += (this.centerX - entity.centerX) / dist * force;
                    this.separationForce.y += (this.centerY - entity.centerY) / dist * force;
                    neighborCount++;
                }
            }
            
            if (neighborCount > 0) {
                this.separationForce.x /= neighborCount;
                this.separationForce.y /= neighborCount;
            }
        }
        
        setState(newState) {
            this.state = newState;
            this.stateTimer = 0;
        }
        
        takeDamage(damage, game) {
            if (this.state === ZOMBIE_STATE.DYING || this.state === ZOMBIE_STATE.DEAD) return;
            
            this.health -= damage;
            
            // 击退效果
            const angle = Utils.angle(game.player.centerX, game.player.centerY, 
                                     this.centerX, this.centerY);
            this.x += Math.cos(angle) * 10;
            this.y += Math.sin(angle) * 10;
            
            // 创建伤害数字
            game.createDamageNumber(this.centerX, this.centerY, damage);
            
            if (this.health <= 0) {
                this.die(game);
            }
        }
        
        die(game) {
            this.setState(ZOMBIE_STATE.DYING);
            game.kills++;
            game.createDeathParticles(this.centerX, this.centerY, this.type.color);
            game.viewport.shake(4);
        }
        
        render(ctx, viewport) {
            if (!viewport.isVisible(this.x, this.y, this.width, this.height)) return;
            
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const screenCenterX = screenPos.x + this.width / 2;
            const screenCenterY = screenPos.y + this.height / 2;
            
            ctx.save();
            ctx.translate(screenCenterX, screenCenterY);
            
            let scale = 1;
            let alpha = 1;
            
            // 状态相关渲染
            switch (this.state) {
                case ZOMBIE_STATE.SPAWNING:
                    scale = Utils.lerp(0.3, 1, this.spawnProgress);
                    alpha = Utils.lerp(0, 1, this.spawnProgress);
                    break;
                case ZOMBIE_STATE.DYING:
                    scale = Utils.lerp(1, 1.3, this.deathProgress);
                    alpha = 1 - this.deathProgress;
                    break;
            }
            
            ctx.globalAlpha = alpha;
            ctx.scale(scale, scale);
            
            // 发光效果
            const glowGradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.width);
            glowGradient.addColorStop(0, this.type.glowColor);
            glowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = glowGradient;
            ctx.beginPath();
            ctx.arc(0, 0, this.width, 0, Math.PI * 2);
            ctx.fill();
            
            // 身体
            ctx.save();
            ctx.rotate(this.targetAngle);
            
            // 主体
            ctx.fillStyle = this.type.color;
            ctx.beginPath();
            ctx.arc(0, 0, this.width / 2, 0, Math.PI * 2);
            ctx.fill();
            
            // 阴影边框
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            // 眼睛
            const eyeOffset = this.width / 5;
            ctx.fillStyle = '#ff3d3d';
            ctx.beginPath();
            ctx.arc(eyeOffset, -eyeOffset / 2, 3, 0, Math.PI * 2);
            ctx.arc(eyeOffset, eyeOffset / 2, 3, 0, Math.PI * 2);
            ctx.fill();
            
            // 爪子
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
            ctx.beginPath();
            ctx.moveTo(this.width / 2 - 5, -8);
            ctx.lineTo(this.width / 2 + 8, -5);
            ctx.lineTo(this.width / 2 + 8, 5);
            ctx.lineTo(this.width / 2 - 5, 8);
            ctx.closePath();
            ctx.fill();
            
            ctx.restore();
            
            // 血量条
            if (this.health < this.maxHealth && this.state !== ZOMBIE_STATE.DYING) {
                const barWidth = this.width;
                const barHeight = 4;
                const healthPercent = this.health / this.maxHealth;
                
                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.fillRect(-barWidth / 2, -this.height / 2 - 10, barWidth, barHeight);
                
                ctx.fillStyle = `rgb(${255 - healthPercent * 155}, ${healthPercent * 100}, 50)`;
                ctx.fillRect(-barWidth / 2, -this.height / 2 - 10, barWidth * healthPercent, barHeight);
            }
            
            ctx.restore();
        }
    }

    // ============================================
    // 伤害数字
    // ============================================
    class DamageNumber {
        constructor(x, y, damage) {
            this.x = x;
            this.y = y;
            this.damage = damage;
            this.lifeTime = 0.8;
            this.timer = 0;
            this.vy = -80;
            this.active = true;
        }
        
        update(dt) {
            this.timer += dt;
            this.y += this.vy * dt;
            this.vy *= 0.95;
            
            if (this.timer >= this.lifeTime) {
                this.active = false;
            }
        }
        
        render(ctx, viewport) {
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const alpha = 1 - (this.timer / this.lifeTime);
            const scale = Utils.lerp(1.2, 0.8, this.timer / this.lifeTime);
            
            ctx.save();
            ctx.translate(screenPos.x, screenPos.y);
            ctx.scale(scale, scale);
            ctx.globalAlpha = alpha;
            
            ctx.font = 'bold 16px Orbitron';
            ctx.textAlign = 'center';
            ctx.fillStyle = '#ff3d3d';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.strokeText(Math.round(this.damage), 0, 0);
            ctx.fillText(Math.round(this.damage), 0, 0);
            
            ctx.restore();
        }
    }

    // ============================================
    // 死亡粒子
    // ============================================
    class DeathParticle {
        constructor(x, y, color) {
            this.x = x;
            this.y = y;
            this.color = color;
            this.vx = Utils.randomRange(-150, 150);
            this.vy = Utils.randomRange(-150, 50);
            this.size = Utils.randomRange(3, 8);
            this.lifeTime = Utils.randomRange(0.3, 0.6);
            this.timer = 0;
            this.active = true;
        }
        
        update(dt) {
            this.timer += dt;
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            this.vy += 300 * dt; // 重力
            
            if (this.timer >= this.lifeTime) {
                this.active = false;
            }
        }
        
        render(ctx, viewport) {
            const screenPos = viewport.worldToScreen(this.x, this.y);
            const alpha = 1 - (this.timer / this.lifeTime);
            
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(screenPos.x, screenPos.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    // ============================================
    // 波次管理器
    // ============================================
    class WaveManager {
        constructor(game) {
            this.game = game;
            this.currentWave = 0;
            this.zombiesRemaining = 0;
            this.zombiesToSpawn = 0;
            this.spawnTimer = 0;
            this.waveDelay = CONFIG.WAVE_DELAY;
            this.waveDelayTimer = 0;
            this.isWaveActive = false;
            this.isBetweenWaves = true;
        }
        
        startNextWave() {
            this.currentWave++;
            this.isWaveActive = true;
            this.isBetweenWaves = false;
            
            // 计算本波僵尸数量
            this.zombiesToSpawn = CONFIG.WAVE_BASE_ZOMBIES + 
                                  (this.currentWave - 1) * CONFIG.WAVE_ZOMBIE_INCREMENT;
            this.zombiesRemaining = this.zombiesToSpawn;
            this.spawnTimer = 0;
            
            // 显示波次公告
            this.showWaveAnnouncement();
            
            // 更新UI
            document.getElementById('waveNumber').textContent = this.currentWave;
            document.getElementById('waveInfo').textContent = `Spawning ${this.zombiesToSpawn} zombies`;
        }
        
        showWaveAnnouncement() {
            const announcement = document.getElementById('waveAnnouncement');
            const text = document.getElementById('announcementText');
            text.textContent = `WAVE ${this.currentWave}`;
            announcement.classList.add('active');
            
            setTimeout(() => {
                announcement.classList.remove('active');
            }, 2000);
        }
        
        update(dt) {
            if (this.isBetweenWaves) {
                this.waveDelayTimer -= dt;
                if (this.waveDelayTimer <= 0) {
                    this.startNextWave();
                }
                return;
            }
            
            if (!this.isWaveActive) return;
            
            // 生成僵尸
            if (this.zombiesToSpawn > 0) {
                this.spawnTimer += dt;
                if (this.spawnTimer >= CONFIG.SPAWN_INTERVAL) {
                    this.spawnTimer = 0;
                    this.spawnZombie();
                    this.zombiesToSpawn--;
                }
            }
            
            // 检查波次是否完成
            const activeZombies = this.countActiveZombies();
            document.getElementById('zombieCount').textContent = activeZombies;
            
            if (this.zombiesToSpawn <= 0 && activeZombies <= 0) {
                this.endWave();
            }
        }
        
        countActiveZombies() {
            let count = 0;
            for (const entity of this.game.entities) {
                if (entity instanceof Zombie && 
                    entity.state !== ZOMBIE_STATE.DYING && 
                    entity.state !== ZOMBIE_STATE.DEAD) {
                    count++;
                }
            }
            return count;
        }
        
        spawnZombie() {
            // 在玩家周围生成，但不在视野内
            const player = this.game.player;
            const minDist = 400;
            const maxDist = 600;
            
            const angle = Math.random() * Math.PI * 2;
            const dist = Utils.randomRange(minDist, maxDist);
            
            let x = player.centerX + Math.cos(angle) * dist;
            let y = player.centerY + Math.sin(angle) * dist;
            
            // 确保在世界边界内
            x = Utils.clamp(x, 50, CONFIG.WORLD_WIDTH - 50);
            y = Utils.clamp(y, 50, CONFIG.WORLD_HEIGHT - 50);
            
            // 根据波次选择僵尸类型
            const type = this.selectZombieType();
            const zombie = new Zombie(x, y, type);
            this.game.addEntity(zombie);
        }
        
        selectZombieType() {
            // 根据波次调整权重
            const types = Object.values(ZOMBIE_TYPES).map(type => {
                let weight = type.weight;
                
                // 后期波次增加特殊僵尸权重
                if (this.currentWave >= 3 && type.name === 'Fast') {
                    weight += 10;
                }
                if (this.currentWave >= 5 && type.name === 'Tank') {
                    weight += 10;
                }
                
                return { ...type, weight };
            });
            
            return Utils.weightedRandom(types);
        }
        
        endWave() {
            this.isWaveActive = false;
            this.isBetweenWaves = true;
            this.waveDelayTimer = CONFIG.WAVE_DELAY;
            
            document.getElementById('waveInfo').textContent = 'Wave Complete!';
            
            // 奖励弹药
            this.game.player.reserveAmmo = Math.min(
                this.game.player.reserveAmmo + 15,
                CONFIG.RESERVE_AMMO * 2
            );
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
            
            this.entities = [];
            this.damageNumbers = [];
            this.particles = [];
            
            this.player = new Player(CONFIG.WORLD_WIDTH / 2, CONFIG.WORLD_HEIGHT / 2);
            this.addEntity(this.player);
            
            this.waveManager = new WaveManager(this);
            
            this.kills = 0;
            this.isGameOver = false;
            
            this.lastTime = 0;
            this.fps = 60;
            this.fpsUpdateTimer = 0;
            
            // 启动第一波
            this.waveManager.waveDelayTimer = 1.0;
            
            this.start();
        }
        
        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
        
        start() {
            requestAnimationFrame((time) => this.gameLoop(time));
        }
        
        gameLoop(time) {
            const dt = Math.min((time - this.lastTime) / 1000, 0.1);
            this.lastTime = time;
            
            // FPS计算
            this.fpsUpdateTimer += dt;
            if (this.fpsUpdateTimer >= 0.5) {
                this.fps = Math.round(1 / dt);
                document.getElementById('fpsValue').textContent = this.fps;
                this.fpsUpdateTimer = 0;
            }
            
            if (!this.isGameOver) {
                this.update(dt);
            }
            
            this.render();
            
            requestAnimationFrame((t) => this.gameLoop(t));
        }
        
        update(dt) {
            // 更新输入
            this.input.updateWorldMouse(this.viewport);
            
            // 更新视口
            this.viewport.follow(this.player, dt);
            
            // 更新波次
            this.waveManager.update(dt);
            
            // 更新实体
            for (let i = this.entities.length - 1; i >= 0; i--) {
                const entity = this.entities[i];
                if (entity.active) {
                    entity.update(dt, this);
                }
                if (!entity.active) {
                    this.entities.splice(i, 1);
                }
            }
            
            // 更新伤害数字
            for (let i = this.damageNumbers.length - 1; i >= 0; i--) {
                const dn = this.damageNumbers[i];
                dn.update(dt);
                if (!dn.active) {
                    this.damageNumbers.splice(i, 1);
                }
            }
            
            // 更新粒子
            for (let i = this.particles.length - 1; i >= 0; i--) {
                const p = this.particles[i];
                p.update(dt);
                if (!p.active) {
                    this.particles.splice(i, 1);
                }
            }
            
            // 碰撞检测
            this.checkCollisions();
            
            // 更新UI
            this.updateUI();
        }
        
        checkCollisions() {
            const bullets = this.entities.filter(e => e instanceof Bullet);
            const zombies = this.entities.filter(e => e instanceof Zombie && 
                                                     e.state !== ZOMBIE_STATE.DYING && 
                                                     e.state !== ZOMBIE_STATE.DEAD);
            
            for (const bullet of bullets) {
                if (!bullet.active) continue;
                
                for (const zombie of zombies) {
                    if (bullet.hitEntities.has(zombie)) continue;
                    
                    if (bullet.collidesWith(zombie)) {
                        zombie.takeDamage(bullet.damage, this);
                        bullet.hitEntities.add(zombie);
                        bullet.active = false;
                        break;
                    }
                }
            }
        }
        
        render() {
            const ctx = this.ctx;
            
            // 清屏
            ctx.fillStyle = '#050607';
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            // 渲染背景网格
            this.renderBackground(ctx);
            
            // 渲染粒子（在实体下方）
            for (const p of this.particles) {
                p.render(ctx, this.viewport);
            }
            
            // 按层级排序并渲染实体
            const sortedEntities = [...this.entities].sort((a, b) => a.layer - b.layer);
            for (const entity of sortedEntities) {
                entity.render(ctx, this.viewport);
            }
            
            // 渲染伤害数字（最上层）
            for (const dn of this.damageNumbers) {
                dn.render(ctx, this.viewport);
            }
        }
        
        renderBackground(ctx) {
            const gridSize = CONFIG.GRID_SIZE;
            const offsetX = -this.viewport.x % gridSize;
            const offsetY = -this.viewport.y % gridSize;
            
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
            ctx.lineWidth = 1;
            
            // 垂直线
            for (let x = offsetX; x < this.canvas.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, this.canvas.height);
                ctx.stroke();
            }
            
            // 水平线
            for (let y = offsetY; y < this.canvas.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(this.canvas.width, y);
                ctx.stroke();
            }
            
            // 世界边界
            const border = this.viewport.worldToScreen(0, 0);
            const borderEnd = this.viewport.worldToScreen(CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT);
            
            ctx.strokeStyle = 'rgba(255, 61, 61, 0.3)';
            ctx.lineWidth = 2;
            ctx.strokeRect(border.x, border.y, 
                          borderEnd.x - border.x, 
                          borderEnd.y - border.y);
        }
        
        addEntity(entity) {
            this.entities.push(entity);
        }
        
        createDamageNumber(x, y, damage) {
            this.damageNumbers.push(new DamageNumber(x, y, damage));
        }
        
        createDeathParticles(x, y, color) {
            for (let i = 0; i < 8; i++) {
                this.particles.push(new DeathParticle(x, y, color));
            }
        }
        
        updateUI() {
            // 血量
            const healthPercent = (this.player.health / this.player.maxHealth) * 100;
            document.getElementById('healthFill').style.width = `${healthPercent}%`;
            
            // 冲刺
            const dashPercent = this.player.getDashCooldownPercent() * 100;
            document.getElementById('dashFill').style.width = `${dashPercent}%`;
            
            // 弹药
            const ammoDisplay = document.getElementById('ammoDisplay');
            if (this.player.isReloading) {
                ammoDisplay.innerHTML = '<span class="ammo-reloading">RELOADING</span>';
            } else {
                ammoDisplay.innerHTML = `<span class="ammo-current">${this.player.currentAmmo}</span>` +
                                        '<span class="ammo-separator">/</span>' +
                                        `<span class="ammo-reserve">${this.player.reserveAmmo}</span>`;
            }
            
            // 击杀数
            document.getElementById('killCount').textContent = this.kills;
        }
        
        gameOver() {
            this.isGameOver = true;
            
            // 显示游戏结束
            const announcement = document.getElementById('waveAnnouncement');
            const text = document.getElementById('announcementText');
            text.textContent = 'GAME OVER';
            text.style.color = '#ff3d3d';
            document.querySelector('.wave-announcement-sub').textContent = `Kills: ${this.kills} | Wave: ${this.waveManager.currentWave}`;
            announcement.classList.add('active');
        }
    }

    // 启动游戏
    window.addEventListener('load', () => {
        new Game();
    });
    </script>
</body>
</html>
```

## 主要实现内容

### 1. 僵尸类型系统
定义了三种僵尸类型，每种有独特的属性：
- **普通僵尸**：平衡的属性，绿色外观
- **快速僵尸**：速度快但血量低，黄色外观
- **坦克僵尸**：血量高速度慢，蓝色外观

### 2. 僵尸状态机
实现了完整的六状态机：
- `SPAWNING` - 生成动画（从小变大淡入）
- `IDLE` - 空闲状态
- `CHASE` - 追逐玩家，带群体避让行为
- `ATTACK` - 攻击状态，接近玩家时造成伤害
- `DYING` - 死亡动画（放大淡出）
- `DEAD` - 死亡，从游戏中移除

### 3. 波次生成系统
- 渐进式难度：每波增加3个僵尸
- 波次间有延迟，给玩家喘息时间
- 根据波次调整特殊僵尸出现概率
- 波次完成奖励弹药补给

### 4. 群体AI行为
- **分离力**：僵尸之间保持距离，避免重叠
- **追踪AI**：持续向玩家移动
- **摇摆效果**：自然的不规则移动

### 5. 战斗系统
- 僵尸攻击带冷却时间
- 玩家受伤无敌帧
- 击退效果
- 伤害数字显示
- 死亡粒子效果
- 屏幕震动反馈