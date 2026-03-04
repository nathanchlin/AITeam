# 游戏基础架构与Canvas渲染系统

**Time**: 2026-03-01T18:07:28.199453

---

这是一个愤怒的小鸟游戏基础架构，我会创建一个完整的、可运行的单文件HTML，包含Canvas渲染系统、游戏循环、场景管理、视差背景、地面渲染和相机系统。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Angry Birds - Game Framework</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent: #e94560;
            --accent-glow: rgba(233, 69, 96, 0.4);
            --text: #eaeaea;
            --text-muted: #8892a0;
        }

        body {
            background: var(--bg-dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', system-ui, sans-serif;
            overflow: hidden;
        }

        .game-container {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 
                0 0 60px rgba(233, 69, 96, 0.2),
                0 20px 60px rgba(0, 0, 0, 0.5);
        }

        canvas {
            display: block;
            cursor: crosshair;
        }

        .game-ui {
            position: absolute;
            top: 16px;
            left: 16px;
            right: 16px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            pointer-events: none;
            z-index: 10;
        }

        .ui-panel {
            background: rgba(22, 33, 62, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(233, 69, 96, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            color: var(--text);
        }

        .ui-panel h3 {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .ui-panel .value {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent);
        }

        .controls-hint {
            position: absolute;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(22, 33, 62, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px 20px;
            color: var(--text-muted);
            font-size: 13px;
            pointer-events: none;
            display: flex;
            gap: 24px;
        }

        .controls-hint kbd {
            background: rgba(233, 69, 96, 0.2);
            color: var(--accent);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: inherit;
            font-weight: 600;
        }

        .debug-panel {
            position: absolute;
            top: 16px;
            right: 16px;
            background: rgba(0, 0, 0, 0.7);
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            padding: 8px 12px;
            border-radius: 4px;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas"></canvas>
        <div class="game-ui">
            <div class="ui-panel">
                <h3>Score</h3>
                <div class="value" id="scoreDisplay">0</div>
            </div>
            <div class="ui-panel">
                <h3>Birds Left</h3>
                <div class="value" id="birdsDisplay">3</div>
            </div>
        </div>
        <div class="controls-hint">
            <span><kbd>A</kbd><kbd>D</kbd> Move Camera</span>
            <span><kbd>W</kbd><kbd>S</kbd> Zoom</span>
            <span><kbd>Space</kbd> Launch Bird</span>
            <span><kbd>R</kbd> Reset</span>
        </div>
        <div class="debug-panel" id="debugPanel"></div>
    </div>

    <script>
    // ============================================
    // 游戏配置常量
    // ============================================
    const CONFIG = {
        CANVAS_WIDTH: 1200,
        CANVAS_HEIGHT: 700,
        GROUND_HEIGHT: 120,
        GRAVITY: 0.5,
        TARGET_FPS: 60,
        WORLD_WIDTH: 2400,
        CAMERA_LERP: 0.08,
        MIN_ZOOM: 0.5,
        MAX_ZOOM: 2.0
    };

    // ============================================
    // 工具函数
    // ============================================
    const Utils = {
        lerp: (a, b, t) => a + (b - a) * t,
        clamp: (val, min, max) => Math.max(min, Math.min(max, val)),
        randomRange: (min, max) => Math.random() * (max - min) + min,
        randomInt: (min, max) => Math.floor(Utils.randomRange(min, max + 1)),
        distance: (x1, y1, x2, y2) => Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2),
        
        // 安全的颜色格式化
        safeColor: (r, g, b, a = 1) => {
            r = Utils.clamp(Math.round(r), 0, 255);
            g = Utils.clamp(Math.round(g), 0, 255);
            b = Utils.clamp(Math.round(b), 0, 255);
            a = Utils.clamp(a, 0, 1);
            return `rgba(${r},${g},${b},${a})`;
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

        add(v) {
            return new Vector2(this.x + v.x, this.y + v.y);
        }

        sub(v) {
            return new Vector2(this.x - v.x, this.y - v.y);
        }

        mul(s) {
            return new Vector2(this.x * s, this.y * s);
        }

        length() {
            return Math.sqrt(this.x * this.x + this.y * this.y);
        }

        normalize() {
            const len = this.length();
            if (len === 0) return new Vector2(0, 0);
            return new Vector2(this.x / len, this.y / len);
        }

        clone() {
            return new Vector2(this.x, this.y);
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
                isDown: false,
                isDragging: false
            };
            this.dragStart = null;

            this.bindEvents();
        }

        bindEvents() {
            window.addEventListener('keydown', (e) => {
                this.keys[e.code] = true;
                if (e.code === 'Space') e.preventDefault();
            });

            window.addEventListener('keyup', (e) => {
                this.keys[e.code] = false;
            });

            this.canvas.addEventListener('mousedown', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = e.clientX - rect.left;
                this.mouse.y = e.clientY - rect.top;
                this.mouse.isDown = true;
                this.dragStart = { x: this.mouse.x, y: this.mouse.y };
            });

            this.canvas.addEventListener('mouseup', () => {
                this.mouse.isDown = false;
                this.mouse.isDragging = false;
                this.dragStart = null;
            });

            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = e.clientX - rect.left;
                this.mouse.y = e.clientY - rect.top;

                if (this.mouse.isDown && this.dragStart) {
                    const dx = this.mouse.x - this.dragStart.x;
                    const dy = this.mouse.y - this.dragStart.y;
                    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                        this.mouse.isDragging = true;
                    }
                }
            });
        }

        isKeyPressed(code) {
            return this.keys[code] === true;
        }

        updateWorldPosition(camera) {
            this.mouse.worldX = (this.mouse.x - CONFIG.CANVAS_WIDTH / 2) / camera.zoom + camera.x;
            this.mouse.worldY = (this.mouse.y - CONFIG.CANVAS_HEIGHT / 2) / camera.zoom + camera.y;
        }
    }

    // ============================================
    // 相机系统
    // ============================================
    class Camera {
        constructor() {
            this.position = new Vector2(CONFIG.CANVAS_WIDTH / 2, 0);
            this.target = new Vector2(CONFIG.CANVAS_WIDTH / 2, 0);
            this.zoom = 1.0;
            this.targetZoom = 1.0;
            this.minX = 0;
            this.maxX = CONFIG.WORLD_WIDTH;
        }

        follow(targetX, targetY, immediate = false) {
            this.target.x = Utils.clamp(targetX, this.minX + CONFIG.CANVAS_WIDTH / 2 / this.zoom, 
                                        this.maxX - CONFIG.CANVAS_WIDTH / 2 / this.zoom);
            this.target.y = targetY;

            if (immediate) {
                this.position.x = this.target.x;
                this.position.y = this.target.y;
            }
        }

        setZoom(zoom) {
            this.targetZoom = Utils.clamp(zoom, CONFIG.MIN_ZOOM, CONFIG.MAX_ZOOM);
        }

        update(deltaTime) {
            // 平滑跟随
            this.position.x = Utils.lerp(this.position.x, this.target.x, CONFIG.CAMERA_LERP);
            this.position.y = Utils.lerp(this.position.y, this.target.y, CONFIG.CAMERA_LERP);
            this.zoom = Utils.lerp(this.zoom, this.targetZoom, 0.05);
        }

        worldToScreen(worldX, worldY) {
            return {
                x: (worldX - this.position.x) * this.zoom + CONFIG.CANVAS_WIDTH / 2,
                y: (worldY - this.position.y) * this.zoom + CONFIG.CANVAS_HEIGHT / 2
            };
        }

        screenToWorld(screenX, screenY) {
            return {
                x: (screenX - CONFIG.CANVAS_WIDTH / 2) / this.zoom + this.position.x,
                y: (screenY - CONFIG.CANVAS_HEIGHT / 2) / this.zoom + this.position.y
            };
        }
    }

    // ============================================
    // 云层类（视差背景）
    // ============================================
    class Cloud {
        constructor(layer, worldWidth) {
            this.layer = layer;
            this.worldWidth = worldWidth;
            this.reset(true);
        }

        reset(initial = false) {
            this.x = initial ? Utils.randomRange(0, this.worldWidth) : -this.width;
            this.y = Utils.randomRange(30, 200);
            this.width = Utils.randomRange(80, 200);
            this.height = Utils.randomRange(30, 60);
            this.speed = Utils.randomRange(0.1, 0.3) * (1 + this.layer * 0.5);
            this.opacity = Utils.randomRange(0.3, 0.7) * (1 - this.layer * 0.2);
            
            // 云朵形状数据
            this.puffs = [];
            const puffCount = Utils.randomInt(3, 5);
            for (let i = 0; i < puffCount; i++) {
                this.puffs.push({
                    offsetX: Utils.randomRange(-this.width * 0.3, this.width * 0.3),
                    offsetY: Utils.randomRange(-this.height * 0.2, this.height * 0.2),
                    radius: Utils.randomRange(this.height * 0.4, this.height * 0.7)
                });
            }
        }

        update(deltaTime) {
            this.x += this.speed;
            if (this.x > this.worldWidth + this.width) {
                this.reset();
            }
        }

        draw(ctx, camera) {
            // 视差效果：不同层有不同的滚动速度
            const parallaxFactor = 0.1 + this.layer * 0.15;
            const screenX = (this.x - camera.position.x * parallaxFactor) % (CONFIG.CANVAS_WIDTH + this.width * 2);
            const adjustedX = screenX < -this.width ? screenX + CONFIG.CANVAS_WIDTH + this.width * 2 : screenX;
            
            const screenY = this.y;

            ctx.save();
            ctx.globalAlpha = this.opacity;

            // 绘制云朵
            this.puffs.forEach(puff => {
                const gradient = ctx.createRadialGradient(
                    adjustedX + puff.offsetX, screenY + puff.offsetY, 0,
                    adjustedX + puff.offsetX, screenY + puff.offsetY, Math.max(1, puff.radius)
                );
                gradient.addColorStop(0, 'rgba(255,255,255,0.9)');
                gradient.addColorStop(0.5, 'rgba(255,255,255,0.6)');
                gradient.addColorStop(1, 'rgba(255,255,255,0)');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(adjustedX + puff.offsetX, screenY + puff.offsetY, Math.max(1, puff.radius), 0, Math.PI * 2);
                ctx.fill();
            });

            ctx.restore();
        }
    }

    // ============================================
    // 背景渲染器
    // ============================================
    class BackgroundRenderer {
        constructor(worldWidth) {
            this.worldWidth = worldWidth;
            this.clouds = [];
            this.stars = [];
            
            // 创建多层云层
            for (let layer = 0; layer < 3; layer++) {
                const cloudCount = 4 - layer;
                for (let i = 0; i < cloudCount; i++) {
                    this.clouds.push(new Cloud(layer, worldWidth));
                }
            }

            // 创建星星
            for (let i = 0; i < 50; i++) {
                this.stars.push({
                    x: Utils.randomRange(0, CONFIG.CANVAS_WIDTH),
                    y: Utils.randomRange(10, 150),
                    size: Utils.randomRange(1, 3),
                    twinkle: Utils.randomRange(0, Math.PI * 2),
                    speed: Utils.randomRange(1, 3)
                });
            }
        }

        update(deltaTime) {
            this.clouds.forEach(cloud => cloud.update(deltaTime));
            
            // 更新星星闪烁
            this.stars.forEach(star => {
                star.twinkle += star.speed * deltaTime * 0.1;
            });
        }

        draw(ctx, camera) {
            // 绘制天空渐变
            const skyGradient = ctx.createLinearGradient(0, 0, 0, CONFIG.CANVAS_HEIGHT);
            skyGradient.addColorStop(0, '#0f0c29');
            skyGradient.addColorStop(0.3, '#302b63');
            skyGradient.addColorStop(0.7, '#24243e');
            skyGradient.addColorStop(1, '#1a1a2e');
            
            ctx.fillStyle = skyGradient;
            ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

            // 绘制星星
            this.stars.forEach(star => {
                const alpha = 0.3 + Math.sin(star.twinkle) * 0.3;
                ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
                ctx.fill();
            });

            // 绘制远山（视差）
            this.drawMountains(ctx, camera);

            // 绘制云层
            this.clouds.forEach(cloud => cloud.draw(ctx, camera));
        }

        drawMountains(ctx, camera) {
            const layers = [
                { color: '#1a1a3a', heightFactor: 0.4, parallax: 0.05, yOffset: 0 },
                { color: '#252545', heightFactor: 0.3, parallax: 0.1, yOffset: 50 },
                { color: '#2d2d55', heightFactor: 0.2, parallax: 0.15, yOffset: 80 }
            ];

            layers.forEach(layer => {
                ctx.fillStyle = layer.color;
                ctx.beginPath();
                
                const baseY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT - layer.yOffset;
                const mountainOffset = -camera.position.x * layer.parallax;

                ctx.moveTo(0, CONFIG.CANVAS_HEIGHT);
                
                for (let x = 0; x <= CONFIG.CANVAS_WIDTH + 50; x += 50) {
                    const worldX = x + mountainOffset;
                    const noise = Math.sin(worldX * 0.005) * 50 + 
                                  Math.sin(worldX * 0.01) * 30 + 
                                  Math.sin(worldX * 0.02) * 15;
                    const y = baseY - Math.abs(noise) * layer.heightFactor;
                    ctx.lineTo(x, y);
                }

                ctx.lineTo(CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
                ctx.closePath();
                ctx.fill();
            });
        }
    }

    // ============================================
    // 地面渲染器
    // ============================================
    class GroundRenderer {
        constructor(worldWidth) {
            this.worldWidth = worldWidth;
            this.grassBlades = [];
            this.rocks = [];
            this.flowers = [];

            this.generateDetails();
        }

        generateDetails() {
            // 生成草
            for (let x = 0; x < this.worldWidth; x += 15) {
                const count = Utils.randomInt(1, 3);
                for (let i = 0; i < count; i++) {
                    this.grassBlades.push({
                        x: x + Utils.randomRange(-5, 5),
                        height: Utils.randomRange(8, 20),
                        sway: Utils.randomRange(0, Math.PI * 2),
                        swaySpeed: Utils.randomRange(1, 3),
                        color: Utils.randomInt(0, 1) === 0 ? '#2d5a27' : '#3d7a37'
                    });
                }
            }

            // 生成岩石
            for (let i = 0; i < 15; i++) {
                this.rocks.push({
                    x: Utils.randomRange(100, this.worldWidth - 100),
                    width: Utils.randomRange(20, 50),
                    height: Utils.randomRange(15, 35),
                    color: Utils.randomInt(0, 1) === 0 ? '#4a4a5a' : '#5a5a6a'
                });
            }

            // 生成花朵
            for (let i = 0; i < 30; i++) {
                this.flowers.push({
                    x: Utils.randomRange(50, this.worldWidth - 50),
                    type: Utils.randomInt(0, 2),
                    size: Utils.randomRange(5, 10)
                });
            }
        }

        update(deltaTime, time) {
            // 更新草的摇摆
            this.grassBlades.forEach(blade => {
                blade.sway += blade.swaySpeed * deltaTime * 0.05;
            });
        }

        draw(ctx, camera) {
            const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT;

            // 绘制主地面
            this.drawMainGround(ctx, camera, groundY);

            // 绘制草地纹理
            this.drawGrassTexture(ctx, camera, groundY);

            // 绘制岩石
            this.drawRocks(ctx, camera, groundY);

            // 绘制草
            this.drawGrass(ctx, camera, groundY);

            // 绘制花朵
            this.drawFlowers(ctx, camera, groundY);
        }

        drawMainGround(ctx, camera, groundY) {
            // 地面渐变
            const groundGradient = ctx.createLinearGradient(0, groundY, 0, CONFIG.CANVAS_HEIGHT);
            groundGradient.addColorStop(0, '#4a7c39');
            groundGradient.addColorStop(0.1, '#3d6b2e');
            groundGradient.addColorStop(0.5, '#2d5020');
            groundGradient.addColorStop(1, '#1a3010');

            ctx.fillStyle = groundGradient;
            ctx.fillRect(0, groundY, CONFIG.CANVAS_WIDTH, CONFIG.GROUND_HEIGHT);

            // 地面顶层线条
            ctx.strokeStyle = '#5a9c49';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            ctx.lineTo(CONFIG.CANVAS_WIDTH, groundY);
            ctx.stroke();
        }

        drawGrassTexture(ctx, camera, groundY) {
            ctx.save();
            
            // 绘制泥土层纹理
            const offsetX = -camera.position.x * camera.zoom % 30;
            ctx.strokeStyle = 'rgba(30, 50, 20, 0.3)';
            ctx.lineWidth = 1;
            
            for (let x = offsetX; x < CONFIG.CANVAS_WIDTH + 30; x += 30) {
                for (let y = groundY + 20; y < CONFIG.CANVAS_HEIGHT; y += 20) {
                    ctx.beginPath();
                    ctx.arc(x, y, 2, 0, Math.PI * 2);
                    ctx.stroke();
                }
            }
            
            ctx.restore();
        }

        drawRocks(ctx, camera, groundY) {
            this.rocks.forEach(rock => {
                const screenPos = camera.worldToScreen(rock.x, groundY);
                
                // 只绘制可见的岩石
                if (screenPos.x < -rock.width || screenPos.x > CONFIG.CANVAS_WIDTH + rock.width) return;

                ctx.fillStyle = rock.color;
                ctx.beginPath();
                
                // 岩石形状
                ctx.moveTo(screenPos.x - rock.width / 2, screenPos.y);
                ctx.quadraticCurveTo(screenPos.x - rock.width / 2, screenPos.y - rock.height * 0.7,
                                     screenPos.x, screenPos.y - rock.height);
                ctx.quadraticCurveTo(screenPos.x + rock.width / 2, screenPos.y - rock.height * 0.7,
                                     screenPos.x + rock.width / 2, screenPos.y);
                ctx.closePath();
                ctx.fill();

                // 岩石高光
                ctx.fillStyle = 'rgba(255,255,255,0.1)';
                ctx.beginPath();
                ctx.arc(screenPos.x - rock.width * 0.15, screenPos.y - rock.height * 0.5, 
                        rock.width * 0.2, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        drawGrass(ctx, camera, groundY) {
            ctx.save();
            
            this.grassBlades.forEach(blade => {
                const screenPos = camera.worldToScreen(blade.x, groundY);
                
                if (screenPos.x < -20 || screenPos.x > CONFIG.CANVAS_WIDTH + 20) return;

                const sway = Math.sin(blade.sway) * 3;

                ctx.strokeStyle = blade.color;
                ctx.lineWidth = 2;
                ctx.lineCap = 'round';
                
                ctx.beginPath();
                ctx.moveTo(screenPos.x, screenPos.y);
                ctx.quadraticCurveTo(screenPos.x + sway, screenPos.y - blade.height * 0.6,
                                     screenPos.x + sway * 1.5, screenPos.y - blade.height);
                ctx.stroke();
            });
            
            ctx.restore();
        }

        drawFlowers(ctx, camera, groundY) {
            const flowerColors = ['#ff6b6b', '#ffd93d', '#ffffff'];
            
            this.flowers.forEach(flower => {
                const screenPos = camera.worldToScreen(flower.x, groundY);
                
                if (screenPos.x < -20 || screenPos.x > CONFIG.CANVAS_WIDTH + 20) return;

                const y = screenPos.y - 5;

                // 茎
                ctx.strokeStyle = '#2d5a27';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(screenPos.x, y);
                ctx.lineTo(screenPos.x, y - flower.size * 2);
                ctx.stroke();

                // 花瓣
                ctx.fillStyle = flowerColors[flower.type];
                const petalY = y - flower.size * 2;
                for (let i = 0; i < 5; i++) {
                    const angle = (i / 5) * Math.PI * 2;
                    ctx.beginPath();
                    ctx.ellipse(
                        screenPos.x + Math.cos(angle) * flower.size * 0.5,
                        petalY + Math.sin(angle) * flower.size * 0.5,
                        flower.size * 0.4,
                        flower.size * 0.25,
                        angle,
                        0,
                        Math.PI * 2
                    );
                    ctx.fill();
                }

                // 花心
                ctx.fillStyle = '#ffd93d';
                ctx.beginPath();
                ctx.arc(screenPos.x, petalY, flower.size * 0.25, 0, Math.PI * 2);
                ctx.fill();
            });
        }
    }

    // ============================================
    // 游戏对象基类
    // ============================================
    class GameObject {
        constructor(x, y) {
            this.position = new Vector2(x, y);
            this.velocity = new Vector2(0, 0);
            this.isActive = true;
            this.id = Math.random().toString(36).substr(2, 9);
        }

        update(deltaTime) {
            // 由子类实现
        }

        draw(ctx, camera) {
            // 由子类实现
        }

        getScreenPosition(camera) {
            return camera.worldToScreen(this.position.x, this.position.y);
        }
    }

    // ============================================
    // 小鸟类
    // ============================================
    class Bird extends GameObject {
        constructor(x, y, type = 'red') {
            super(x, y);
            this.type = type;
            this.radius = 20;
            this.isLaunched = false;
            this.rotation = 0;
            this.rotationSpeed = 0;
            this.trail = [];
            this.maxTrailLength = 20;

            // 根据类型设置属性
            this.setupType();
        }

        setupType() {
            switch (this.type) {
                case 'red':
                    this.color = '#e94560';
                    this.secondaryColor = '#c73e54';
                    break;
                case 'yellow':
                    this.color = '#ffd93d';
                    this.secondaryColor = '#e5c235';
                    break;
                case 'blue':
                    this.color = '#4dabf7';
                    this.secondaryColor = '#339af7';
                    break;
                default:
                    this.color = '#e94560';
                    this.secondaryColor = '#c73e54';
            }
        }

        launch(velocity) {
            this.velocity = velocity;
            this.isLaunched = true;
            this.rotationSpeed = velocity.x * 0.02;
        }

        update(deltaTime) {
            if (!this.isLaunched) return;

            // 应用重力
            this.velocity.y += CONFIG.GRAVITY;

            // 更新位置
            this.position.x += this.velocity.x;
            this.position.y += this.velocity.y;

            // 旋转
            this.rotation += this.rotationSpeed;

            // 添加轨迹点
            this.trail.push({
                x: this.position.x,
                y: this.position.y,
                alpha: 1
            });

            // 限制轨迹长度
            if (this.trail.length > this.maxTrailLength) {
                this.trail.shift();
            }

            // 衰减轨迹透明度
            this.trail.forEach((point, i) => {
                point.alpha = (i + 1) / this.trail.length;
            });

            // 地面碰撞
            const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT - this.radius;
            if (this.position.y > groundY) {
                this.position.y = groundY;
                this.velocity.y *= -0.5;
                this.velocity.x *= 0.8;
                this.rotationSpeed *= 0.8;

                if (Math.abs(this.velocity.y) < 1) {
                    this.velocity.y = 0;
                }
            }

            // 边界检查
            if (this.position.x < this.radius) {
                this.position.x = this.radius;
                this.velocity.x *= -0.5;
            }
            if (this.position.x > CONFIG.WORLD_WIDTH - this.radius) {
                this.position.x = CONFIG.WORLD_WIDTH - this.radius;
                this.velocity.x *= -0.5;
            }
        }

        draw(ctx, camera) {
            const screen = this.getScreenPosition(camera);
            const scaledRadius = this.radius * camera.zoom;

            // 绘制轨迹
            if (this.isLaunched && this.trail.length > 1) {
                ctx.beginPath();
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 3 * camera.zoom;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                const trailScreen = this.trail.map(p => camera.worldToScreen(p.x, p.y));
                ctx.moveTo(trailScreen[0].x, trailScreen[0].y);

                for (let i = 1; i < trailScreen.length; i++) {
                    ctx.globalAlpha = this.trail[i].alpha * 0.5;
                    ctx.lineTo(trailScreen[i].x, trailScreen[i].y);
                }
                ctx.stroke();
                ctx.globalAlpha = 1;
            }

            ctx.save();
            ctx.translate(screen.x, screen.y);
            ctx.rotate(this.rotation);

            // 身体阴影
            ctx.fillStyle = 'rgba(0,0,0,0.2)';
            ctx.beginPath();
            ctx.ellipse(scaledRadius * 0.1, scaledRadius * 0.1, scaledRadius, scaledRadius * 0.9, 0, 0, Math.PI * 2);
            ctx.fill();

            // 身体渐变
            const bodyGradient = ctx.createRadialGradient(
                -scaledRadius * 0.3, -scaledRadius * 0.3, 0,
                0, 0, scaledRadius
            );
            bodyGradient.addColorStop(0, this.color);
            bodyGradient.addColorStop(0.7, this.color);
            bodyGradient.addColorStop(1, this.secondaryColor);

            ctx.fillStyle = bodyGradient;
            ctx.beginPath();
            ctx.arc(0, 0, scaledRadius, 0, Math.PI * 2);
            ctx.fill();

            // 眼睛
            this.drawEyes(ctx, scaledRadius);

            // 眉毛
            this.drawEyebrows(ctx, scaledRadius);

            // 喙
            this.drawBeak(ctx, scaledRadius);

            // 尾巴羽毛
            this.drawTail(ctx, scaledRadius);

            ctx.restore();
        }

        drawEyes(ctx, radius) {
            const eyeOffsetX = radius * 0.35;
            const eyeOffsetY = -radius * 0.1;
            const eyeSize = radius * 0.28;

            // 眼白
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.ellipse(-eyeOffsetX, eyeOffsetY, eyeSize, eyeSize * 1.2, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(eyeOffsetX, eyeOffsetY, eyeSize, eyeSize * 1.2, 0, 0, Math.PI * 2);
            ctx.fill();

            // 瞳孔
            ctx.fillStyle = '#1a1a1a';
            ctx.beginPath();
            ctx.arc(-eyeOffsetX + eyeSize * 0.15, eyeOffsetY, eyeSize * 0.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeOffsetX + eyeSize * 0.15, eyeOffsetY, eyeSize * 0.5, 0, Math.PI * 2);
            ctx.fill();

            // 高光
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-eyeOffsetX - eyeSize * 0.15, eyeOffsetY - eyeSize * 0.2, eyeSize * 0.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeOffsetX - eyeSize * 0.15, eyeOffsetY - eyeSize * 0.2, eyeSize * 0.2, 0, Math.PI * 2);
            ctx.fill();
        }

        drawEyebrows(ctx, radius) {
            ctx.strokeStyle = '#2d2d2d';
            ctx.lineWidth = radius * 0.12;
            ctx.lineCap = 'round';

            // 左眉毛（愤怒斜下）
            ctx.beginPath();
            ctx.moveTo(-radius * 0.6, -radius * 0.45);
            ctx.lineTo(-radius * 0.15, -radius * 0.3);
            ctx.stroke();

            // 右眉毛（愤怒斜下）
            ctx.beginPath();
            ctx.moveTo(radius * 0.6, -radius * 0.45);
            ctx.lineTo(radius * 0.15, -radius * 0.3);
            ctx.stroke();
        }

        drawBeak(ctx, radius) {
            const beakX = 0;
            const beakY = radius * 0.2;

            // 上喙
            ctx.fillStyle = '#f5a623';
            ctx.beginPath();
            ctx.moveTo(beakX - radius * 0.15, beakY);
            ctx.lineTo(beakX + radius * 0.5, beakY + radius * 0.1);
            ctx.lineTo(beakX - radius * 0.1, beakY + radius * 0.2);
            ctx.closePath();
            ctx.fill();

            // 下喙
            ctx.fillStyle = '#e08e1b';
            ctx.beginPath();
            ctx.moveTo(beakX - radius * 0.1, beakY + radius * 0.2);
            ctx.lineTo(beakX + radius * 0.3, beakY + radius * 0.25);
            ctx.lineTo(beakX, beakY + radius * 0.35);
            ctx.closePath();
            ctx.fill();
        }

        drawTail(ctx, radius) {
            ctx.fillStyle = this.secondaryColor;
            
            // 尾羽
            for (let i = 0; i < 3; i++) {
                const angle = Math.PI + (i - 1) * 0.3;
                const length = radius * 0.8;
                const width = radius * 0.25;

                ctx.save();
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.moveTo(-radius * 0.7, 0);
                ctx.lineTo(-radius * 0.7 - length, -width);
                ctx.lineTo(-radius * 0.7 - length * 0.7, 0);
                ctx.lineTo(-radius * 0.7 - length, width);
                ctx.closePath();
                ctx.fill();
                ctx.restore();
            }
        }
    }

    // ============================================
    // 弹弓类
    // ============================================
    class Slingshot {
        constructor(x, y) {
            this.position = new Vector2(x, y);
            this.width = 30;
            this.height = 100;
            this.forkHeight = 70;
            this.pullPoint = new Vector2(x, y - this.forkHeight);
            this.maxPullDistance = 100;
            this.currentBird = null;
            this.isPulling = false;
            this.pullVector = new Vector2(0, 0);
        }

        attachBird(bird) {
            this.currentBird = bird;
            bird.position.x = this.pullPoint.x;
            bird.position.y = this.pullPoint.y;
        }

        startPull(mouseX, mouseY) {
            if (this.currentBird && !this.currentBird.isLaunched) {
                this.isPulling = true;
            }
        }

        updatePull(mouseX, mouseY, camera) {
            if (!this.isPulling || !this.currentBird) return;

            // 计算拉动向量（从弹弓中心到鼠标位置的反方向）
            const worldMouse = camera.screenToWorld(mouseX, mouseY);
            
            // 计算从拉动点到鼠标的向量
            const dx = this.pullPoint.x - worldMouse.x;
            const dy = this.pullPoint.y - worldMouse.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // 限制拉动距离
            const limitedDist = Math.min(distance, this.maxPullDistance);
            const angle = Math.atan2(dy, dx);

            this.pullVector.x = Math.cos(angle) * limitedDist;
            this.pullVector.y = Math.sin(angle) * limitedDist;

            // 更新小鸟位置
            this.currentBird.position.x = this.pullPoint.x - this.pullVector.x;
            this.currentBird.position.y = this.pullPoint.y - this.pullVector.y;
        }

        release() {
            if (!this.currentBird || !this.isPulling) {
                this.isPulling = false;
                return null;
            }

            // 计算发射速度（拉动向量的反方向，乘以力度因子）
            const power = 0.25;
            const velocity = new Vector2(
                -this.pullVector.x * power,
                -this.pullVector.y * power
            );

            this.currentBird.launch(velocity);
            const launchedBird = this.currentBird;
            this.currentBird = null;
            this.isPulling = false;
            this.pullVector = new Vector2(0, 0);

            return launchedBird;
        }

        draw(ctx, camera) {
            const screen = camera.worldToScreen(this.position.x, this.position.y);
            const scale = camera.zoom;

            // 后支架
            this.drawBackFork(ctx, screen, scale);

            // 绘制橡皮筋（后）
            if (this.currentBird && this.isPulling) {
                this.drawBackBand(ctx, screen, scale);
            }

            // 绘制小鸟
            if (this.currentBird) {
                this.currentBird.draw(ctx, camera);
            }

            // 绘制橡皮筋（前）
            if (this.currentBird && this.isPulling) {
                this.drawFrontBand(ctx, screen, scale);
            }

            // 前支架
            this.drawFrontFork(ctx, screen, scale);

            // 绘制拉动预览线
            if (this.isPulling && this.pullVector.length() > 10) {
                this.drawTrajectoryPreview(ctx, screen, scale);
            }
        }

        drawBackFork(ctx, screen, scale) {
            ctx.fillStyle = '#5d4037';
            ctx.strokeStyle = '#3e2723';
            ctx.lineWidth = 3 * scale;

            // 后支柱
            ctx.beginPath();
            ctx.moveTo(screen.x - 20 * scale, screen.y);
            ctx.lineTo(screen.x - 15 * scale, screen.y - this.forkHeight * scale);
            ctx.lineTo(screen.x - 25 * scale, screen.y - this.forkHeight * scale - 20 * scale);
            ctx.lineWidth = 8 * scale;
            ctx.stroke();

            // 后叉头
            ctx.fillStyle = '#6d4c41';
            ctx.beginPath();
            ctx.arc(screen.x - 20 * scale, screen.y - this.forkHeight * scale - 20 * scale, 8 * scale, 0, Math.PI * 2);
            ctx.fill();
        }

        drawFrontFork(ctx, screen, scale) {
            // 前支柱
            ctx.strokeStyle = '#8d6e63';
            ctx.lineWidth = 10 * scale;
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(screen.x + 10 * scale, screen.y);
            ctx.lineTo(screen.x + 5 * scale, screen.y - this.forkHeight * scale);
            ctx.stroke();

            // 前叉头
            ctx.fillStyle = '#a1887f';
            ctx.beginPath();
            ctx.arc(screen.x + 5 * scale, screen.y - this.forkHeight * scale - 20 * scale, 8 * scale, 0, Math.PI * 2);
            ctx.fill();

            // 底座
            ctx.fillStyle = '#4e342e';
            ctx.beginPath();
            ctx.moveTo(screen.x - 30 * scale, screen.y);
            ctx.lineTo(screen.x + 20 * scale, screen.y);
            ctx.lineTo(screen.x + 15 * scale, screen.y + 20 * scale);
            ctx.lineTo(screen.x - 25 * scale, screen.y + 20 * scale);
            ctx.closePath();
            ctx.fill();

            // 底座纹理
            ctx.strokeStyle = '#3e2723';
            ctx.lineWidth = 2 * scale;
            for (let i = 0; i < 3; i++) {
                ctx.beginPath();
                ctx.moveTo(screen.x - 20 * scale + i * 15 * scale, screen.y + 5 * scale);
                ctx.lineTo(screen.x - 25 * scale + i * 15 * scale, screen.y + 15 * scale);
                ctx.stroke();
            }
        }

        drawBackBand(ctx, screen, scale) {
            const birdScreen = camera.worldToScreen(this.currentBird.position.x, this.currentBird.position.y);
            
            ctx.strokeStyle = '#4a3728';
            ctx.lineWidth = 6 * scale;
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(screen.x - 20 * scale, screen.y - this.forkHeight * scale - 20 * scale);
            ctx.lineTo(birdScreen.x, birdScreen.y);
            ctx.stroke();
        }

        drawFrontBand(ctx, screen, scale) {
            const birdScreen = camera.worldToScreen(this.currentBird.position.x, this.currentBird.position.y);
            
            ctx.strokeStyle = '#6d5344';
            ctx.lineWidth = 5 * scale;
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(screen.x + 5 * scale, screen.y - this.forkHeight * scale - 20 * scale);
            ctx.lineTo(birdScreen.x, birdScreen.y);
            ctx.stroke();
        }

        drawTrajectoryPreview(ctx, screen, scale) {
            const power = 0.25;
            const vx = -this.pullVector.x * power;
            const vy = -this.pullVector.y * power;

            ctx.save();
            ctx.setLineDash([5, 5]);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 2 * scale;

            let px = this.currentBird.position.x;
            let py = this.currentBird.position.y;
            let pvx = vx;
            let pvy = vy;

            ctx.beginPath();
            const startScreen = camera.worldToScreen(px, py);
            ctx.moveTo(startScreen.x, startScreen.y);

            for (let i = 0; i < 30; i++) {
                pvy += CONFIG.GRAVITY;
                px += pvx;
                py += pvy;

                if (py > CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT) break;

                const previewScreen = camera.worldToScreen(px, py);
                ctx.lineTo(previewScreen.x, previewScreen.y);
            }

            ctx.stroke();
            ctx.restore();
        }
    }

    // ============================================
    // 猪类
    // ============================================
    class Pig extends GameObject {
        constructor(x, y, size = 'medium') {
            super(x, y);
            this.size = size;
            this.health = 100;
            this.rotation = 0;
            this.isDestroyed = false;
            this.wobble = 0;
            this.wobbleSpeed = Utils.randomRange(1, 3);

            this.setupSize();
        }

        setupSize() {
            switch (this.size) {
                case 'small':
                    this.radius = 18;
                    this.health = 50;
                    break;
                case 'medium':
                    this.radius = 25;
                    this.health = 100;
                    break;
                case 'large':
                    this.radius = 35;
                    this.health = 150;
                    break;
                default:
                    this.radius = 25;
            }
        }

        damage(amount) {
            this.health -= amount;
            this.wobble = 5;
            
            if (this.health <= 0) {
                this.isDestroyed = true;
            }
        }

        update(deltaTime) {
            if (this.wobble > 0) {
                this.wobble -= 0.1;
            }
        }

        draw(ctx, camera) {
            if (this.isDestroyed) return;

            const screen = this.getScreenPosition(camera);
            const scaledRadius = this.radius * camera.zoom;
            const wobbleAngle = Math.sin(this.wobble * 2) * 0.1;

            ctx.save();
            ctx.translate(screen.x, screen.y);
            ctx.rotate(wobbleAngle);

            // 身体阴影
            ctx.fillStyle = 'rgba(0,0,0,0.2)';
            ctx.beginPath();
            ctx.ellipse(scaledRadius * 0.1, scaledRadius * 0.1, scaledRadius, scaledRadius * 0.95, 0, 0, Math.PI * 2);
            ctx.fill();

            // 身体渐变
            const bodyGradient = ctx.createRadialGradient(
                -scaledRadius * 0.3, -scaledRadius * 0.3, 0,
                0, 0, scaledRadius
            );
            bodyGradient.addColorStop(0, '#7cb342');
            bodyGradient.addColorStop(0.7, '#689f38');
            bodyGradient.addColorStop(1, '#558b2f');

            ctx.fillStyle = bodyGradient;
            ctx.beginPath();
            ctx.arc(0, 0, scaledRadius, 0, Math.PI * 2);
            ctx.fill();

            // 耳朵
            this.drawEars(ctx, scaledRadius);

            // 眼睛
            this.drawEyes(ctx, scaledRadius);

            // 鼻子
            this.drawSnout(ctx, scaledRadius);

            // 伤害效果
            if (this.health < 100) {
                this.drawDamage(ctx, scaledRadius);
            }

            ctx.restore();
        }

        drawEars(ctx, radius) {
            ctx.fillStyle = '#689f38';
            
            // 左耳
            ctx.beginPath();
            ctx.ellipse(-radius * 0.7, -radius * 0.6, radius * 0.25, radius * 0.35, -0.3, 0, Math.PI * 2);
            ctx.fill();

            // 右耳
            ctx.beginPath();
            ctx.ellipse(radius * 0.7, -radius * 0.6, radius * 0.25, radius * 0.35, 0.3, 0, Math.PI * 2);
            ctx.fill();
        }

        drawEyes(ctx, radius) {
            const eyeOffsetX = radius * 0.3;
            const eyeOffsetY = -radius * 0.15;
            const eyeSize = radius * 0.25;

            // 眼白
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-eyeOffsetX, eyeOffsetY, eyeSize, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeOffsetX, eyeOffsetY, eyeSize, 0, Math.PI * 2);
            ctx.fill();

            // 瞳孔
            ctx.fillStyle = '#1a1a1a';
            ctx.beginPath();
            ctx.arc(-eyeOffsetX, eyeOffsetY, eyeSize * 0.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeOffsetX, eyeOffsetY, eyeSize * 0.5, 0, Math.PI * 2);
            ctx.fill();

            // 高光
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-eyeOffsetX - eyeSize * 0.2, eyeOffsetY - eyeSize * 0.2, eyeSize * 0.25, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeOffsetX - eyeSize * 0.2, eyeOffsetY - eyeSize * 0.2, eyeSize * 0.25, 0, Math.PI * 2);
            ctx.fill();
        }

        drawSnout(ctx, radius) {
            const snoutY = radius * 0.25;

            // 鼻子
            ctx.fillStyle = '#8bc34a';
            ctx.beginPath();
            ctx.ellipse(0, snoutY, radius * 0.35, radius * 0.25, 0, 0, Math.PI * 2);
            ctx.fill();

            // 鼻孔
            ctx.fillStyle = '#558b2f';
            ctx.beginPath();
            ctx.ellipse(-radius * 0.12, snoutY, radius * 0.08, radius * 0.1, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(radius * 0.12, snoutY, radius * 0.08, radius * 0.1, 0, 0, Math.PI * 2);
            ctx.fill();
        }

        drawDamage(ctx, radius) {
            const damageLevel = 1 - (this.health / 100);
            
            ctx.strokeStyle = '#33691e';
            ctx.lineWidth = 2;

            // 划痕
            const scratchCount = Math.floor(damageLevel * 5);
            for (let i = 0; i < scratchCount; i++) {
                const angle = Utils.randomRange(0, Math.PI * 2);
                const dist = Utils.randomRange(0.3, 0.8) * radius;
                const len = Utils.randomRange(5, 15);
                
                ctx.beginPath();
                ctx.moveTo(Math.cos(angle) * dist, Math.sin(angle) * dist);
                ctx.lineTo(Math.cos(angle) * (dist + len), Math.sin(angle) * (dist + len));
                ctx.stroke();
            }
        }
    }

    // ============================================
    // 木块类
    // ============================================
    class Block extends GameObject {
        constructor(x, y, width, height, type = 'wood') {
            super(x, y);
            this.width = width;
            this.height = height;
            this.type = type;
            this.health = 100;
            this.rotation = 0;
            this.isDestroyed = false;

            this.setupType();
        }

        setupType() {
            switch (this.type) {
                case 'wood':
                    this.color = '#8d6e63';
                    this.secondaryColor = '#6d4c41';
                    this.health = 80;
                    break;
                case 'stone':
                    this.color = '#78909c';
                    this.secondaryColor = '#546e7a';
                    this.health = 150;
                    break;
                case 'glass':
                    this.color = 'rgba(200, 230, 255, 0.7)';
                    this.secondaryColor = 'rgba(150, 200, 230, 0.8)';
                    this.health = 30;
                    break;
                default:
                    this.color = '#8d6e63';
                    this.secondaryColor = '#6d4c41';
            }
        }

        damage(amount) {
            this.health -= amount;
            if (this.health <= 0) {
                this.isDestroyed = true;
            }
        }

        update(deltaTime) {
            // 物理更新可以在这里
        }

        draw(ctx, camera) {
            if (this.isDestroyed) return;

            const screen = this.getScreenPosition(camera);
            const scaledWidth = this.width * camera.zoom;
            const scaledHeight = this.height * camera.zoom;

            ctx.save();
            ctx.translate(screen.x, screen.y);
            ctx.rotate(this.rotation);

            // 阴影
            ctx.fillStyle = 'rgba(0,0,0,0.2)';
            ctx.fillRect(-scaledWidth / 2 + 4, -scaledHeight / 2 + 4, scaledWidth, scaledHeight);

            // 主体
            ctx.fillStyle = this.color;
            ctx.fillRect(-scaledWidth / 2, -scaledHeight / 2, scaledWidth, scaledHeight);

            // 边框
            ctx.strokeStyle = this.secondaryColor;
            ctx.lineWidth = 2 * camera.zoom;
            ctx.strokeRect(-scaledWidth / 2, -scaledHeight / 2, scaledWidth, scaledHeight);

            // 纹理线条
            if (this.type === 'wood') {
                ctx.strokeStyle = 'rgba(0,0,0,0.1)';
                ctx.lineWidth = 1;
                for (let i = 0; i < 3; i++) {
                    const y = -scaledHeight / 2 + (i + 1) * scaledHeight / 4;
                    ctx.beginPath();
                    ctx.moveTo(-scaledWidth / 2 + 2, y);
                    ctx.lineTo(scaledWidth / 2 - 2, y);
                    ctx.stroke();
                }
            } else if (this.type === 'stone') {
                ctx.strokeStyle = 'rgba(0,0,0,0.15)';
                ctx.lineWidth = 1;
                for (let i = 0; i < 2; i++) {
                    for (let j = 0; j < 2; j++) {
                        const x = -scaledWidth / 2 + scaledWidth / 3 + i * scaledWidth / 3;
                        const y = -scaledHeight / 2 + scaledHeight / 3 + j * scaledHeight / 3;
                        ctx.beginPath();
                        ctx.arc(x, y, 3, 0, Math.PI * 2);
                        ctx.stroke();
                    }
                }
            } else if (this.type === 'glass') {
                // 玻璃反光
                ctx.fillStyle = 'rgba(255,255,255,0.3)';
                ctx.beginPath();
                ctx.moveTo(-scaledWidth / 2 + 5, -scaledHeight / 2 + 5);
                ctx.lineTo(-scaledWidth / 2 + scaledWidth * 0.3, -scaledHeight / 2 + 5);
                ctx.lineTo(-scaledWidth / 2 + 5, -scaledHeight / 2 + scaledHeight * 0.3);
                ctx.closePath();
                ctx.fill();
            }

            // 伤害裂纹
            if (this.health < 50) {
                ctx.strokeStyle = 'rgba(0,0,0,0.3)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-scaledWidth / 4, -scaledHeight / 2);
                ctx.lineTo(0, 0);
                ctx.lineTo(scaledWidth / 4, scaledHeight / 2);
                ctx.stroke();
            }

            ctx.restore();
        }
    }

    // ============================================
    // 场景管理器
    // ============================================
    class SceneManager {
        constructor() {
            this.scenes = new Map();
            this.currentScene = null;
        }

        register(name, scene) {
            this.scenes.set(name, scene);
        }

        switchTo(name) {
            if (this.currentScene) {
                this.currentScene.onExit();
            }
            this.currentScene = this.scenes.get(name);
            if (this.currentScene) {
                this.currentScene.onEnter();
            }
        }

        update(deltaTime) {
            if (this.currentScene) {
                this.currentScene.update(deltaTime);
            }
        }

        draw(ctx, camera) {
            if (this.currentScene) {
                this.currentScene.draw(ctx, camera);
            }
        }

        handleInput(input) {
            if (this.currentScene) {
                this.currentScene.handleInput(input);
            }
        }
    }

    // ============================================
    // 游戏场景
    // ============================================
    class GameScene {
        constructor(game) {
            this.game = game;
            this.birds = [];
            this.launchedBirds = [];
            this.pigs = [];
            this.blocks = [];
            this.score = 0;
            this.birdsLeft = 3;
            this.currentBirdIndex = 0;
            this.gameState = 'ready'; // ready, aiming, flying, ended
        }

        onEnter() {
            this.setupLevel();
        }

        onExit() {
            // 清理
        }

        setupLevel() {
            const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT;

            // 创建弹弓
            this.slingshot = new Slingshot(200, groundY);

            // 创建备用小鸟
            const birdTypes = ['red', 'yellow', 'blue'];
            for (let i = 0; i < this.birdsLeft; i++) {
                const bird = new Bird(100 - i * 40, groundY - 25, birdTypes[i % birdTypes.length]);
                this.birds.push(bird);
            }

            // 装载第一只小鸟
            this.loadNextBird();

            // 创建猪
            const pigConfigs = [
                { x: 900, y: groundY - 25, size: 'medium' },
                { x: 1000, y: groundY - 25, size: 'small' },
                { x: 950, y: groundY - 100, size: 'medium' }
            ];

            pigConfigs.forEach(config => {
                this.pigs.push(new Pig(config.x, config.y, config.size));
            });

            // 创建木块结构
            const blockConfigs = [
                // 底层
                { x: 850, y: groundY - 25, w: 20, h: 100, type: 'wood' },
                { x: 950, y: groundY - 25, w: 20, h: 100, type: 'wood' },
                { x: 1050, y: groundY - 25, w: 20, h: 100, type: 'wood' },
                // 横梁
                { x: 900, y: groundY - 80, w: 80, h: 20, type: 'wood' },
                { x: 1000, y: groundY - 80, w: 80, h: 20, type: 'wood' },
                // 第二层
                { x: 900, y: groundY - 125, w: 20, h: 80, type: 'glass' },
                { x: 1000, y: groundY - 125, w: 20, h: 80, type: 'glass' },
                // 顶部
                { x: 950, y: groundY - 170, w: 120, h: 15, type: 'stone' },
                // 额外结构
                { x: 1100, y: groundY - 40, w: 60, h: 60, type: 'stone' },
                { x: 800, y: groundY - 30, w: 40, h: 40, type: 'glass' }
            ];

            blockConfigs.forEach(config => {
                this.blocks.push(new Block(config.x, config.y, config.w, config.h, config.type));
            });
        }

        loadNextBird() {
            if (this.currentBirdIndex < this.birds.length) {
                this.slingshot.attachBird(this.birds[this.currentBirdIndex]);
                this.currentBirdIndex++;
            }
        }

        update(deltaTime) {
            // 更新所有对象
            this.birds.forEach(bird => bird.update(deltaTime));
            this.pigs.forEach(pig => pig.update(deltaTime));
            this.blocks.forEach(block => block.update(deltaTime));

            // 检测碰撞
            this.checkCollisions();

            // 更新相机跟随
            const flyingBird = this.launchedBirds.find(b => b.isLaunched && 
                (Math.abs(b.velocity.x) > 0.5 || Math.abs(b.velocity.y) > 0.5));
            
            if (flyingBird) {
                this.game.camera.follow(flyingBird.position.x, flyingBird.position.y - 100);
            } else {
                // 回到弹弓位置
                this.game.camera.follow(this.slingshot.position.x + 100, 0);
            }

            // 更新UI
            this.updateUI();

            // 检查游戏状态
            this.checkGameState();
        }

        checkCollisions() {
            this.launchedBirds.forEach(bird => {
                if (!bird.isLaunched) return;

                // 鸟与猪碰撞
                this.pigs.forEach(pig => {
                    if (pig.isDestroyed) return;
                    
                    const dist = Utils.distance(bird.position.x, bird.position.y, 
                                                 pig.position.x, pig.position.y);
                    if (dist < bird.radius + pig.radius) {
                        const damage = Math.abs(bird.velocity.x) + Math.abs(bird.velocity.y);
                        pig.damage(damage * 5);
                        bird.velocity.x *= 0.5;
                        bird.velocity.y *= 0.5;
                        
                        if (pig.isDestroyed) {
                            this.score += 500;
                        }
                    }
                });

                // 鸟与方块碰撞
                this.blocks.forEach(block => {
                    if (block.isDestroyed) return;
                    
                    // 简化的AABB碰撞检测
                    const birdLeft = bird.position.x - bird.radius;
                    const birdRight = bird.position.x + bird.radius;
                    const birdTop = bird.position.y - bird.radius;
                    const birdBottom = bird.position.y + bird.radius;
                    
                    const blockLeft = block.position.x - block.width / 2;
                    const blockRight = block.position.x + block.width / 2;
                    const blockTop = block.position.y - block.height / 2;
                    const blockBottom = block.position.y + block.height / 2;

                    if (birdRight > blockLeft && birdLeft < blockRight &&
                        birdBottom > blockTop && birdTop < blockBottom) {
                        
                        const damage = Math.abs(bird.velocity.x) + Math.abs(bird.velocity.y);
                        block.damage(damage * 3);
                        
                        // 反弹
                        const overlapX = Math.min(birdRight - blockLeft, blockRight - birdLeft);
                        const overlapY = Math.min(birdBottom - blockTop, blockBottom - birdTop);
                        
                        if (overlapX < overlapY) {
                            bird.velocity.x *= -0.5;
                        } else {
                            bird.velocity.y *= -0.5;
                        }
                        
                        if (block.isDestroyed) {
                            this.score += 100;
                        }
                    }
                });
            });
        }

        updateUI() {
            const scoreDisplay = document.getElementById('scoreDisplay');
            const birdsDisplay = document.getElementById('birdsDisplay');
            
            if (scoreDisplay) scoreDisplay.textContent = this.score;
            if (birdsDisplay) birdsDisplay.textContent = this.birdsLeft - this.currentBirdIndex + 1;
        }

        checkGameState() {
            // 检查是否所有猪都被消灭
            const allPigsDestroyed = this.pigs.every(pig => pig.isDestroyed);
            if (allPigsDestroyed) {
                this.gameState = 'won';
            }

            // 检查是否用完所有小鸟
            const allBirdsUsed = this.currentBirdIndex >= this.birds.length;
            const noFlyingBird = !this.launchedBirds.some(b => 
                Math.abs(b.velocity.x) > 0.5 || Math.abs(b.velocity.y) > 0.5);
            
            if (allBirdsUsed && noFlyingBird && !allPigsDestroyed) {
                this.gameState = 'lost';
            }
        }

        draw(ctx, camera) {
            // 绘制方块
            this.blocks.forEach(block => block.draw(ctx, camera));

            // 绘制猪
            this.pigs.forEach(pig => pig.draw(ctx, camera));

            // 绘制弹弓
            this.slingshot.draw(ctx, camera);

            // 绘制已发射的鸟
            this.launchedBirds.forEach(bird => bird.draw(ctx, camera));

            // 绘制备用小鸟
            for (let i = this.currentBirdIndex; i < this.birds.length; i++) {
                this.birds[i].draw(ctx, camera);
            }

            // 绘制游戏状态
            if (this.gameState === 'won') {
                this.drawGameMessage(ctx, 'Level Complete!', '#4caf50');
            } else if (this.gameState === 'lost') {
                this.drawGameMessage(ctx, 'Level Failed', '#f44336');
            }
        }

        drawGameMessage(ctx, message, color) {
            ctx.save();
            ctx.fillStyle = 'rgba(0,0,0,0.7)';
            ctx.fillRect(CONFIG.CANVAS_WIDTH / 2 - 200, CONFIG.CANVAS_HEIGHT / 2 - 60, 400, 120);
            
            ctx.fillStyle = color;
            ctx.font = 'bold 36px Segoe UI, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(message, CONFIG.CANVAS_WIDTH / 2, CONFIG.CANVAS_HEIGHT / 2 - 20);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = '18px Segoe UI, sans-serif';
            ctx.fillText('Press R to restart', CONFIG.CANVAS_WIDTH / 2, CONFIG.CANVAS_HEIGHT / 2 + 25);
            ctx.restore();
        }

        handleInput(input) {
            if (this.gameState !== 'ready' && this.gameState !== 'aiming' && this.gameState !== 'flying') {
                return;
            }

            // 鼠标按下开始瞄准
            if (input.mouse.isDown && !input.mouse.isDragging) {
                if (this.gameState === 'ready') {
                    this.slingshot.startPull(input.mouse.x, input.mouse.y);
                    this.gameState = 'aiming';
                }
            }

            // 拖动瞄准
            if (input.mouse.isDragging && this.gameState === 'aiming') {
                this.slingshot.updatePull(input.mouse.x, input.mouse.y, this.game.camera);
            }

            // 松开发射
            if (!input.mouse.isDown && this.gameState === 'aiming') {
                const launchedBird = this.slingshot.release();
                if (launchedBird) {
                    this.launchedBirds.push(launchedBird);
                    this.gameState = 'flying';
                    
                    // 延迟装载下一只鸟
                    setTimeout(() => {
                        if (this.currentBirdIndex < this.birds.length) {
                            this.loadNextBird();
                            this.gameState = 'ready';
                        }
                    }, 2000);
                } else {
                    this.gameState = 'ready';
                }
            }

            // 空格键快速发射
            if (input.isKeyPressed('Space') && this.gameState === 'ready') {
                const bird = this.slingshot.currentBird;
                if (bird) {
                    bird.launch(new Vector2(15, -12));
                    this.slingshot.currentBird = null;
                    this.launchedBirds.push(bird);
                    this.gameState = 'flying';
                    
                    setTimeout(() => {
                        if (this.currentBirdIndex < this.birds.length) {
                            this.loadNextBird();
                            this.gameState = 'ready';
                        }
                    }, 2000);
                }
            }
        }
    }

    // ============================================
    // 主游戏类
    // ============================================
    class Game {
        constructor() {
            this.canvas = document.getElementById('gameCanvas');
            this.ctx = this.canvas.getContext('2d');
            
            // 设置画布大小
            this.canvas.width = CONFIG.CANVAS_WIDTH;
            this.canvas.height = CONFIG.CANVAS_HEIGHT;

            // 初始化系统
            this.camera = new Camera();
            this.input = new InputManager(this.canvas);
            this.sceneManager = new SceneManager();
            
            // 初始化渲染器
            this.backgroundRenderer = new BackgroundRenderer(CONFIG.WORLD_WIDTH);
            this.groundRenderer = new GroundRenderer(CONFIG.WORLD_WIDTH);

            // 注册场景
            this.gameScene = new GameScene(this);
            this.sceneManager.register('game', this.gameScene);
            this.sceneManager.switchTo('game');

            // 游戏时间
            this.lastTime = 0;
            this.gameTime = 0;
            this.fps = 0;
            this.frameCount = 0;
            this.fpsUpdateTime = 0;

            // 调试模式
            this.debugMode = true;

            // 绑定事件
            this.bindEvents();

            // 启动游戏循环
            this.start();
        }

        bindEvents() {
            window.addEventListener('keydown', (e) => {
                // R键重置
                if (e.code === 'KeyR') {
                    this.reset();
                }
            });
        }

        reset() {
            this.gameScene = new GameScene(this);
            this.sceneManager.register('game', this.gameScene);
            this.sceneManager.switchTo('game');
            this.camera = new Camera();
        }

        start() {
            this.lastTime = performance.now();
            this.gameLoop();
        }

        gameLoop() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - this.lastTime) / 1000;
            this.lastTime = currentTime;

            // 限制deltaTime防止大跳跃
            const clampedDelta = Math.min(deltaTime, 0.1);

            // 更新FPS
            this.updateFPS(currentTime, clampedDelta);

            // 更新游戏时间
            this.gameTime += clampedDelta;

            // 处理输入
            this.handleGlobalInput();

            // 更新
            this.update(clampedDelta);

            // 渲染
            this.render();

            // 更新调试面板
            this.updateDebugPanel();

            // 继续循环
            requestAnimationFrame(() => this.gameLoop());
        }

        updateFPS(currentTime, deltaTime) {
            this.frameCount++;
            this.fpsUpdateTime += deltaTime;
            
            if (this.fpsUpdateTime >= 1) {
                this.fps = this.frameCount;
                this.frameCount = 0;
                this.fpsUpdateTime = 0;
            }
        }

        handleGlobalInput() {
            // 相机控制
            const moveSpeed = 10;
            
            if (this.input.isKeyPressed('KeyA')) {
                this.camera.follow(this.camera.position.x - moveSpeed, this.camera.position.y, true);
            }
            if (this.input.isKeyPressed('KeyD')) {
                this.camera.follow(this.camera.position.x + moveSpeed, this.camera.position.y, true);
            }
            if (this.input.isKeyPressed('KeyW')) {
                this.camera.setZoom(this.camera.zoom + 0.02);
            }
            if (this.input.isKeyPressed('KeyS')) {
                this.camera.setZoom(this.camera.zoom - 0.02);
            }

            // 更新鼠标世界坐标
            this.input.updateWorldPosition(this.camera);
        }

        update(deltaTime) {
            // 更新相机
            this.camera.update(deltaTime);

            // 更新背景
            this.backgroundRenderer.update(deltaTime);
            this.groundRenderer.update(deltaTime, this.gameTime);

            // 更新场景
            this.sceneManager.update(deltaTime);

            // 处理场景输入
            this.sceneManager.handleInput(this.input);
        }

        render() {
            // 清空画布
            this.ctx.clearRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

            // 绘制背景
            this.backgroundRenderer.draw(this.ctx, this.camera);

            // 绘制地面
            this.groundRenderer.draw(this.ctx, this.camera);

            // 绘制场景
            this.sceneManager.draw(this.ctx, this.camera);

            // 绘制UI覆盖层
            this.drawUIOverlay();
        }

        drawUIOverlay() {
            // 绘制准星（鼠标位置）
            this.ctx.save();
            this.ctx.strokeStyle = 'rgba(233, 69, 96, 0.5)';
            this.ctx.lineWidth = 1;
            
            // 十字准星
            const mx = this.input.mouse.x;
            const my = this.input.mouse.y;
            
            this.ctx.beginPath();
            this.ctx.moveTo(mx - 10, my);
            this.ctx.lineTo(mx + 10, my);
            this.ctx.moveTo(mx, my - 10);
            this.ctx.lineTo(mx, my + 10);
            this.ctx.stroke();
            
            // 圆圈
            this.ctx.beginPath();
            this.ctx.arc(mx, my, 5, 0, Math.PI * 2);
            this.ctx.stroke();
            
            this.ctx.restore();
        }

        updateDebugPanel() {
            if (!this.debugMode) return;

            const debugPanel = document.getElementById('debugPanel');
            if (debugPanel) {
                debugPanel.innerHTML = `
                    FPS: ${this.fps}<br>
                    Camera: ${this.camera.position.x.toFixed(0)}, ${this.camera.position.y.toFixed(0)}<br>
                    Zoom: ${this.camera.zoom.toFixed(2)}x<br>
                    Mouse: ${this.input.mouse.worldX.toFixed(0)}, ${this.input.mouse.worldY.toFixed(0)}
                `;
            }
        }
    }

    // ============================================
    // 初始化
    // ============================================
    window.addEventListener('DOMContentLoaded', () => {
        // 检查 reduced motion 偏好
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        // 创建游戏实例
        const game = new Game();
        
        console.log('Angry Birds Game Framework Loaded');
        console.log('Controls:');
        console.log('  - Click and drag on bird to aim');
        console.log('  - Release to launch');
        console.log('  - A/D: Move camera');
        console.log('  - W/S: Zoom in/out');
        console.log('  - Space: Quick launch');
        console.log('  - R: Reset game');
    });
    </script>
</body>
</html>
```

## 代码说明

### 核心架构

1. **游戏循环系统**
   - 使用 `requestAnimationFrame` 实现60FPS流畅渲染
   - 包含 `deltaTime` 计算确保帧率无关的物理模拟
   - FPS监控和时间管理

2. **场景管理器**
   - 支持多场景注册和切换
   - 包含完整的生命周期：`onEnter`、`onExit`、`update`、`draw`
   - 解耦的场景输入处理

3. **相机系统**
   - 平滑跟随目标（lerp插值）
   - 支持缩放（0.5x - 2.0x）
   - 世界坐标与屏幕坐标转换

### 渲染管线

1. **视差背景**
   - 三层远山（不同视差因子）
   - 动态云层系统（自动生成和回收）
   - 闪烁星空效果

2. **地面渲染**
   - 多层渐变地面
   - 程序化生成的草地摇摆动画
   - 岩石和花朵装饰

3. **游戏对象渲染**
   - 小鸟：带有愤怒表情、轨迹效果
   - 猪：带有可爱的猪特征和受伤效果
   - 木块：三种材质（木头、石头、玻璃）

### 交互功能

- **弹弓瞄准系统**：拖拽瞄准，轨迹预览
- **键盘控制**：相机移动（A/D）、缩放（W/S）、快速发射
- **碰撞检测**：简化的圆形与AABB碰撞

### 操作说明

| 按键 | 功能 |
|------|------|
| 鼠标拖拽 | 瞄准并发射小鸟 |
| A / D | 左右移动相机 |
| W / S | 放大/缩小视野 |
| Space | 快速发射 |
| R | 重置游戏 |