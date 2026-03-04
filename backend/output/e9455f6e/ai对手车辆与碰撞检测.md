# AI对手车辆与碰撞检测

**Time**: 2026-02-28T22:52:26.954069

---

我来为你实现AI对手车辆与碰撞检测系统。这需要在现有代码基础上添加AI车辆类、碰撞检测系统、层级排序和阴影渲染。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neon Racer - AI Opponents & Collision</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
        
        :root {
            --bg-dark: #0a0a0f;
            --bg-panel: rgba(15, 15, 25, 0.95);
            --neon-cyan: #00f5ff;
            --neon-pink: #ff2d75;
            --neon-yellow: #f0ff00;
            --neon-green: #00ff88;
            --neon-orange: #ff8800;
            --neon-purple: #b347ea;
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
        
        #vfxCanvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            border-radius: 8px;
        }
        
        #nitroOverlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            border-radius: 8px;
            opacity: 0;
            transition: opacity 0.1s;
            box-shadow: inset 0 0 100px rgba(0, 245, 255, 0.5);
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
        
        .perf-label { color: var(--text-muted); }
        
        .perf-value {
            font-weight: bold;
            font-family: 'Orbitron', sans-serif;
        }
        
        .perf-value.fps { color: var(--neon-green); }
        .perf-value.frame { color: var(--neon-yellow); }
        .perf-value.particles { color: var(--neon-pink); }
        .perf-value.ai { color: var(--neon-orange); }
        
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
        
        #hud {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 16px 20px;
            backdrop-filter: blur(10px);
            z-index: 100;
            min-width: 220px;
        }
        
        #speedometer {
            position: relative;
            width: 180px;
            height: 100px;
            margin-bottom: 10px;
        }
        
        #speedBar {
            width: 100%;
            height: 8px;
            background: rgba(0,0,0,0.5);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        #speedFill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, var(--neon-green), var(--neon-yellow), var(--neon-pink));
            border-radius: 4px;
            transition: width 0.1s;
        }
        
        #speedText {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            color: var(--neon-cyan);
            text-align: center;
            text-shadow: 0 0 20px var(--neon-cyan);
        }
        
        #speedUnit {
            font-size: 12px;
            color: var(--text-muted);
            text-align: center;
        }
        
        #gearIndicator {
            font-family: 'Orbitron', sans-serif;
            font-size: 18px;
            color: var(--neon-yellow);
            text-align: center;
            margin-top: 4px;
        }
        
        #nitroBar {
            width: 100%;
            height: 6px;
            background: rgba(0,0,0,0.5);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        #nitroFill {
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan));
            border-radius: 3px;
            transition: width 0.1s;
        }
        
        #positionIndicator {
            position: absolute;
            top: 10px;
            left: 10px;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px 16px;
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        
        #positionText {
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            color: var(--neon-yellow);
            text-shadow: 0 0 20px var(--neon-yellow);
        }
        
        #positionSuffix {
            font-size: 16px;
            color: var(--text-muted);
        }
        
        #lapCounter {
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        
        #collisionFlash {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            border-radius: 8px;
            opacity: 0;
            background: radial-gradient(circle, transparent 30%, rgba(255, 45, 117, 0.3) 100%);
            transition: opacity 0.05s;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <canvas id="vfxCanvas"></canvas>
        <div id="nitroOverlay"></div>
        <div id="collisionFlash"></div>
        
        <div id="positionIndicator">
            <span id="positionText">1</span><span id="positionSuffix">st</span>
            <div id="lapCounter">LAP 1/3</div>
        </div>
        
        <div id="performancePanel">
            <h3>PERFORMANCE</h3>
            <div class="perf-row">
                <span class="perf-label">FPS</span>
                <span class="perf-value fps" id="fpsValue">60</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Frame</span>
                <span class="perf-value frame" id="frameValue">0ms</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Particles</span>
                <span class="perf-value particles" id="particleValue">0</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">AI Cars</span>
                <span class="perf-value ai" id="aiValue">0</span>
            </div>
        </div>
        
        <div id="controls">
            <h4>CONTROLS</h4>
            <span class="key-hint">↑</span> Accelerate<br>
            <span class="key-hint">↓</span> Brake<br>
            <span class="key-hint">←</span> <span class="key-hint">→</span> Steer<br>
            <span class="key-hint">SPACE</span> Nitro<br>
            <span class="key-hint">SHIFT</span> Handbrake
        </div>
        
        <div id="hud">
            <div id="speedometer">
                <div id="speedBar">
                    <div id="speedFill"></div>
                </div>
                <div id="speedText">0</div>
                <div id="speedUnit">KM/H</div>
                <div id="gearIndicator">N</div>
            </div>
            <div id="nitroBar">
                <div id="nitroFill"></div>
            </div>
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
        
        ROAD_WIDTH: 2000,
        SEGMENT_LENGTH: 200,
        DRAW_DISTANCE: 150,
        FOV: 100,
        CAMERA_HEIGHT: 1000,
        CAMERA_DEPTH: 0,
        
        TRACK_LENGTH: 500,
        LAP_LENGTH: 500,
        
        COLORS: {
            sky: { top: '#0a0a1a', bottom: '#1a1a3a' },
            horizon: '#1a0a2e',
            bgDark: '#0a0a0f',
            road: '#1a1a2e',
            roadLine: '#00f5ff',
            roadLineGlow: 'rgba(0, 245, 255, 0.5)',
            neonCyan: '#00f5ff',
            neonPink: '#ff2d75',
            neonYellow: '#f0ff00',
            neonGreen: '#00ff88',
            neonOrange: '#ff8800',
            neonPurple: '#b347ea',
            
            asphalt: { light: '#2a2a3e', dark: '#1e1e2e' },
            grass: { light: '#0a2a1a', dark: '#061a0e' },
            rumble: { light: '#ff2d75', dark: '#ffffff' },
            lane: 'rgba(0, 245, 255, 0.4)'
        }
    };

    CONFIG.CAMERA_DEPTH = 1 / Math.tan((CONFIG.FOV / 2) * Math.PI / 180);

    // ============================================
    // 玩家车辆配置
    // ============================================
    const PLAYER_CONFIG = {
        maxSpeed: 320,
        acceleration: 0.8,
        braking: -1.2,
        deceleration: -0.15,
        offRoadDeceleration: -0.8,
        offRoadLimit: 0.4,
        
        centrifugal: 0.35,
        
        steerSpeed: 0.12,
        steerMax: 0.7,
        steerReturn: 0.15,
        
        driftFactor: 0.94,
        driftThreshold: 0.25,
        driftSteerMultiplier: 1.5,
        driftSpeedPenalty: 0.995,
        
        handbrakeGrip: 0.85,
        handbrakeTurnBoost: 1.8,
        
        nitroMax: 100,
        nitroDrain: 0.8,
        nitroRecharge: 0.15,
        nitroBoost: 1.5,
        
        collisionRadius: 80,
        collisionBounce: 0.6,
        collisionSpeedPenalty: 0.7,
        
        gears: [
            { minSpeed: 0, maxSpeed: 60, accel: 1.0, name: '1' },
            { minSpeed: 60, maxSpeed: 120, accel: 0.85, name: '2' },
            { minSpeed: 120, maxSpeed: 180, accel: 0.7, name: '3' },
            { minSpeed: 180, maxSpeed: 240, accel: 0.55, name: '4' },
            { minSpeed: 240, maxSpeed: 320, accel: 0.4, name: '5' }
        ]
    };

    // ============================================
    // AI配置
    // ============================================
    const AI_CONFIG = {
        count: 4,
        minSpeed: 180,
        maxSpeed: 280,
        reactionTime: 0.1,
        laneChangeInterval: 2,
        laneChangeChance: 0.3,
        overtakeDistance: 300,
        avoidDistance: 200,
        collisionRadius: 80,
        acceleration: 0.5,
        deceleration: 0.3
    };

    // ============================================
    // 工具类
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
        
        static easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }
        
        static exponentialFog(distance, density) {
            return 1 / Math.pow(Math.E, (distance * distance * density));
        }
        
        static project(p, cameraX, cameraY, cameraZ, cameraDepth, width, height, roadWidth) {
            const translatedZ = p.z - cameraZ;
            p.camera = {
                x: p.x - cameraX,
                y: p.y - cameraY,
                z: translatedZ
            };
            
            if (translatedZ <= 0) {
                p.screen = { x: 0, y: 0, w: 0, scale: 0 };
                return p;
            }
            
            const scale = cameraDepth / translatedZ;
            p.screen = {
                x: Math.round(width / 2 + scale * p.camera.x * width / 2),
                y: Math.round(height / 2 - scale * p.camera.y * height / 2),
                w: Math.round(scale * roadWidth * width / 2),
                scale: scale
            };
            
            return p;
        }
        
        static distance2D(x1, z1, x2, z2) {
            const dx = x2 - x1;
            const dz = z2 - z1;
            return Math.sqrt(dx * dx + dz * dz);
        }
    }

    // ============================================
    // 输入管理器
    // ============================================
    class InputManager {
        constructor() {
            this.keys = {};
            this.keysJustPressed = {};
            this.bindEvents();
        }
        
        bindEvents() {
            window.addEventListener('keydown', (e) => {
                if (!this.keys[e.code]) {
                    this.keysJustPressed[e.code] = true;
                }
                this.keys[e.code] = true;
                
                if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
                    e.preventDefault();
                }
            });
            
            window.addEventListener('keyup', (e) => {
                this.keys[e.code] = false;
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
        }
    }

    // ============================================
    // 粒子系统
    // ============================================
    class Particle {
        constructor(x, y, vx, vy, life, size, color, type = 'default') {
            this.x = x;
            this.y = y;
            this.vx = vx;
            this.vy = vy;
            this.life = life;
            this.maxLife = life;
            this.size = size;
            this.color = color;
            this.type = type;
            this.alpha = 1;
            this.rotation = Math.random() * Math.PI * 2;
            this.rotationSpeed = (Math.random() - 0.5) * 0.2;
        }
        
        update(dt) {
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            this.life -= dt;
            this.alpha = Math.max(0, this.life / this.maxLife);
            this.rotation += this.rotationSpeed * dt;
            
            if (this.type === 'smoke') {
                this.size *= 1.02;
                this.vy -= 0.5 * dt;
            } else if (this.type === 'spark') {
                this.vy += 0.3 * dt;
            } else if (this.type === 'speedline') {
                this.size *= 0.98;
            }
            
            return this.life > 0;
        }
    }

    class ParticleSystem {
        constructor() {
            this.particles = [];
            this.maxParticles = 500;
        }
        
        emit(x, y, count, config) {
            for (let i = 0; i < count && this.particles.length < this.maxParticles; i++) {
                const angle = config.angle + (Math.random() - 0.5) * config.spread;
                const speed = config.speed * (0.5 + Math.random() * 0.5);
                const particle = new Particle(
                    x + (Math.random() - 0.5) * (config.offsetX || 0),
                    y + (Math.random() - 0.5) * (config.offsetY || 0),
                    Math.cos(angle) * speed,
                    Math.sin(angle) * speed,
                    config.life * (0.5 + Math.random() * 0.5),
                    config.size * (0.5 + Math.random() * 0.5),
                    config.color,
                    config.type
                );
                this.particles.push(particle);
            }
        }
        
        emitSpeedLines(x, y, count, speedRatio) {
            const config = {
                angle: Math.PI,
                spread: 0.3,
                speed: 15 + speedRatio * 25,
                life: 0.3 + speedRatio * 0.3,
                size: 50 + speedRatio * 100,
                color: `rgba(0, 245, 255, ${0.3 + speedRatio * 0.4})`,
                type: 'speedline',
                offsetX: 100,
                offsetY: 50
            };
            this.emit(x, y, count, config);
        }
        
        emitTireSmoke(x, y, intensity) {
            const config = {
                angle: -Math.PI / 2,
                spread: Math.PI / 3,
                speed: 2 + intensity * 3,
                life: 0.8 + Math.random() * 0.4,
                size: 8 + intensity * 12,
                color: `rgba(180, 180, 180, ${0.3 + intensity * 0.3})`,
                type: 'smoke',
                offsetX: 30,
                offsetY: 10
            };
            this.emit(x, y, Math.floor(2 + intensity * 4), config);
        }
        
        emitSparks(x, y, intensity) {
            const config = {
                angle: -Math.PI / 2,
                spread: Math.PI,
                speed: 8 + intensity * 12,
                life: 0.4 + Math.random() * 0.3,
                size: 2 + intensity * 3,
                color: CONFIG.COLORS.neonOrange,
                type: 'spark',
                offsetX: 20,
                offsetY: 10
            };
            this.emit(x, y, Math.floor(3 + intensity * 5), config);
        }
        
        emitNitroFlame(x, y) {
            const colors = [CONFIG.COLORS.neonCyan, CONFIG.COLORS.neonPurple, CONFIG.COLORS.neonPink];
            const config = {
                angle: Math.PI,
                spread: 0.5,
                speed: 10 + Math.random() * 5,
                life: 0.2 + Math.random() * 0.2,
                size: 15 + Math.random() * 15,
                color: colors[Math.floor(Math.random() * colors.length)],
                type: 'flame',
                offsetX: 40,
                offsetY: 15
            };
            this.emit(x, y, 4, config);
        }
        
        emitCollisionSparks(x, y) {
            const config = {
                angle: 0,
                spread: Math.PI * 2,
                speed: 15,
                life: 0.5,
                size: 4,
                color: CONFIG.COLORS.neonYellow,
                type: 'spark',
                offsetX: 0,
                offsetY: 0
            };
            this.emit(x, y, 15, config);
        }
        
        update(dt) {
            this.particles = this.particles.filter(p => p.update(dt));
        }
        
        render(ctx, camera) {
            ctx.save();
            
            for (const p of this.particles) {
                ctx.globalAlpha = p.alpha;
                
                if (p.type === 'speedline') {
                    ctx.strokeStyle = p.color;
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    const lineLength = p.size * p.alpha;
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p.x - Math.cos(p.rotation) * lineLength, p.y - Math.sin(p.rotation) * lineLength);
                    ctx.stroke();
                } else if (p.type === 'smoke') {
                    const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
                    gradient.addColorStop(0, `rgba(150, 150, 150, ${p.alpha * 0.5})`);
                    gradient.addColorStop(1, `rgba(100, 100, 100, 0)`);
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                } else if (p.type === 'spark') {
                    ctx.fillStyle = p.color;
                    ctx.shadowColor = p.color;
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;
                } else if (p.type === 'flame') {
                    const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
                    gradient.addColorStop(0, p.color);
                    gradient.addColorStop(0.5, `rgba(255, 255, 255, ${p.alpha * 0.5})`);
                    gradient.addColorStop(1, `rgba(0, 245, 255, 0)`);
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            ctx.restore();
        }
        
        get count() {
            return this.particles.length;
        }
    }

    // ============================================
    // 相机震动系统
    // ============================================
    class CameraShake {
        constructor() {
            this.shakeX = 0;
            this.shakeY = 0;
            this.intensity = 0;
            this.decay = 0.9;
        }
        
        trigger(intensity) {
            this.intensity = Math.max(this.intensity, intensity);
        }
        
        update(dt) {
            if (this.intensity > 0.01) {
                this.shakeX = (Math.random() - 0.5) * this.intensity * 2;
                this.shakeY = (Math.random() - 0.5) * this.intensity * 2;
                this.intensity *= this.decay;
            } else {
                this.shakeX = 0;
                this.shakeY = 0;
                this.intensity = 0;
            }
        }
        
        get offsetX() { return this.shakeX; }
        get offsetY() { return this.shakeY; }
    }

    // ============================================
    // 赛道生成器
    // ============================================
    class TrackBuilder {
        constructor() {
            this.segments = [];
        }
        
        build() {
            this.segments = [];
            
            this.addStraight(50);
            this.addCurve(30, 2);
            this.addHill(30, 30);
            this.addCurve(25, -3);
            this.addStraight(40);
            this.addCurve(35, 4);
            this.addHill(20, -20);
            this.addCurve(30, -2);
            this.addStraight(30);
            this.addCurve(40, 3);
            this.addHill(25, 25);
            this.addStraight(45);
            this.addCurve(30, -4);
            this.addHill(35, -30);
            this.addStraight(50);
            
            let z = 0;
            let x = 0;
            let y = 0;
            
            for (let i = 0; i < this.segments.length; i++) {
                const seg = this.segments[i];
                seg.index = i;
                seg.z = z;
                seg.x = x;
                seg.y = y;
                
                z += CONFIG.SEGMENT_LENGTH;
                x += seg.curve || 0;
                y += seg.hill || 0;
                
                seg.p1 = { x: x, y: y, z: z };
                seg.p2 = { x: x + (seg.curve || 0), y: y + (seg.hill || 0), z: z + CONFIG.SEGMENT_LENGTH };
            }
            
            return this.segments;
        }
        
        addStraight(length) {
            for (let i = 0; i < length; i++) {
                this.segments.push({ curve: 0, hill: 0 });
            }
        }
        
        addCurve(length, intensity) {
            for (let i = 0; i < length; i++) {
                const factor = Math.sin((i / length) * Math.PI);
                this.segments.push({ curve: intensity * factor, hill: 0 });
            }
        }
        
        addHill(length, height) {
            for (let i = 0; i < length; i++) {
                const factor = Math.sin((i / length) * Math.PI);
                this.segments.push({ curve: 0, hill: (height / length) * factor * 2 });
            }
        }
        
        getSegment(z) {
            const index = Math.floor(z / CONFIG.SEGMENT_LENGTH) % this.segments.length;
            return this.segments[index >= 0 ? index : index + this.segments.length];
        }
        
        get length() {
            return this.segments.length * CONFIG.SEGMENT_LENGTH;
        }
    }

    // ============================================
    // 玩家车辆类
    // ============================================
    class PlayerCar {
        constructor() {
            this.x = 0;
            this.z = 0;
            this.y = 0;
            this.speed = 0;
            this.steer = 0;
            this.driftAngle = 0;
            this.nitro = PLAYER_CONFIG.nitroMax;
            this.nitroActive = false;
            this.isDrifting = false;
            this.isOffRoad = false;
            this.handbrake = false;
            this.currentGear = 0;
            this.width = 80;
            this.height = 40;
            this.vx = 0;
            this.vz = 0;
            this.colliding = false;
            this.collisionCooldown = 0;
        }
        
        update(dt, input, track, cameraShake, particleSystem) {
            const speedRatio = this.speed / PLAYER_CONFIG.maxSpeed;
            
            // 处理碰撞冷却
            if (this.collisionCooldown > 0) {
                this.collisionCooldown -= dt;
            }
            
            // 加速与刹车
            let accel = 0;
            if (input.isKeyDown('ArrowUp')) {
                const gearMultiplier = this.getGearMultiplier();
                accel = PLAYER_CONFIG.acceleration * gearMultiplier;
            } else if (input.isKeyDown('ArrowDown')) {
                accel = PLAYER_CONFIG.braking;
            } else {
                accel = PLAYER_CONFIG.deceleration;
            }
            
            // 氮气加速
            this.nitroActive = input.isKeyDown('Space') && this.nitro > 0 && this.speed > 50;
            if (this.nitroActive) {
                this.nitro -= PLAYER_CONFIG.nitroDrain;
                accel *= PLAYER_CONFIG.nitroBoost;
            } else if (this.nitro < PLAYER_CONFIG.nitroMax) {
                this.nitro += PLAYER_CONFIG.nitroRecharge;
            }
            this.nitro = MathUtils.clamp(this.nitro, 0, PLAYER_CONFIG.nitroMax);
            
            // 手刹
            this.handbrake = input.isKeyDown('ShiftLeft') || input.isKeyDown('ShiftRight');
            
            // 转向
            const steerInput = (input.isKeyDown('ArrowLeft') ? 1 : 0) - (input.isKeyDown('ArrowRight') ? 1 : 0);
            if (steerInput !== 0) {
                let steerMult = 1;
                if (this.handbrake) {
                    steerMult = PLAYER_CONFIG.handbrakeTurnBoost;
                }
                if (this.isDrifting) {
                    steerMult *= PLAYER_CONFIG.driftSteerMultiplier;
                }
                this.steer += steerInput * PLAYER_CONFIG.steerSpeed * steerMult * (1 - speedRatio * 0.5);
                this.steer = MathUtils.clamp(this.steer, -PLAYER_CONFIG.steerMax, PLAYER_CONFIG.steerMax);
            } else {
                this.steer *= (1 - PLAYER_CONFIG.steerReturn);
            }
            
            // 应用加速度
            this.speed += accel * dt * 60;
            
            // 离心力
            const segment = track.getSegment(this.z);
            if (segment) {
                this.x += segment.curve * speedRatio * PLAYER_CONFIG.centrifugal * dt * 60;
            }
            
            // 转向移动
            if (this.handbrake) {
                this.driftAngle = MathUtils.lerp(this.driftAngle, this.steer * 0.8, 0.1);
                this.speed *= Math.pow(PLAYER_CONFIG.handbrakeGrip, dt * 60);
            } else {
                this.driftAngle = MathUtils.lerp(this.driftAngle, this.steer * 0.3, 0.05);
            }
            
            this.x += this.steer * this.speed * 0.002 * dt * 60;
            
            // 漂移检测
            this.isDrifting = Math.abs(this.driftAngle) > PLAYER_CONFIG.driftThreshold && this.speed > 100;
            if (this.isDrifting) {
                this.speed *= Math.pow(PLAYER_CONFIG.driftSpeedPenalty, dt * 60);
            }
            
            // 离开赛道减速
            const halfRoad = CONFIG.ROAD_WIDTH / 2 - 100;
            this.isOffRoad = Math.abs(this.x) > halfRoad;
            if (this.isOffRoad) {
                this.speed += PLAYER_CONFIG.offRoadDeceleration * dt * 60;
                if (this.speed > PLAYER_CONFIG.maxSpeed * PLAYER_CONFIG.offRoadLimit) {
                    this.speed = MathUtils.lerp(this.speed, PLAYER_CONFIG.maxSpeed * PLAYER_CONFIG.offRoadLimit, 0.05);
                }
            }
            
            // 速度限制
            this.speed = MathUtils.clamp(this.speed, 0, PLAYER_CONFIG.maxSpeed);
            
            // 更新位置
            this.z += this.speed * dt * 60;
            
            // 循环赛道
            const trackLength = track.length;
            while (this.z >= trackLength) {
                this.z -= trackLength;
            }
            while (this.z < 0) {
                this.z += trackLength;
            }
            
            // 获取Y位置
            if (segment) {
                const segmentProgress = (this.z % CONFIG.SEGMENT_LENGTH) / CONFIG.SEGMENT_LENGTH;
                const nextSegment = track.getSegment(this.z + CONFIG.SEGMENT_LENGTH);
                this.y = MathUtils.lerp(segment.y || 0, nextSegment?.y || 0, segmentProgress);
            }
            
            // 特效
            if (this.isDrifting && this.speed > 100) {
                const driftIntensity = Math.abs(this.driftAngle) / PLAYER_CONFIG.steerMax;
                cameraShake.trigger(driftIntensity * 2);
                particleSystem.emitTireSmoke(
                    CONFIG.CANVAS_WIDTH / 2 - this.steer * 50,
                    CONFIG.CANVAS_HEIGHT - 150,
                    driftIntensity
                );
            }
            
            if (this.isOffRoad && this.speed > 80) {
                particleSystem.emitSparks(
                    CONFIG.CANVAS_WIDTH / 2 + (Math.random() - 0.5) * 100,
                    CONFIG.CANVAS_HEIGHT - 140,
                    0.3
                );
            }
            
            if (this.nitroActive) {
                particleSystem.emitNitroFlame(
                    CONFIG.CANVAS_WIDTH / 2,
                    CONFIG.CANVAS_HEIGHT - 130
                );
            }
            
            // 更新档位
            this.updateGear();
        }
        
        getGearMultiplier() {
            for (let i = PLAYER_CONFIG.gears.length - 1; i >= 0; i--) {
                if (this.speed >= PLAYER_CONFIG.gears[i].minSpeed) {
                    this.currentGear = i;
                    return PLAYER_CONFIG.gears[i].accel;
                }
            }
            return 1.0;
        }
        
        updateGear() {
            for (let i = PLAYER_CONFIG.gears.length - 1; i >= 0; i--) {
                if (this.speed >= PLAYER_CONFIG.gears[i].minSpeed) {
                    this.currentGear = i;
                    return;
                }
            }
            this.currentGear = 0;
        }
        
        applyCollision(otherX, otherZ, isPlayer = true) {
            if (this.collisionCooldown > 0) return;
            
            const dx = this.x - otherX;
            const dz = this.z - otherZ;
            const distance = Math.sqrt(dx * dx + dz * dz);
            
            if (distance < 0.01) return;
            
            // 归一化方向
            const nx = dx / distance;
            const nz = dz / distance;
            
            // 弹开
            const bounceForce = PLAYER_CONFIG.collisionBounce;
            this.x += nx * bounceForce * 50;
            
            // 速度衰减
            this.speed *= PLAYER_CONFIG.collisionSpeedPenalty;
            
            this.collisionCooldown = 0.3;
            this.colliding = true;
        }
        
        render(ctx, screenX, screenY, scale, isPlayer = true) {
            ctx.save();
            
            const carWidth = this.width * scale;
            const carHeight = this.height * scale;
            
            // 阴影
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.beginPath();
            ctx.ellipse(screenX, screenY + carHeight * 0.3, carWidth * 0.8, carHeight * 0.3, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // 车身
            ctx.translate(screenX, screenY);
            ctx.rotate(this.driftAngle * 0.5);
            
            // 主体
            const gradient = ctx.createLinearGradient(-carWidth/2, -carHeight/2, carWidth/2, carHeight/2);
            gradient.addColorStop(0, '#00f5ff');
            gradient.addColorStop(0.5, '#0088aa');
            gradient.addColorStop(1, '#004466');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.moveTo(-carWidth * 0.5, carHeight * 0.3);
            ctx.lineTo(-carWidth * 0.3, -carHeight * 0.4);
            ctx.lineTo(carWidth * 0.3, -carHeight * 0.4);
            ctx.lineTo(carWidth * 0.5, carHeight * 0.3);
            ctx.closePath();
            ctx.fill();
            
            // 霓虹边框
            ctx.strokeStyle = CONFIG.COLORS.neonCyan;
            ctx.lineWidth = 2 * scale;
            ctx.shadowColor = CONFIG.COLORS.neonCyan;
            ctx.shadowBlur = 15 * scale;
            ctx.stroke();
            
            // 驾驶舱
            ctx.fillStyle = 'rgba(0, 100, 150, 0.8)';
            ctx.beginPath();
            ctx.ellipse(0, -carHeight * 0.1, carWidth * 0.2, carHeight * 0.25, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // 车灯
            ctx.fillStyle = CONFIG.COLORS.neonYellow;
            ctx.shadowColor = CONFIG.COLORS.neonYellow;
            ctx.shadowBlur = 20 * scale;
            ctx.beginPath();
            ctx.arc(-carWidth * 0.25, -carHeight * 0.35, 4 * scale, 0, Math.PI * 2);
            ctx.arc(carWidth * 0.25, -carHeight * 0.35, 4 * scale, 0, Math.PI * 2);
            ctx.fill();
            
            // 尾灯
            if (this.speed > 0) {
                ctx.fillStyle = CONFIG.COLORS.neonPink;
                ctx.shadowColor = CONFIG.COLORS.neonPink;
                ctx.shadowBlur = 15 * scale;
                ctx.beginPath();
                ctx.arc(-carWidth * 0.35, carHeight * 0.2, 3 * scale, 0, Math.PI * 2);
                ctx.arc(carWidth * 0.35, carHeight * 0.2, 3 * scale, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // 氮气效果
            if (this.nitroActive) {
                ctx.fillStyle = CONFIG.COLORS.neonPurple;
                ctx.shadowColor = CONFIG.COLORS.neonPurple;
                ctx.shadowBlur = 30 * scale;
                ctx.beginPath();
                ctx.ellipse(0, carHeight * 0.5, carWidth * 0.15, carHeight * 0.4, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            
            ctx.restore();
        }
    }

    // ============================================
    // AI车辆类
    // ============================================
    class AICar {
        constructor(id, startZ, color, maxSpeed) {
            this.id = id;
            this.x = (Math.random() - 0.5) * CONFIG.ROAD_WIDTH * 0.6;
            this.z = startZ;
            this.y = 0;
            this.speed = 0;
            this.maxSpeed = maxSpeed;
            this.targetSpeed = maxSpeed * (0.7 + Math.random() * 0.3);
            this.color = color;
            this.steer = 0;
            this.targetLane = this.x;
            this.laneChangeTimer = Math.random() * AI_CONFIG.laneChangeInterval;
            this.width = 75;
            this.height = 38;
            this.driftAngle = 0;
            this.isColliding = false;
            this.collisionCooldown = 0;
            this.avoidingCollision = false;
            this.lastPlayerDistance = 0;
        }
        
        update(dt, track, player, otherAIs, particleSystem) {
            // 碰撞冷却
            if (this.collisionCooldown > 0) {
                this.collisionCooldown -= dt;
            }
            
            // 获取当前赛道段信息
            const segment = track.getSegment(this.z);
            
            // 基础跟随赛道
            let targetX = 0;
            if (segment) {
                // 跟随弯道
                const curveFactor = (segment.curve || 0) * 0.5;
                targetX = -curveFactor * CONFIG.ROAD_WIDTH * 0.3;
            }
            
            // 随机变道
            this.laneChangeTimer -= dt;
            if (this.laneChangeTimer <= 0 && !this.avoidingCollision) {
                this.laneChangeTimer = AI_CONFIG.laneChangeInterval + Math.random() * 2;
                if (Math.random() < AI_CONFIG.laneChangeChance) {
                    this.targetLane = (Math.random() - 0.5) * CONFIG.ROAD_WIDTH * 0.7;
                }
            }
            
            // 与玩家的距离检测
            const playerDistZ = player.z - this.z;
            const playerDist = Math.abs(playerDistZ);
            const playerDistX = Math.abs(player.x - this.x);
            
            // 避开玩家
            if (playerDist < AI_CONFIG.avoidDistance && playerDistX < 150) {
                this.avoidingCollision = true;
                if (player.x > this.x) {
                    targetX = this.x - 200;
                } else {
                    targetX = this.x + 200;
                }
                targetX = MathUtils.clamp(targetX, -CONFIG.ROAD_WIDTH * 0.4, CONFIG.ROAD_WIDTH * 0.4);
            } else {
                this.avoidingCollision = false;
                targetX = this.targetLane;
            }
            
            // 避开其他AI
            for (const other of otherAIs) {
                if (other.id === this.id) continue;
                
                const distZ = Math.abs(other.z - this.z);
                const distX = Math.abs(other.x - this.x);
                
                if (distZ < AI_CONFIG.avoidDistance * 0.7 && distX < 120) {
                    this.avoidingCollision = true;
                    if (other.x > this.x) {
                        targetX = this.x - 150;
                    } else {
                        targetX = this.x + 150;
                    }
                    targetX = MathUtils.clamp(targetX, -CONFIG.ROAD_WIDTH * 0.4, CONFIG.ROAD_WIDTH * 0.4);
                    break;
                }
            }
            
            // 平滑转向
            const steerStrength = 0.03;
            this.steer = (targetX - this.x) * steerStrength;
            this.steer = MathUtils.clamp(this.steer, -0.5, 0.5);
            
            // 应用转向
            this.x += this.steer * this.speed * 0.003 * dt * 60;
            this.x = MathUtils.clamp(this.x, -CONFIG.ROAD_WIDTH * 0.45, CONFIG.ROAD_WIDTH * 0.45);
            
            // 漂移角度
            this.driftAngle = MathUtils.lerp(this.driftAngle, this.steer * 0.4, 0.05);
            
            // 速度控制
            let speedAdjust = 1;
            if (this.avoidingCollision) {
                speedAdjust = 0.8;
            }
            if (Math.abs(this.steer) > 0.2) {
                speedAdjust *= 0.95;
            }
            
            // 加速/减速
            const currentTarget = this.targetSpeed * speedAdjust;
            if (this.speed < currentTarget) {
                this.speed += AI_CONFIG.acceleration * dt * 60;
            } else if (this.speed > currentTarget) {
                this.speed -= AI_CONFIG.deceleration * dt * 60;
            }
            
            this.speed = MathUtils.clamp(this.speed, 0, this.maxSpeed);
            
            // 更新位置
            this.z += this.speed * dt * 60;
            
            // 循环赛道
            const trackLength = track.length;
            while (this.z >= trackLength) {
                this.z -= trackLength;
            }
            while (this.z < 0) {
                this.z += trackLength;
            }
            
            // 获取Y位置
            if (segment) {
                const segmentProgress = (this.z % CONFIG.SEGMENT_LENGTH) / CONFIG.SEGMENT_LENGTH;
                const nextSegment = track.getSegment(this.z + CONFIG.SEGMENT_LENGTH);
                this.y = MathUtils.lerp(segment.y || 0, nextSegment?.y || 0, segmentProgress);
            }
        }
        
        applyCollision(otherX, otherZ) {
            if (this.collisionCooldown > 0) return;
            
            const dx = this.x - otherX;
            const dz = this.z - otherZ;
            const distance = Math.sqrt(dx * dx + dz * dz);
            
            if (distance < 0.01) return;
            
            // 归一化方向
            const nx = dx / distance;
            
            // 弹开
            this.x += nx * 40;
            this.x = MathUtils.clamp(this.x, -CONFIG.ROAD_WIDTH * 0.45, CONFIG.ROAD_WIDTH * 0.45);
            
            // 速度衰减
            this.speed *= 0.85;
            this.targetSpeed *= 0.95;
            
            this.collisionCooldown = 0.5;
            this.isColliding = true;
        }
        
        render(ctx, screenX, screenY, scale) {
            ctx.save();
            
            const carWidth = this.width * scale;
            const carHeight = this.height * scale;
            
            // 阴影
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
            ctx.beginPath();
            ctx.ellipse(screenX, screenY + carHeight * 0.3, carWidth * 0.7, carHeight * 0.25, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // 车身
            ctx.translate(screenX, screenY);
            ctx.rotate(this.driftAngle * 0.5);
            
            // 主体 - 根据颜色渲染不同AI
            const gradient = ctx.createLinearGradient(-carWidth/2, -carHeight/2, carWidth/2, carHeight/2);
            
            const baseColor = this.color;
            const darkColor = this.darkenColor(this.color, 0.5);
            const midColor = this.darkenColor(this.color, 0.75);
            
            gradient.addColorStop(0, baseColor);
            gradient.addColorStop(0.5, midColor);
            gradient.addColorStop(1, darkColor);
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.moveTo(-carWidth * 0.5, carHeight * 0.3);
            ctx.lineTo(-carWidth * 0.3, -carHeight * 0.4);
            ctx.lineTo(carWidth * 0.3, -carHeight * 0.4);
            ctx.lineTo(carWidth * 0.5, carHeight * 0.3);
            ctx.closePath();
            ctx.fill();
            
            // 霓虹边框
            ctx.strokeStyle = this.color;
            ctx.lineWidth = 2 * scale;
            ctx.shadowColor = this.color;
            ctx.shadowBlur = 12 * scale;
            ctx.stroke();
            
            // 驾驶舱
            ctx.fillStyle = 'rgba(0, 50, 80, 0.8)';
            ctx.shadowBlur = 0;
            ctx.beginPath();
            ctx.ellipse(0, -carHeight * 0.1, carWidth * 0.18, carHeight * 0.22, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // 车灯
            ctx.fillStyle = '#ffffff';
            ctx.shadowColor = '#ffffff';
            ctx.shadowBlur = 10 * scale;
            ctx.beginPath();
            ctx.arc(-carWidth * 0.22, -carHeight * 0.32, 3 * scale, 0, Math.PI * 2);
            ctx.arc(carWidth * 0.22, -carHeight * 0.32, 3 * scale, 0, Math.PI * 2);
            ctx.fill();
            
            // 尾灯
            ctx.fillStyle = '#ff4444';
            ctx.shadowColor = '#ff4444';
            ctx.shadowBlur = 8 * scale;
            ctx.beginPath();
            ctx.arc(-carWidth * 0.32, carHeight * 0.18, 2.5 * scale, 0, Math.PI * 2);
            ctx.arc(carWidth * 0.32, carHeight * 0.18, 2.5 * scale, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
        }
        
        darkenColor(hex, factor) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            
            const nr = Math.floor(r * factor);
            const ng = Math.floor(g * factor);
            const nb = Math.floor(b * factor);
            
            return `rgb(${nr}, ${ng}, ${nb})`;
        }
    }

    // ============================================
    // 碰撞检测系统
    // ============================================
    class CollisionSystem {
        constructor() {
            this.collisionDistance = AI_CONFIG.collisionRadius;
        }
        
        checkPlayerAI(player, aiCars, particleSystem, cameraShake) {
            for (const ai of aiCars) {
                // 计算相对Z距离（考虑循环赛道）
                let dz = Math.abs(player.z - ai.z);
                const dx = Math.abs(player.x - ai.x);
                
                // 检测碰撞
                if (dz < this.collisionDistance && dx < this.collisionDistance * 0.8) {
                    // 触发碰撞效果
                    player.applyCollision(ai.x, ai.z, true);
                    ai.applyCollision(player.x, player.z);
                    
                    // 视觉效果
                    cameraShake.trigger(8);
                    
                    // 碰撞火花
                    const screenX = CONFIG.CANVAS_WIDTH / 2 + (ai.x - player.x) * 0.3;
                    const screenY = CONFIG.CANVAS_HEIGHT - 150;
                    particleSystem.emitCollisionSparks(screenX, screenY);
                    
                    return true;
                }
            }
            return false;
        }
        
        checkAICollisions(aiCars, particleSystem) {
            for (let i = 0; i < aiCars.length; i++) {
                for (let j = i + 1; j < aiCars.length; j++) {
                    const ai1 = aiCars[i];
                    const ai2 = aiCars[j];
                    
                    let dz = Math.abs(ai1.z - ai2.z);
                    const dx = Math.abs(ai1.x - ai2.x);
                    
                    if (dz < this.collisionDistance * 0.7 && dx < this.collisionDistance * 0.6) {
                        ai1.applyCollision(ai2.x, ai2.z);
                        ai2.applyCollision(ai1.x, ai1.z);
                    }
                }
            }
        }
    }

    // ============================================
    // 渲染器
    // ============================================
    class Renderer {
        constructor(canvas, vfxCanvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.vfxCanvas = vfxCanvas;
            this.vfxCtx = vfxCanvas.getContext('2d');
            
            canvas.width = CONFIG.CANVAS_WIDTH;
            canvas.height = CONFIG.CANVAS_HEIGHT;
            vfxCanvas.width = CONFIG.CANVAS_WIDTH;
            vfxCanvas.height = CONFIG.CANVAS_HEIGHT;
        }
        
        clear() {
            this.ctx.fillStyle = CONFIG.COLORS.bgDark;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.vfxCtx.clearRect(0, 0, this.vfxCanvas.width, this.vfxCanvas.height);
        }
        
        renderSky(cameraY) {
            const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height * 0.5);
            gradient.addColorStop(0, CONFIG.COLORS.sky.top);
            gradient.addColorStop(1, CONFIG.COLORS.sky.bottom);
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height * 0.5);
            
            // 星星
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            for (let i = 0; i < 100; i++) {
                const x = (i * 137) % this.canvas.width;
                const y = (i * 73) % (this.canvas.height * 0.4);
                const size = (i % 3) + 1;
                this.ctx.beginPath();
                this.ctx.arc(x, y, size, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            // 地平线发光
            const horizonGlow = this.ctx.createLinearGradient(0, this.canvas.height * 0.4, 0, this.canvas.height * 0.55);
            horizonGlow.addColorStop(0, 'transparent');
            horizonGlow.addColorStop(0.5, CONFIG.COLORS.horizon);
            horizonGlow.addColorStop(1, 'transparent');
            this.ctx.fillStyle = horizonGlow;
            this.ctx.fillRect(0, this.canvas.height * 0.35, this.canvas.width, this.canvas.height * 0.2);
        }
        
        renderRoadSegment(segment, nextSegment, camera, index) {
            const ctx = this.ctx;
            const width = this.canvas.width;
            const height = this.canvas.height;
            
            // 投影点
            const p1 = MathUtils.project(
                { x: camera.x + segment.x, y: segment.y, z: segment.z },
                camera.x, camera.y + CONFIG.CAMERA_HEIGHT, camera.z,
                CONFIG.CAMERA_DEPTH, width, height, CONFIG.ROAD_WIDTH
            );
            
            const p2 = MathUtils.project(
                { x: camera.x + nextSegment.x, y: nextSegment.y, z: nextSegment.z },
                camera.x, camera.y + CONFIG.CAMERA_HEIGHT, camera.z,
                CONFIG.CAMERA_DEPTH, width, height, CONFIG.ROAD_WIDTH
            );
            
            if (p1.screen.scale <= 0 || p2.screen.scale <= 0) return;
            
            // 雾效
            const fog = MathUtils.exponentialFog(p1.camera.z / CONFIG.SEGMENT_LENGTH, 0.00015);
            
            // 颜色交替
            const isLight = Math.floor(segment.index / 3) % 2 === 0;
            
            // 草地
            const grassColor = isLight ? CONFIG.COLORS.grass.light : CONFIG.COLORS.grass.dark;
            ctx.fillStyle = this.applyFog(grassColor, fog);
            ctx.fillRect(0, p2.screen.y, width, p1.screen.y - p2.screen.y);
            
            // 路肩
            const rumbleColor = isLight ? CONFIG.COLORS.rumble.light : CONFIG.COLORS.rumble.dark;
            const rumbleW1 = p1.screen.w * 1.15;
            const rumbleW2 = p2.screen.w * 1.15;
            
            ctx.fillStyle = this.applyFog(rumbleColor, fog);
            ctx.beginPath();
            ctx.moveTo(p1.screen.x - rumbleW1, p1.screen.y);
            ctx.lineTo(p1.screen.x + rumbleW1, p1.screen.y);
            ctx.lineTo(p2.screen.x + rumbleW2, p2.screen.y);
            ctx.lineTo(p2.screen.x - rumbleW2, p2.screen.y);
            ctx.fill();
            
            // 道路
            const roadColor = isLight ? CONFIG.COLORS.asphalt.light : CONFIG.COLORS.asphalt.dark;
            ctx.fillStyle = this.applyFog(roadColor, fog);
            ctx.beginPath();
            ctx.moveTo(p1.screen.x - p1.screen.w, p1.screen.y);
            ctx.lineTo(p1.screen.x + p1.screen.w, p1.screen.y);
            ctx.lineTo(p2.screen.x + p2.screen.w, p2.screen.y);
            ctx.lineTo(p2.screen.x - p2.screen.w, p2.screen.y);
            ctx.fill();
            
            // 车道线
            if (isLight) {
                ctx.strokeStyle = this.applyFog(CONFIG.COLORS.lane, fog);
                ctx.lineWidth = 2;
                ctx.setLineDash([20, 30]);
                ctx.beginPath();
                ctx.moveTo(p1.screen.x, p1.screen.y);
                ctx.lineTo(p2.screen.x, p2.screen.y);
                ctx.stroke();
                ctx.setLineDash([]);
            }
            
            // 边线
            ctx.strokeStyle = this.applyFog(CONFIG.COLORS.roadLineGlow, fog);
            ctx.lineWidth = 3;
            ctx.shadowColor = CONFIG.COLORS.neonCyan;
            ctx.shadowBlur = 10 * fog;
            ctx.beginPath();
            ctx.moveTo(p1.screen.x - p1.screen.w * 0.95, p1.screen.y);
            ctx.lineTo(p2.screen.x - p2.screen.w * 0.95, p2.screen.y);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(p1.screen.x + p1.screen.w * 0.95, p1.screen.y);
            ctx.lineTo(p2.screen.x + p2.screen.w * 0.95, p2.screen.y);
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
        
        applyFog(color, fog) {
            if (fog >= 1) return color;
            // 简化雾效应用
            return color;
        }
        
        renderVehicle(vehicle, camera, isPlayer = false) {
            const p = MathUtils.project(
                { x: vehicle.x, y: vehicle.y, z: vehicle.z },
                camera.x, camera.y + CONFIG.CAMERA_HEIGHT, camera.z,
                CONFIG.CAMERA_DEPTH, this.canvas.width, this.canvas.height, CONFIG.ROAD_WIDTH
            );
            
            if (p.screen.scale <= 0 || p.camera.z < 0) return null;
            
            vehicle.render(this.ctx, p.screen.x, p.screen.y, p.screen.scale, isPlayer);
            
            return { screenY: p.screen.y, z: vehicle.z };
        }
    }

    // ============================================
    // 主游戏类
    // ============================================
    class Game {
        constructor() {
            this.canvas = document.getElementById('gameCanvas');
            this.vfxCanvas = document.getElementById('vfxCanvas');
            
            this.renderer = new Renderer(this.canvas, this.vfxCanvas);
            this.input = new InputManager();
            this.track = new TrackBuilder();
            this.particleSystem = new ParticleSystem();
            this.cameraShake = new CameraShake();
            this.collisionSystem = new CollisionSystem();
            
            this.track.build();
            
            this.player = new PlayerCar();
            this.aiCars = [];
            this.initAICars();
            
            this.camera = { x: 0, y: 0, z: 0 };
            
            this.lastTime = 0;
            this.frameCount = 0;
            this.fps = 60;
            this.frameTime = 0;
            
            this.collisionFlash = document.getElementById('collisionFlash');
            this.nitroOverlay = document.getElementById('nitroOverlay');
            
            this.updateHUD();
            this.gameLoop(0);
        }
        
        initAICars() {
            const colors = [
                CONFIG.COLORS.neonPink,
                CONFIG.COLORS.neonOrange,
                CONFIG.COLORS.neonGreen,
                CONFIG.COLORS.neonPurple
            ];
            
            const trackLength = this.track.length;
            
            for (let i = 0; i < AI_CONFIG.count; i++) {
                const startZ = (i + 1) * (trackLength / (AI_CONFIG.count + 2));
                const maxSpeed = MathUtils.randomRange(AI_CONFIG.minSpeed, AI_CONFIG.maxSpeed);
                
                const ai = new AICar(i, startZ, colors[i % colors.length], maxSpeed);
                this.aiCars.push(ai);
            }
        }
        
        gameLoop(timestamp) {
            const dt = Math.min((timestamp - this.lastTime) / 1000, 0.05);
            this.lastTime = timestamp;
            
            // FPS计算
            this.frameCount++;
            if (this.frameCount % 30 === 0) {
                this.fps = Math.round(1 / dt);
            }
            this.frameTime = (timestamp - this.lastTime + dt * 1000).toFixed(1);
            
            // 更新
            this.update(dt);
            
            // 渲染
            this.render();
            
            // HUD更新
            this.updateHUD();
            
            // 清除按键状态
            this.input.clearJustPressed();
            
            requestAnimationFrame((t) => this.gameLoop(t));
        }
        
        update(dt) {
            // 更新玩家
            this.player.update(dt, this.input, this.track, this.cameraShake, this.particleSystem);
            
            // 更新AI
            for (const ai of this.aiCars) {
                ai.update(dt, this.track, this.player, this.aiCars, this.particleSystem);
            }
            
            // 碰撞检测
            const playerCollided = this.collisionSystem.checkPlayerAI(this.player, this.aiCars, this.particleSystem, this.cameraShake);
            this.collisionSystem.checkAICollisions(this.aiCars, this.particleSystem);
            
            // 碰撞闪烁效果
            if (playerCollided) {
                this.collisionFlash.style.opacity = '1';
            } else {
                this.collisionFlash.style.opacity = '0';
            }
            
            // 更新相机震动
            this.cameraShake.update(dt);
            
            // 更新粒子
            this.particleSystem.update(dt);
            
            // 更新相机位置
            this.camera.z = this.player.z - 100;
            this.camera.x = this.player.x * 0.5;
            this.camera.y = this.player.y;
            
            // 氮气覆盖层
            this.nitroOverlay.style.opacity = this.player.nitroActive ? '0.3' : '0';
        }
        
        render() {
            this.renderer.clear();
            
            // 相机震动偏移
            const shakeX = this.cameraShake.offsetX;
            const shakeY = this.cameraShake.offsetY;
            
            this.renderer.ctx.save();
            this.renderer.ctx.translate(shakeX, shakeY);
            
            // 渲染天空
            this.renderer.renderSky(this.camera.y);
            
            // 渲染道路
            const baseSegment = Math.floor(this.camera.z / CONFIG.SEGMENT_LENGTH);
            const segments = this.track.segments;
            
            for (let n = 0; n < CONFIG.DRAW_DISTANCE; n++) {
                const index = (baseSegment + n) % segments.length;
                const segment = segments[index];
                const nextIndex = (index + 1) % segments.length;
                const nextSegment = segments[nextIndex];
                
                if (segment && nextSegment) {
                    this.renderer.renderRoadSegment(segment, nextSegment, this.camera, n);
                }
            }
            
            // 收集所有车辆用于排序
            const vehicles = [];
            
            // 添加AI车辆
            for (const ai of this.aiCars) {
                const relZ = ai.z - this.camera.z;
                if (relZ > -100 && relZ < CONFIG.DRAW_DISTANCE * CONFIG.SEGMENT_LENGTH) {
                    vehicles.push({ type: 'ai', vehicle: ai, z: ai.z });
                }
            }
            
            // 添加玩家车辆
            vehicles.push({ type: 'player', vehicle: this.player, z: this.player.z });
            
            // 按Z轴排序（远的先绘制）
            vehicles.sort((a, b) => b.z - a.z);
            
            // 渲染车辆
            for (const v of vehicles) {
                if (v.type === 'player') {
                    this.renderer.renderVehicle(v.vehicle, this.camera, true);
                } else {
                    this.renderer.renderVehicle(v.vehicle, this.camera, false);
                }
            }
            
            this.renderer.ctx.restore();
            
            // 渲染粒子（在震动效果之外）
            this.particleSystem.render(this.renderer.vfxCtx, this.camera);
        }
        
        updateHUD() {
            // 速度表
            const speedPercent = (this.player.speed / PLAYER_CONFIG.maxSpeed) * 100;
            document.getElementById('speedFill').style.width = speedPercent + '%';
            document.getElementById('speedText').textContent = Math.floor(this.player.speed);
            document.getElementById('gearIndicator').textContent = 'GEAR ' + PLAYER_CONFIG.gears[this.player.currentGear].name;
            
            // 氮气条
            const nitroPercent = (this.player.nitro / PLAYER_CONFIG.nitroMax) * 100;
            document.getElementById('nitroFill').style.width = nitroPercent + '%';
            
            // 性能面板
            document.getElementById('fpsValue').textContent = this.fps;
            document.getElementById('frameValue').textContent = this.frameTime + 'ms';
            document.getElementById('particleValue').textContent = this.particleSystem.count;
            document.getElementById('aiValue').textContent = this.aiCars.length;
            
            // 排名计算
            let position = 1;
            for (const ai of this.aiCars) {
                if (ai.z > this.player.z) {
                    position++;
                }
            }
            
            const suffixes = ['st', 'nd', 'rd', 'th'];
            const suffix = position <= 3 ? suffixes[position - 1] : 'th';
            document.getElementById('positionText').textContent = position;
            document.getElementById('positionSuffix').textContent = suffix;
        }
    }

    // 启动游戏
    window.onload = () => {
        new Game();
    };
</script>
</body>
</html>
```

## 实现说明

### AI对手车辆系统

1. **AICar 类**：
   - 每辆AI有独立的最大速度、颜色和起始位置
   - 实现简化的赛道跟随算法，根据赛道弯道调整方向
   - 随机变道行为：每隔一定时间有概率切换车道
   - 避障系统：检测前方玩家和其他AI，自动规避碰撞

2. **AI行为特点**：
   - `laneChangeTimer`：控制变道间隔
   - `targetLane`：目标车道位置
   - `avoidingCollision`：避让状态标志
   - 平滑转向过渡，不会突然变向

### 碰撞检测系统

1. **CollisionSystem 类**：
   - `checkPlayerAI()`：检测玩家与所有AI的碰撞
   - `checkAICollisions()`：检测AI之间的碰撞
   - 基于X轴和Z轴距离的碰撞判定

2. **碰撞效果**：
   - 位置弹开：碰撞双方互相推开
   - 速度衰减：碰撞后速度降低
   - 冷却时间：防止连续碰撞判定
   - 视觉反馈：镜头震动 + 碰撞火花粒子

### 渲染优化

1. **层级排序**：
   - 所有车辆按Z轴深度排序
   - 远处的车辆先绘制，实现正确的遮挡关系

2. **车辆阴影**：
   - 每辆车都有椭圆形阴影
   - 阴影位置在车身下方，增强立体感

3. **性能优化**：
   - 只渲染视距范围内的AI车辆
   - 粒子数量上限控制