# 游戏框架与Canvas渲染引擎

**Time**: 2026-02-28T22:35:14.889637

---

好的，我来为你搭建一个完整的赛车游戏框架，包含Canvas渲染引擎、资源加载器、状态机和性能监控面板。设计风格采用赛博朋克/霓虹科技感，契合赛车游戏的主题。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neon Racer - Game Framework</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
        
        :root {
            --bg-dark: #0a0a0f;
            --bg-panel: rgba(15, 15, 25, 0.95);
            --neon-cyan: #00f5ff;
            --neon-pink: #ff2d75;
            --neon-yellow: #f0ff00;
            --neon-green: #00ff88;
            --text-primary: #e0e0e0;
            --text-muted: #6a6a7a;
            --border-color: rgba(0, 245, 255, 0.3);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Share Tech Mono', monospace;
            background: var(--bg-dark);
            color: var(--text-primary);
            overflow: hidden;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        #gameContainer {
            position: relative;
            width: 100%;
            max-width: 1200px;
            aspect-ratio: 16/9;
        }
        
        #gameCanvas {
            display: block;
            width: 100%;
            height: 100%;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            box-shadow: 
                0 0 30px rgba(0, 245, 255, 0.15),
                inset 0 0 60px rgba(0, 0, 0, 0.5);
        }
        
        #performancePanel {
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px 16px;
            font-size: 12px;
            min-width: 180px;
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        
        #performancePanel h3 {
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            color: var(--neon-cyan);
            margin-bottom: 8px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .perf-row {
            display: flex;
            justify-content: space-between;
            margin: 4px 0;
            padding: 2px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .perf-label {
            color: var(--text-muted);
        }
        
        .perf-value {
            font-weight: bold;
            font-family: 'Orbitron', sans-serif;
        }
        
        .perf-value.fps { color: var(--neon-green); }
        .perf-value.frame { color: var(--neon-yellow); }
        .perf-value.memory { color: var(--neon-pink); }
        
        #controls {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px 16px;
            font-size: 11px;
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        
        #controls h4 {
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            color: var(--neon-pink);
            margin-bottom: 6px;
            letter-spacing: 1px;
        }
        
        .key-hint {
            display: inline-block;
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 3px;
            margin: 2px;
            font-size: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        #loadingScreen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--bg-dark);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
            transition: opacity 0.5s ease;
        }
        
        #loadingScreen.hidden {
            opacity: 0;
            pointer-events: none;
        }
        
        #loadingScreen h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            color: var(--neon-cyan);
            margin-bottom: 20px;
            text-shadow: 0 0 20px var(--neon-cyan);
        }
        
        .loading-bar-container {
            width: 300px;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .loading-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-pink));
            transition: width 0.3s ease;
        }
        
        #loadingStatus {
            margin-top: 10px;
            font-size: 12px;
            color: var(--text-muted);
        }
        
        @media (max-width: 768px) {
            #performancePanel, #controls {
                transform: scale(0.85);
                transform-origin: top right;
            }
            #controls {
                transform-origin: bottom left;
            }
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        
        <div id="loadingScreen">
            <h2>NEON RACER</h2>
            <div class="loading-bar-container">
                <div class="loading-bar" id="loadingBar"></div>
            </div>
            <div id="loadingStatus">Initializing...</div>
        </div>
        
        <div id="performancePanel">
            <h3>Performance</h3>
            <div class="perf-row">
                <span class="perf-label">FPS</span>
                <span class="perf-value fps" id="fpsValue">0</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Frame Time</span>
                <span class="perf-value frame" id="frameTimeValue">0ms</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Draw Calls</span>
                <span class="perf-value" id="drawCallsValue">0</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Objects</span>
                <span class="perf-value" id="objectCountValue">0</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">State</span>
                <span class="perf-value" id="stateValue" style="color: var(--neon-cyan);">MENU</span>
            </div>
        </div>
        
        <div id="controls">
            <h4>Controls</h4>
            <span class="key-hint">W/S</span> Accelerate/Brake
            <br>
            <span class="key-hint">A/D</span> Steer
            <br>
            <span class="key-hint">ESC</span> Pause
            <br>
            <span class="key-hint">SPACE</span> Start/Resume
        </div>
    </div>

    <script>
    // ============================================
    // 游戏配置常量
    // ============================================
    const CONFIG = {
        TARGET_FPS: 60,
        CANVAS_WIDTH: 1200,
        CANVAS_HEIGHT: 675,
        ROAD_WIDTH: 400,
        LANE_COUNT: 3,
        COLORS: {
            bgDark: '#0a0a0f',
            road: '#1a1a2e',
            roadLine: '#00f5ff',
            roadLineGlow: 'rgba(0, 245, 255, 0.5)',
            neonCyan: '#00f5ff',
            neonPink: '#ff2d75',
            neonYellow: '#f0ff00',
            neonGreen: '#00ff88',
            neonOrange: '#ff8800'
        }
    };

    // ============================================
    // 工具类：数学辅助
    // ============================================
    class MathUtils {
        static lerp(a, b, t) {
            return a + (b - a) * t;
        }
        
        static clamp(value, min, max) {
            return Math.max(min, Math.min(max, value));
        }
        
        static randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }
        
        static randomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }
        
        static easeInOutQuad(t) {
            return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        }
        
        static easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }
    }

    // ============================================
    // 资源加载器
    // ============================================
    class ResourceLoader {
        constructor() {
            this.resources = new Map();
            this.loadingProgress = 0;
            this.totalResources = 0;
            this.loadedResources = 0;
        }
        
        loadImages(imageList) {
            return new Promise((resolve) => {
                this.totalResources = imageList.length;
                this.loadedResources = 0;
                
                if (imageList.length === 0) {
                    resolve();
                    return;
                }
                
                imageList.forEach(({ name, src }) => {
                    const img = new Image();
                    img.onload = () => {
                        this.resources.set(name, img);
                        this.loadedResources++;
                        this.loadingProgress = this.loadedResources / this.totalResources;
                        
                        if (this.loadedResources === this.totalResources) {
                            resolve();
                        }
                    };
                    img.onerror = () => {
                        console.warn(`Failed to load: ${src}`);
                        this.loadedResources++;
                        this.loadingProgress = this.loadedResources / this.totalResources;
                        
                        if (this.loadedResources === this.totalResources) {
                            resolve();
                        }
                    };
                    img.src = src;
                });
            });
        }
        
        getImage(name) {
            return this.resources.get(name);
        }
        
        getProgress() {
            return this.loadingProgress;
        }
    }

    // ============================================
    // 输入管理器
    // ============================================
    class InputManager {
        constructor() {
            this.keys = {};
            this.keysJustPressed = {};
            this.mouse = { x: 0, y: 0, clicked: false };
            
            this.bindEvents();
        }
        
        bindEvents() {
            window.addEventListener('keydown', (e) => {
                if (!this.keys[e.code]) {
                    this.keysJustPressed[e.code] = true;
                }
                this.keys[e.code] = true;
                
                // 阻止某些默认行为
                if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
                    e.preventDefault();
                }
            });
            
            window.addEventListener('keyup', (e) => {
                this.keys[e.code] = false;
            });
            
            const canvas = document.getElementById('gameCanvas');
            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                const scaleX = CONFIG.CANVAS_WIDTH / rect.width;
                const scaleY = CONFIG.CANVAS_HEIGHT / rect.height;
                this.mouse.x = (e.clientX - rect.left) * scaleX;
                this.mouse.y = (e.clientY - rect.top) * scaleY;
            });
            
            canvas.addEventListener('click', () => {
                this.mouse.clicked = true;
            });
        }
        
        isKeyDown(code) {
            return !!this.keys[code];
        }
        
        isKeyJustPressed(code) {
            return !!this.keysJustPressed[code];
        }
        
        clearJustPressed() {
            this.keysJustPressed = {};
            this.mouse.clicked = false;
        }
    }

    // ============================================
    // 性能监控器
    // ============================================
    class PerformanceMonitor {
        constructor() {
            this.fps = 0;
            this.frameTime = 0;
            this.drawCalls = 0;
            this.objectCount = 0;
            
            this.frameCount = 0;
            this.lastTime = performance.now();
            this.fpsUpdateTime = 0;
            this.frameTimeHistory = [];
            this.maxHistoryLength = 60;
            
            this.elements = {
                fps: document.getElementById('fpsValue'),
                frameTime: document.getElementById('frameTimeValue'),
                drawCalls: document.getElementById('drawCallsValue'),
                objectCount: document.getElementById('objectCountValue'),
                state: document.getElementById('stateValue')
            };
        }
        
        beginFrame() {
            this.frameStartTime = performance.now();
            this.drawCalls = 0;
            this.objectCount = 0;
        }
        
        endFrame() {
            const now = performance.now();
            const frameTime = now - this.frameStartTime;
            
            this.frameTimeHistory.push(frameTime);
            if (this.frameTimeHistory.length > this.maxHistoryLength) {
                this.frameTimeHistory.shift();
            }
            
            this.frameCount++;
            
            if (now - this.fpsUpdateTime >= 500) {
                this.fps = Math.round(this.frameCount * 1000 / (now - this.fpsUpdateTime));
                this.frameCount = 0;
                this.fpsUpdateTime = now;
                
                const sum = this.frameTimeHistory.reduce((a, b) => a + b, 0);
                this.frameTime = (sum / this.frameTimeHistory.length).toFixed(2);
                
                this.updateDisplay();
            }
        }
        
        addDrawCall(count = 1) {
            this.drawCalls += count;
        }
        
        addObject(count = 1) {
            this.objectCount += count;
        }
        
        updateDisplay() {
            this.elements.fps.textContent = this.fps;
            this.elements.frameTime.textContent = this.frameTime + 'ms';
            this.elements.drawCalls.textContent = this.drawCalls;
            this.elements.objectCount.textContent = this.objectCount;
            
            // FPS颜色指示
            if (this.fps >= 55) {
                this.elements.fps.style.color = CONFIG.COLORS.neonGreen;
            } else if (this.fps >= 30) {
                this.elements.fps.style.color = CONFIG.COLORS.neonYellow;
            } else {
                this.elements.fps.style.color = CONFIG.COLORS.neonPink;
            }
        }
        
        updateState(stateName) {
            this.elements.state.textContent = stateName;
            const stateColors = {
                'MENU': CONFIG.COLORS.neonCyan,
                'PLAYING': CONFIG.COLORS.neonGreen,
                'PAUSED': CONFIG.COLORS.neonYellow,
                'GAMEOVER': CONFIG.COLORS.neonPink
            };
            this.elements.state.style.color = stateColors[stateName] || CONFIG.COLORS.neonCyan;
        }
    }

    // ============================================
    // 游戏状态机
    // ============================================
    class GameStateMachine {
        constructor(game) {
            this.game = game;
            this.currentState = null;
            this.states = new Map();
            this.stateStartTime = 0;
        }
        
        registerState(name, state) {
            this.states.set(name, state);
        }
        
        changeState(name) {
            if (this.currentState && this.currentState.exit) {
                this.currentState.exit();
            }
            
            this.currentState = this.states.get(name);
            this.stateStartTime = performance.now();
            
            if (this.currentState && this.currentState.enter) {
                this.currentState.enter();
            }
            
            this.game.performanceMonitor.updateState(name);
            console.log(`State changed to: ${name}`);
        }
        
        update(deltaTime) {
            if (this.currentState && this.currentState.update) {
                this.currentState.update(deltaTime);
            }
        }
        
        render(ctx) {
            if (this.currentState && this.currentState.render) {
                this.currentState.render(ctx);
            }
        }
        
        getStateTime() {
            return performance.now() - this.stateStartTime;
        }
    }

    // ============================================
    // 渲染器
    // ============================================
    class Renderer {
        constructor(canvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.width = CONFIG.CANVAS_WIDTH;
            this.height = CONFIG.CANVAS_HEIGHT;
            this.layers = [];
            
            // 设置canvas实际尺寸
            this.canvas.width = this.width;
            this.canvas.height = this.height;
            
            // 禁用图像平滑以获得清晰像素
            this.ctx.imageSmoothingEnabled = false;
        }
        
        clear() {
            this.ctx.fillStyle = CONFIG.COLORS.bgDark;
            this.ctx.fillRect(0, 0, this.width, this.height);
        }
        
        save() {
            this.ctx.save();
        }
        
        restore() {
            this.ctx.restore();
        }
        
        translate(x, y) {
            this.ctx.translate(x, y);
        }
        
        scale(x, y) {
            this.ctx.scale(x, y);
        }
        
        rotate(angle) {
            this.ctx.rotate(angle);
        }
        
        setAlpha(alpha) {
            this.ctx.globalAlpha = MathUtils.clamp(alpha, 0, 1);
        }
        
        drawRect(x, y, width, height, color, fill = true) {
            if (fill) {
                this.ctx.fillStyle = color;
                this.ctx.fillRect(x, y, width, height);
            } else {
                this.ctx.strokeStyle = color;
                this.ctx.strokeRect(x, y, width, height);
            }
        }
        
        drawCircle(x, y, radius, color, fill = true) {
            const safeRadius = Math.max(0.1, radius);
            this.ctx.beginPath();
            this.ctx.arc(x, y, safeRadius, 0, Math.PI * 2);
            if (fill) {
                this.ctx.fillStyle = color;
                this.ctx.fill();
            } else {
                this.ctx.strokeStyle = color;
                this.ctx.stroke();
            }
        }
        
        drawLine(x1, y1, x2, y2, color, width = 1) {
            this.ctx.beginPath();
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = width;
            this.ctx.stroke();
        }
        
        drawText(text, x, y, options = {}) {
            const {
                color = '#ffffff',
                font = '16px Share Tech Mono',
                align = 'left',
                baseline = 'top'
            } = options;
            
            this.ctx.font = font;
            this.ctx.textAlign = align;
            this.ctx.textBaseline = baseline;
            this.ctx.fillStyle = color;
            this.ctx.fillText(text, x, y);
        }
        
        drawTextWithShadow(text, x, y, options = {}) {
            const {
                color = '#ffffff',
                shadowColor = 'rgba(0,0,0,0.8)',
                shadowBlur = 4,
                shadowOffsetX = 2,
                shadowOffsetY = 2,
                font = '16px Share Tech Mono',
                align = 'left',
                baseline = 'top'
            } = options;
            
            this.ctx.font = font;
            this.ctx.textAlign = align;
            this.ctx.textBaseline = baseline;
            
            // 阴影层
            this.ctx.shadowColor = shadowColor;
            this.ctx.shadowBlur = shadowBlur;
            this.ctx.shadowOffsetX = shadowOffsetX;
            this.ctx.shadowOffsetY = shadowOffsetY;
            this.ctx.fillStyle = color;
            this.ctx.fillText(text, x, y);
            
            // 重置阴影
            this.ctx.shadowColor = 'transparent';
            this.ctx.shadowBlur = 0;
            this.ctx.shadowOffsetX = 0;
            this.ctx.shadowOffsetY = 0;
        }
        
        drawGlowText(text, x, y, options = {}) {
            const {
                color = CONFIG.COLORS.neonCyan,
                glowColor = color,
                font = '32px Orbitron',
                align = 'center',
                baseline = 'middle'
            } = options;
            
            this.ctx.font = font;
            this.ctx.textAlign = align;
            this.ctx.textBaseline = baseline;
            
            // 外发光
            this.ctx.shadowColor = glowColor;
            this.ctx.shadowBlur = 20;
            this.ctx.fillStyle = glowColor;
            this.ctx.fillText(text, x, y);
            
            // 内发光
            this.ctx.shadowBlur = 10;
            this.ctx.fillStyle = color;
            this.ctx.fillText(text, x, y);
            
            // 清除阴影
            this.ctx.shadowColor = 'transparent';
            this.ctx.shadowBlur = 0;
        }
        
        createGradient(x0, y0, x1, y1, colorStops) {
            const gradient = this.ctx.createLinearGradient(x0, y0, x1, y1);
            colorStops.forEach(([offset, color]) => {
                gradient.addColorStop(MathUtils.clamp(offset, 0, 1), color);
            });
            return gradient;
        }
        
        createRadialGradient(x, y, r0, r1, colorStops) {
            const safeR0 = Math.max(0.1, r0);
            const safeR1 = Math.max(0.1, r1);
            const gradient = this.ctx.createRadialGradient(x, y, safeR0, x, y, safeR1);
            colorStops.forEach(([offset, color]) => {
                gradient.addColorStop(MathUtils.clamp(offset, 0, 1), color);
            });
            return gradient;
        }
        
        fillWithGradient(gradient) {
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(0, 0, this.width, this.height);
        }
        
        // 绘制带发光效果的形状
        drawGlowRect(x, y, width, height, color, glowIntensity = 10) {
            this.ctx.shadowColor = color;
            this.ctx.shadowBlur = glowIntensity;
            this.ctx.fillStyle = color;
            this.ctx.fillRect(x, y, width, height);
            this.ctx.shadowColor = 'transparent';
            this.ctx.shadowBlur = 0;
        }
    }

    // ============================================
    // 粒子系统
    // ============================================
    class Particle {
        constructor(x, y, options = {}) {
            this.x = x;
            this.y = y;
            this.vx = options.vx || 0;
            this.vy = options.vy || 0;
            this.life = options.life || 1;
            this.maxLife = this.life;
            this.size = options.size || 3;
            this.color = options.color || '#ffffff';
            this.decay = options.decay || 0.02;
            this.gravity = options.gravity || 0;
            this.friction = options.friction || 1;
            this.active = true;
        }
        
        update(deltaTime) {
            if (!this.active) return;
            
            this.life -= this.decay * deltaTime * 60;
            this.vy += this.gravity * deltaTime * 60;
            this.vx *= this.friction;
            this.vy *= this.friction;
            this.x += this.vx * deltaTime * 60;
            this.y += this.vy * deltaTime * 60;
            
            if (this.life <= 0) {
                this.active = false;
            }
        }
        
        render(ctx, renderer) {
            if (!this.active) return;
            
            const alpha = MathUtils.clamp(this.life / this.maxLife, 0, 1);
            renderer.setAlpha(alpha);
            renderer.drawCircle(this.x, this.y, this.size * alpha, this.color);
            renderer.setAlpha(1);
        }
    }

    class ParticleSystem {
        constructor() {
            this.particles = [];
        }
        
        emit(x, y, count, options = {}) {
            for (let i = 0; i < count; i++) {
                const angle = options.angle !== undefined ? options.angle : Math.random() * Math.PI * 2;
                const speed = options.speed ? MathUtils.randomRange(options.speed.min, options.speed.max) : MathUtils.randomRange(1, 5);
                
                const particle = new Particle(x, y, {
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    life: options.life ? MathUtils.randomRange(options.life.min, options.life.max) : 1,
                    size: options.size ? MathUtils.randomRange(options.size.min, options.size.max) : 3,
                    color: Array.isArray(options.colors) ? options.colors[MathUtils.randomInt(0, options.colors.length - 1)] : options.color || '#ffffff',
                    decay: options.decay || 0.02,
                    gravity: options.gravity || 0,
                    friction: options.friction || 0.98
                });
                
                this.particles.push(particle);
            }
        }
        
        update(deltaTime) {
            this.particles = this.particles.filter(p => {
                p.update(deltaTime);
                return p.active;
            });
        }
        
        render(ctx, renderer) {
            this.particles.forEach(p => p.render(ctx, renderer));
        }
        
        clear() {
            this.particles = [];
        }
    }

    // ============================================
    // 游戏对象基类
    // ============================================
    class GameObject {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.width = 0;
            this.height = 0;
            this.active = true;
            this.velocityX = 0;
            this.velocityY = 0;
        }
        
        update(deltaTime) {
            // 子类实现
        }
        
        render(renderer) {
            // 子类实现
        }
        
        getBounds() {
            return {
                x: this.x - this.width / 2,
                y: this.y - this.height / 2,
                width: this.width,
                height: this.height
            };
        }
        
        intersects(other) {
            const a = this.getBounds();
            const b = other.getBounds();
            return a.x < b.x + b.width &&
                   a.x + a.width > b.x &&
                   a.y < b.y + b.height &&
                   a.y + a.height > b.y;
        }
    }

    // ============================================
    // 玩家赛车
    // ============================================
    class PlayerCar extends GameObject {
        constructor(x, y) {
            super(x, y);
            this.width = 40;
            this.height = 70;
            this.speed = 0;
            this.maxSpeed = 15;
            this.acceleration = 0.3;
            this.brakePower = 0.5;
            this.friction = 0.02;
            this.steerSpeed = 0;
            this.maxSteerSpeed = 8;
            this.steerAcceleration = 0.5;
            this.lane = 1; // 0, 1, 2
            this.targetX = x;
            this.distance = 0;
            this.tilt = 0;
        }
        
        update(deltaTime, input) {
            // 加速/刹车
            if (input.isKeyDown('KeyW') || input.isKeyDown('ArrowUp')) {
                this.speed = Math.min(this.speed + this.acceleration, this.maxSpeed);
            } else if (input.isKeyDown('KeyS') || input.isKeyDown('ArrowDown')) {
                this.speed = Math.max(this.speed - this.brakePower, -this.maxSpeed * 0.3);
            } else {
                // 自然减速
                if (this.speed > 0) {
                    this.speed = Math.max(0, this.speed - this.friction);
                } else if (this.speed < 0) {
                    this.speed = Math.min(0, this.speed + this.friction);
                }
            }
            
            // 转向
            if (input.isKeyDown('KeyA') || input.isKeyDown('ArrowLeft')) {
                this.steerSpeed = Math.max(this.steerSpeed - this.steerAcceleration, -this.maxSteerSpeed);
            } else if (input.isKeyDown('KeyD') || input.isKeyDown('ArrowRight')) {
                this.steerSpeed = Math.min(this.steerSpeed + this.steerAcceleration, this.maxSteerSpeed);
            } else {
                // 回正
                if (this.steerSpeed > 0) {
                    this.steerSpeed = Math.max(0, this.steerSpeed - this.steerAcceleration * 0.5);
                } else {
                    this.steerSpeed = Math.min(0, this.steerSpeed + this.steerAcceleration * 0.5);
                }
            }
            
            // 更新位置
            this.x += this.steerSpeed * deltaTime * 60;
            this.distance += this.speed * deltaTime * 60;
            
            // 限制在道路范围内
            const roadLeft = (CONFIG.CANVAS_WIDTH - CONFIG.ROAD_WIDTH) / 2 + 30;
            const roadRight = (CONFIG.CANVAS_WIDTH + CONFIG.ROAD_WIDTH) / 2 - 30;
            this.x = MathUtils.clamp(this.x, roadLeft, roadRight);
            
            // 计算倾斜
            this.tilt = this.steerSpeed / this.maxSteerSpeed * 0.15;
        }
        
        render(renderer) {
            renderer.save();
            renderer.translate(this.x, this.y);
            renderer.rotate(this.tilt);
            
            // 赛车主体
            const gradient = renderer.createGradient(-this.width/2, 0, this.width/2, 0, [
                [0, '#1a1a2e'],
                [0.5, '#2d2d4a'],
                [1, '#1a1a2e']
            ]);
            
            renderer.ctx.fillStyle = gradient;
            renderer.ctx.beginPath();
            renderer.ctx.moveTo(0, -this.height/2);
            renderer.ctx.lineTo(this.width/2, -this.height/4);
            renderer.ctx.lineTo(this.width/2, this.height/2);
            renderer.ctx.lineTo(-this.width/2, this.height/2);
            renderer.ctx.lineTo(-this.width/2, -this.height/4);
            renderer.ctx.closePath();
            renderer.ctx.fill();
            
            // 车身线条
            renderer.ctx.strokeStyle = CONFIG.COLORS.neonCyan;
            renderer.ctx.lineWidth = 2;
            renderer.ctx.stroke();
            
            // 驾驶舱
            renderer.drawRect(-10, -15, 20, 25, '#0d0d15', true);
            renderer.ctx.strokeStyle = CONFIG.COLORS.neonPink;
            renderer.ctx.lineWidth = 1;
            renderer.ctx.strokeRect(-10, -15, 20, 25);
            
            // 前灯
            renderer.drawGlowRect(-12, -this.height/2 + 5, 6, 4, CONFIG.COLORS.neonYellow, 8);
            renderer.drawGlowRect(6, -this.height/2 + 5, 6, 4, CONFIG.COLORS.neonYellow, 8);
            
            // 尾灯
            renderer.drawGlowRect(-15, this.height/2 - 8, 10, 4, CONFIG.COLORS.neonPink, 10);
            renderer.drawGlowRect(5, this.height/2 - 8, 10, 4, CONFIG.COLORS.neonPink, 10);
            
            // 引擎盖装饰线
            renderer.drawLine(-8, -this.height/2 + 15, -8, -10, CONFIG.COLORS.neonCyan, 1);
            renderer.drawLine(8, -this.height/2 + 15, 8, -10, CONFIG.COLORS.neonCyan, 1);
            
            renderer.restore();
        }
    }

    // ============================================
    // 道路渲染器
    // ============================================
    class Road {
        constructor() {
            this.offset = 0;
            this.lineSpacing = 80;
            this.lineWidth = 8;
            this.lineHeight = 40;
        }
        
        update(deltaTime, speed) {
            this.offset += speed * deltaTime * 60;
            this.offset %= this.lineSpacing;
        }
        
        render(renderer) {
            const roadLeft = (CONFIG.CANVAS_WIDTH - CONFIG.ROAD_WIDTH) / 2;
            const roadRight = roadLeft + CONFIG.ROAD_WIDTH;
            
            // 道路背景
            const roadGradient = renderer.createGradient(roadLeft, 0, roadRight, 0, [
                [0, '#0d0d15'],
                [0.1, '#1a1a2e'],
                [0.9, '#1a1a2e'],
                [1, '#0d0d15']
            ]);
            renderer.drawRect(roadLeft, 0, CONFIG.ROAD_WIDTH, CONFIG.CANVAS_HEIGHT, roadGradient);
            
            // 道路边缘发光线
            renderer.drawGlowRect(roadLeft, 0, 4, CONFIG.CANVAS_HEIGHT, CONFIG.COLORS.neonCyan, 15);
            renderer.drawGlowRect(roadRight - 4, 0, 4, CONFIG.CANVAS_HEIGHT, CONFIG.COLORS.neonCyan, 15);
            
            // 车道分隔线
            const laneWidth = CONFIG.ROAD_WIDTH / 3;
            for (let i = 1; i < 3; i++) {
                const laneX = roadLeft + i * laneWidth - this.lineWidth / 2;
                
                // 虚线效果
                for (let y = -this.lineSpacing + this.offset; y < CONFIG.CANVAS_HEIGHT; y += this.lineSpacing) {
                    if (y + this.lineHeight > 0 && y < CONFIG.CANVAS_HEIGHT) {
                        renderer.drawGlowRect(laneX, y, this.lineWidth, this.lineHeight, CONFIG.COLORS.neonCyan, 5);
                    }
                }
            }
            
            // 中央分隔线（实线，不同颜色）
            const centerX = CONFIG.CANVAS_WIDTH;
            renderer.drawGlowRect(centerX - 2, 0, 4, CONFIG.CANVAS_HEIGHT, CONFIG.COLORS.neonPink, 8);
        }
    }

    // ============================================
    // 背景星空
    // ============================================
    class StarField {
        constructor() {
            this.stars = [];
            this.generateStars(100);
        }
        
        generateStars(count) {
            for (let i = 0; i < count; i++) {
                this.stars.push({
                    x: Math.random() * CONFIG.CANVAS_WIDTH,
                    y: Math.random() * CONFIG.CANVAS_HEIGHT,
                    size: Math.random() * 2 + 0.5,
                    brightness: Math.random(),
                    twinkleSpeed: Math.random() * 0.05 + 0.01,
                    phase: Math.random() * Math.PI * 2
                });
            }
        }
        
        update(deltaTime, time) {
            this.stars.forEach(star => {
                star.currentBrightness = (Math.sin(time * star.twinkleSpeed + star.phase) + 1) / 2 * star.brightness;
            });
        }
        
        render(renderer) {
            this.stars.forEach(star => {
                const alpha = 0.3 + star.currentBrightness * 0.7;
                renderer.setAlpha(alpha);
                renderer.drawCircle(star.x, star.y, star.size, '#ffffff');
            });
            renderer.setAlpha(1);
        }
    }

    // ============================================
    // UI管理器
    // ============================================
    class UIManager {
        constructor() {
            this.buttons = [];
            this.hoveredButton = null;
        }
        
        createButton(x, y, width, height, text, callback) {
            const button = {
                x, y, width, height, text, callback,
                hovered: false,
                scale: 1,
                targetScale: 1
            };
            this.buttons.push(button);
            return button;
        }
        
        update(mouse) {
            this.buttons.forEach(btn => {
                const inBounds = mouse.x >= btn.x - btn.width/2 &&
                                mouse.x <= btn.x + btn.width/2 &&
                                mouse.y >= btn.y - btn.height/2 &&
                                mouse.y <= btn.y + btn.height/2;
                
                btn.hovered = inBounds;
                btn.targetScale = inBounds ? 1.05 : 1;
                btn.scale = MathUtils.lerp(btn.scale, btn.targetScale, 0.2);
                
                if (inBounds && mouse.clicked) {
                    btn.callback();
                }
            });
        }
        
        render(renderer) {
            this.buttons.forEach(btn => {
                renderer.save();
                renderer.translate(btn.x, btn.y);
                renderer.scale(btn.scale, btn.scale);
                
                // 按钮背景
                const bgColor = btn.hovered ? 'rgba(0, 245, 255, 0.15)' : 'rgba(0, 245, 255, 0.05)';
                renderer.drawRect(-btn.width/2, -btn.height/2, btn.width, btn.height, bgColor);
                
                // 按钮边框
                const borderColor = btn.hovered ? CONFIG.COLORS.neonCyan : 'rgba(0, 245, 255, 0.3)';
                renderer.ctx.strokeStyle = borderColor;
                renderer.ctx.lineWidth = 2;
                renderer.ctx.strokeRect(-btn.width/2, -btn.height/2, btn.width, btn.height);
                
                // 发光效果
                if (btn.hovered) {
                    renderer.ctx.shadowColor = CONFIG.COLORS.neonCyan;
                    renderer.ctx.shadowBlur = 15;
                    renderer.ctx.strokeRect(-btn.width/2, -btn.height/2, btn.width, btn.height);
                    renderer.ctx.shadowBlur = 0;
                }
                
                // 按钮文字
                renderer.drawGlowText(btn.text, 0, 0, {
                    font: '18px Orbitron',
                    color: btn.hovered ? '#ffffff' : CONFIG.COLORS.neonCyan,
                    glowColor: btn.hovered ? CONFIG.COLORS.neonCyan : 'transparent'
                });
                
                renderer.restore();
            });
        }
        
        clear() {
            this.buttons = [];
        }
    }

    // ============================================
    // 游戏状态实现
    // ============================================
    
    // 菜单状态
    class MenuState {
        constructor(game) {
            this.game = game;
            this.titleY = 0;
            this.animationTime = 0;
        }
        
        enter() {
            this.game.ui.clear();
            this.game.ui.createButton(
                CONFIG.CANVAS_WIDTH / 2,
                CONFIG.CANVAS_HEIGHT / 2 + 50,
                200, 50,
                'START RACE',
                () => this.game.stateMachine.changeState('PLAYING')
            );
            
            this.game.ui.createButton(
                CONFIG.CANVAS_WIDTH / 2,
                CONFIG.CANVAS_HEIGHT / 2 + 120,
                200, 50,
                'CONTROLS',
                () => console.log('Controls clicked')
            );
        }
        
        exit() {
            this.game.ui.clear();
        }
        
        update(deltaTime) {
            this.animationTime += deltaTime;
            this.titleY = Math.sin(this.animationTime * 2) * 5;
            this.game.ui.update(this.game.input.mouse);
        }
        
        render(ctx) {
            const renderer = this.game.renderer;
            
            // 背景
            renderer.clear();
            this.game.starField.render(renderer);
            
            // 标题
            renderer.drawGlowText('NEON RACER', CONFIG.CANVAS_WIDTH / 2, 150 + this.titleY, {
                font: '64px Orbitron',
                color: CONFIG.COLORS.neonCyan,
                glowColor: CONFIG.COLORS.neonCyan
            });
            
            // 副标题
            renderer.drawGlowText('Press SPACE or Click to Start', CONFIG.CANVAS_WIDTH / 2, 220, {
                font: '16px Share Tech Mono',
                color: CONFIG.COLORS.neonPink,
                glowColor: CONFIG.COLORS.neonPink
            });
            
            // 装饰线
            const lineY = 260;
            renderer.drawLine(100, lineY, CONFIG.CANVAS_WIDTH - 100, lineY, CONFIG.COLORS.neonCyan, 1);
            
            // 渲染UI
            this.game.ui.render(renderer);
            
            // 版本信息
            renderer.drawText('v1.0.0 - Game Framework Demo', 20, CONFIG.CANVAS_HEIGHT - 30, {
                color: 'rgba(255,255,255,0.3)',
                font: '12px Share Tech Mono'
            });
        }
    }

    // 游戏进行状态
    class PlayingState {
        constructor(game) {
            this.game = game;
            this.score = 0;
            this.highScore = 0;
        }
        
        enter() {
            this.game.player.x = CONFIG.CANVAS_WIDTH / 2;
            this.game.player.y = CONFIG.CANVAS_HEIGHT - 120;
            this.game.player.speed = 0;
            this.game.player.distance = 0;
            this.game.player.steerSpeed = 0;
            this.score = 0;
            this.game.particles.clear();
        }
        
        exit() {
            if (this.score > this.highScore) {
                this.highScore = this.score;
            }
        }
        
        update(deltaTime) {
            const input = this.game.input;
            
            // 更新玩家
            this.game.player.update(deltaTime, input);
            
            // 更新道路
            this.game.road.update(deltaTime, this.game.player.speed);
            
            // 更新星空
            this.game.starField.update(deltaTime, this.game.time);
            
            // 生成粒子（尾气效果）
            if (this.game.player.speed > 2) {
                this.game.particles.emit(
                    this.game.player.x + (Math.random() - 0.5) * 20,
                    this.game.player.y + this.game.player.height / 2,
                    1,
                    {
                        angle: Math.PI / 2 + (Math.random() - 0.5) * 0.3,
                        speed: { min: 1, max: 3 },
                        life: { min: 0.3, max: 0.8 },
                        size: { min: 2, max: 5 },
                        colors: [CONFIG.COLORS.neonOrange, CONFIG.COLORS.neonYellow, '#ff4400'],
                        decay: 0.03,
                        gravity: 0.1
                    }
                );
            }
            
            // 更新粒子
            this.game.particles.update(deltaTime);
            
            // 更新分数
            this.score = Math.floor(this.game.player.distance / 10);
            
            // 暂停检测
            if (input.isKeyJustPressed('Escape')) {
                this.game.stateMachine.changeState('PAUSED');
            }
            
            // 检测边界碰撞（简化版游戏结束）
            const roadLeft = (CONFIG.CANVAS_WIDTH - CONFIG.ROAD_WIDTH) / 2;
            const roadRight = roadLeft + CONFIG.ROAD_WIDTH;
            
            // 可以在这里添加障碍物碰撞检测
        }
        
        render(ctx) {
            const renderer = this.game.renderer;
            
            renderer.clear();
            
            // 渲染星空背景
            this.game.starField.render(renderer);
            
            // 渲染道路
            this.game.road.render(renderer);
            
            // 渲染粒子
            this.game.particles.render(ctx, renderer);
            
            // 渲染玩家
            this.game.player.render(renderer);
            
            // 渲染HUD
            this.renderHUD(renderer);
        }
        
        renderHUD(renderer) {
            // 速度表
            const speedPercent = this.game.player.speed / this.game.player.maxSpeed;
            const barWidth = 200;
            const barHeight = 20;
            const barX = 30;
            const barY = 30;
            
            // 速度条背景
            renderer.drawRect(barX, barY, barWidth, barHeight, 'rgba(0,0,0,0.5)');
            renderer.ctx.strokeStyle = 'rgba(255,255,255,0.3)';
            renderer.ctx.lineWidth = 1;
            renderer.ctx.strokeRect(barX, barY, barWidth, barHeight);
            
            // 速度条填充
            const fillWidth = barWidth * speedPercent;
            const speedColor = speedPercent > 0.8 ? CONFIG.COLORS.neonPink :
                              speedPercent > 0.5 ? CONFIG.COLORS.neonYellow :
                              CONFIG.COLORS.neonGreen;
            
            if (fillWidth > 0) {
                renderer.drawGlowRect(barX, barY, fillWidth, barHeight, speedColor, 10);
            }
            
            // 速度标签
            renderer.drawText('SPEED', barX, barY - 18, {
                font: '12px Orbitron',
                color: CONFIG.COLORS.neonCyan
            });
            
            // 速度数值
            const kmh = Math.floor(this.game.player.speed * 20);
            renderer.drawGlowText(kmh + ' km/h', barX + barWidth + 15, barY + barHeight/2, {
                font: '16px Orbitron',
                color: speedColor,
                glowColor: speedColor,
                align: 'left',
                baseline: 'middle'
            });
            
            // 分数
            renderer.drawGlowText('SCORE: ' + this.score, CONFIG.CANVAS_WIDTH - 30, 30, {
                font: '24px Orbitron',
                color: CONFIG.COLORS.neonYellow,
                glowColor: CONFIG.COLORS.neonYellow,
                align: 'right'
            });
            
            // 距离
            const distance = Math.floor(this.game.player.distance);
            renderer.drawText('Distance: ' + distance + 'm', CONFIG.CANVAS_WIDTH - 30, 60, {
                font: '14px Share Tech Mono',
                color: 'rgba(255,255,255,0.7)',
                align: 'right'
            });
        }
    }

    // 暂停状态
    class PausedState {
        constructor(game) {
            this.game = game;
            this.overlayAlpha = 0;
        }
        
        enter() {
            this.overlayAlpha = 0;
            this.game.ui.clear();
            
            this.game.ui.createButton(
                CONFIG.CANVAS_WIDTH / 2,
                CONFIG.CANVAS_HEIGHT / 2,
                200, 50,
                'RESUME',
                () => this.game.stateMachine.changeState('PLAYING')
            );
            
            this.game.ui.createButton(
                CONFIG.CANVAS_WIDTH / 2,
                CONFIG.CANVAS_HEIGHT / 2 + 70,
                200, 50,
                'MAIN MENU',
                () => this.game.stateMachine.changeState('MENU')
            );
        }
        
        exit() {
            this.game.ui.clear();
        }
        
        update(deltaTime) {
            this.overlayAlpha = Math.min(this.overlayAlpha + deltaTime * 3, 0.7);
            this.game.ui.update(this.game.input.mouse);
            
            if (this.game.input.isKeyJustPressed('Escape') || 
                this.game.input.isKeyJustPressed('Space')) {
                this.game.stateMachine.changeState('PLAYING');
            }
        }
        
        render(ctx) {
            const renderer = this.game.renderer;
            
            // 渲染当前游戏画面（暂停前的状态）
            // 这里简化处理，重新渲染道路和玩家
            renderer.clear();
            this.game.starField.render(renderer);
            this.game.road.render(renderer);
            this.game.player.render(renderer);
            
            // 半透明遮罩
            renderer.setAlpha(this.overlayAlpha);
            renderer.drawRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT, '#000000');
            renderer.setAlpha(1);
            
            // 暂停文字
            renderer.drawGlowText('PAUSED', CONFIG.CANVAS_WIDTH / 2, CONFIG.CANVAS_HEIGHT / 2 - 100, {
                font: '48px Orbitron',
                color: CONFIG.COLORS.neonYellow,
                glowColor: CONFIG.COLORS.neonYellow
            });
            
            // 渲染UI按钮
            this.game.ui.render(renderer);
        }
    }

    // 游戏结束状态
    class GameOverState {
        constructor(game) {
            this.game = game;
            this.finalScore = 0;
        }
        
        enter() {
            this.finalScore = Math.floor(this.game.player.distance / 10);
            this.game.ui.clear();
            
            this.game.ui.createButton(
                CONFIG.CANVAS_WIDTH / 2,
                CONFIG.CANVAS_HEIGHT / 2 + 80,
                200, 50,
                'RETRY',
                () => this.game.stateMachine.changeState('PLAYING')
            );
            
            this.game.ui.createButton(
                CONFIG.CANVAS_WIDTH / 2,
                CONFIG.CANVAS_HEIGHT / 2 + 150,
                200, 50,
                'MAIN MENU',
                () => this.game.stateMachine.changeState('MENU')
            );
        }
        
        exit() {
            this.game.ui.clear();
        }
        
        update(deltaTime) {
            this.game.starField.update(deltaTime, this.game.time);
            this.game.ui.update(this.game.input.mouse);
        }
        
        render(ctx) {
            const renderer = this.game.renderer;
            
            renderer.clear();
            this.game.starField.render(renderer);
            
            // 游戏结束标题
            renderer.drawGlowText('GAME OVER', CONFIG.CANVAS_WIDTH / 2, 150, {
                font: '56px Orbitron',
                color: CONFIG.COLORS.neonPink,
                glowColor: CONFIG.COLORS.neonPink
            });
            
            // 最终分数
            renderer.drawText('Final Score', CONFIG.CANVAS_WIDTH / 2, 250, {
                font: '18px Share Tech Mono',
                color: 'rgba(255,255,255,0.7)',
                align: 'center'
            });
            
            renderer.drawGlowText(this.finalScore.toString(), CONFIG.CANVAS_WIDTH / 2, 300, {
                font: '72px Orbitron',
                color: CONFIG.COLORS.neonYellow,
                glowColor: CONFIG.COLORS.neonYellow
            });
            
            // 渲染UI
            this.game.ui.render(renderer);
        }
    }

    // ============================================
    // 主游戏类
    // ============================================
    class Game {
        constructor() {
            this.canvas = document.getElementById('gameCanvas');
            this.renderer = new Renderer(this.canvas);
            this.input = new InputManager();
            this.resourceLoader = new ResourceLoader();
            this.performanceMonitor = new PerformanceMonitor();
            this.stateMachine = new GameStateMachine(this);
            this.ui = new UIManager();
            this.particles = new ParticleSystem();
            
            // 游戏对象
            this.player = new PlayerCar(CONFIG.CANVAS_WIDTH / 2, CONFIG.CANVAS_HEIGHT - 120);
            this.road = new Road();
            this.starField = new StarField();
            
            // 时间管理
            this.lastFrameTime = 0;
            this.time = 0;
            this.deltaTime = 0;
            this.isRunning = false;
            
            // 帧率控制
            this.targetFrameTime = 1000 / CONFIG.TARGET_FPS;
            this.accumulatedTime = 0;
            
            // 注册状态
            this.registerStates();
            
            // 初始化
            this.init();
        }
        
        registerStates() {
            this.stateMachine.registerState('MENU', new MenuState(this));
            this.stateMachine.registerState('PLAYING', new PlayingState(this));
            this.stateMachine.registerState('PAUSED', new PausedState(this));
            this.stateMachine.registerState('GAMEOVER', new GameOverState(this));
        }
        
        async init() {
            const loadingBar = document.getElementById('loadingBar');
            const loadingStatus = document.getElementById('loadingStatus');
            const loadingScreen = document.getElementById('loadingScreen');
            
            // 模拟资源加载
            const resources = [
                { name: 'placeholder1', src: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' },
                { name: 'placeholder2', src: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' }
            ];
            
            loadingStatus.textContent = 'Loading resources...';
            await this.resourceLoader.loadImages(resources);
            loadingBar.style.width = '50%';
            
            loadingStatus.textContent = 'Initializing game systems...';
            await this.delay(300);
            loadingBar.style.width = '75%';
            
            loadingStatus.textContent = 'Starting game...';
            await this.delay(200);
            loadingBar.style.width = '100%';
            
            await this.delay(500);
            loadingScreen.classList.add('hidden');
            
            // 开始游戏
            this.stateMachine.changeState('MENU');
            this.start();
        }
        
        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        
        start() {
            this.isRunning = true;
            this.lastFrameTime = performance.now();
            this.gameLoop();
        }
        
        gameLoop() {
            if (!this.isRunning) return;
            
            const now = performance.now();
            const elapsed = now - this.lastFrameTime;
            this.lastFrameTime = now;
            
            // 计算deltaTime（秒）
            this.deltaTime = Math.min(elapsed / 1000, 0.1); // 限制最大deltaTime
            this.time += this.deltaTime;
            
            // 性能监控开始
            this.performanceMonitor.beginFrame();
            
            // 更新
            this.stateMachine.update(this.deltaTime);
            
            // 清除单帧输入
            this.input.clearJustPressed();
            
            // 渲染
            this.stateMachine.render(this.renderer.ctx);
            
            // 更新性能监控中的对象计数
            this.performanceMonitor.addObject(this.particles.particles.length + 1);
            
            // 性能监控结束
            this.performanceMonitor.endFrame();
            
            // 下一帧
            requestAnimationFrame(() => this.gameLoop());
        }
        
        stop() {
            this.isRunning = false;
        }
    }

    // ============================================
    // 初始化
    // ============================================
    let game = null;
    
    window.addEventListener('DOMContentLoaded', () => {
        game = new Game();
    });
    </script>
</body>
</html>
```

## 框架架构说明

### 核心模块

1. **Game（主游戏类）**
   - 管理所有子系统
   - 控制游戏循环
   - 协调状态机切换

2. **GameStateMachine（状态机）**
   - 四个状态：MENU、PLAYING、PAUSED、GAMEOVER
   - 每个状态有独立的 enter/exit/update/render 方法

3. **Renderer（渲染引擎）**
   - 封装 Canvas 2D API
   - 提供高级渲染方法（发光文字、渐变、粒子等）
   - 支持变换矩阵操作

4. **ResourceLoader（资源加载器）**
   - 异步图片加载
   - 进度跟踪
   - 可扩展支持音频等资源

5. **PerformanceMonitor（性能监控）**
   - FPS 实时监控
   - 帧时间统计
   - 绘制调用计数
   - 状态显示

6. **InputManager（输入管理）**
   - 键盘状态追踪
   - 鼠标位置和点击
   - 单次按键检测

7. **ParticleSystem（粒子系统）**
   - 可配置的粒子发射器
   - 支持颜色、速度、生命周期等参数
   - 自动回收失效粒子

### 游戏对象

- **PlayerCar**：玩家控制的赛车，包含物理模拟（加速度、摩擦力、转向）
- **Road**：无限滚动的道路，带有发光车道线
- **StarField**：动态星空背景

### 操作说明

| 按键 | 功能 |
|------|------|
| W / ↑ | 加速 |
| S / ↓ | 刹车 |
| A / ← | 左转 |
| D / → | 右转 |
| ESC | 暂停 |
| SPACE | 开始/继续 |

打开 HTML 文件即可运行，游戏会显示加载画面后进入主菜单。点击 START RACE 或按空格键开始游戏。