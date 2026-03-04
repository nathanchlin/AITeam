# 游戏界面与Canvas渲染系统

**Time**: 2026-02-28T16:13:33.606998

---

好的，我来为你构建一个暗黑幻想风格的昆特牌战场Canvas渲染系统。这将是一个完整的单文件HTML，包含所有渲染逻辑、粒子系统、天气特效和交互功能。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>昆特牌 - 暗黑幻想战场</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #0a0a0f;
            overflow: hidden;
            font-family: 'Cinzel', 'Times New Roman', serif;
            color: #d4c4a8;
        }
        
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap');
        
        #gameContainer {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #gameCanvas {
            display: block;
            cursor: pointer;
        }
        
        #uiOverlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        
        .weather-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            pointer-events: all;
        }
        
        .weather-btn {
            padding: 10px 20px;
            background: linear-gradient(180deg, #2a2520 0%, #1a1815 100%);
            border: 1px solid #5a4a35;
            color: #c9a227;
            font-family: 'Cinzel', serif;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .weather-btn:hover {
            background: linear-gradient(180deg, #3a3530 0%, #2a2825 100%);
            border-color: #c9a227;
            box-shadow: 0 0 15px rgba(201, 162, 39, 0.3);
        }
        
        .weather-btn.active {
            background: linear-gradient(180deg, #4a3a25 0%, #3a2a15 100%);
            border-color: #c9a227;
            color: #f0d060;
        }
        
        .game-info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            font-size: 12px;
            color: #6a5a45;
            pointer-events: all;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <div id="uiOverlay">
            <div class="weather-controls">
                <button class="weather-btn active" data-weather="clear">晴天</button>
                <button class="weather-btn" data-weather="fog">迷雾</button>
                <button class="weather-btn" data-weather="rain">暴雨</button>
            </div>
            <div class="game-info">
                <p>鼠标悬停查看卡牌 | 点击选择 | 按空格键切换回合</p>
            </div>
        </div>
    </div>

    <script>
    (function() {
        'use strict';
        
        // ==================== 配置常量 ====================
        const CONFIG = {
            COLORS: {
                BG_PRIMARY: '#0d0d12',
                BG_SECONDARY: '#151520',
                GRID_LINE: '#2a2a35',
                GRID_HIGHLIGHT: '#3a3a45',
                GOLD_PRIMARY: '#c9a227',
                GOLD_LIGHT: '#f0d060',
                GOLD_DARK: '#8a7020',
                BLOOD_RED: '#8b0000',
                BLOOD_LIGHT: '#cc2020',
                STEEL_GRAY: '#4a5568',
                TEXT_PRIMARY: '#d4c4a8',
                TEXT_SECONDARY: '#8a7a65',
                CARD_BORDER: '#5a4a35',
                ENEMY_ZONE: '#1a1520',
                ALLY_ZONE: '#151a20'
            },
            CARD_WIDTH: 80,
            CARD_HEIGHT: 120,
            HAND_FAN_ANGLE: 0.4,
            HAND_FAN_RADIUS: 50
        };
        
        // ==================== 游戏状态 ====================
        const GameState = {
            weather: 'clear',
            particles: [],
            fogParticles: [],
            rainDrops: [],
            ashParticles: [],
            hoveredCard: null,
            selectedCard: null,
            mousePos: { x: 0, y: 0 },
            time: 0,
            roundNumber: 1,
            currentTurn: 'player',
            playerPassed: false,
            enemyPassed: false
        };
        
        // ==================== 卡牌数据 ====================
        const sampleCards = [
            { id: 1, name: '狂猎战士', power: 8, faction: 'MONSTERS', type: 'UNIT', row: 'MELEE' },
            { id: 2, name: '食尸鬼', power: 4, faction: 'MONSTERS', type: 'UNIT', row: 'MELEE' },
            { id: 3, name: '鹰身女妖', power: 6, faction: 'MONSTERS', type: 'UNIT', row: 'RANGED' },
            { id: 4, name: '巨魔', power: 10, faction: 'MONSTERS', type: 'UNIT', row: 'SIEGE' },
            { id: 5, name: '大狮鹫', power: 7, faction: 'MONSTERS', type: 'UNIT', row: 'MELEE' },
            { id: 6, name: '古老树精', power: 5, faction: 'MONSTERS', type: 'UNIT', row: 'RANGED' },
            { id: 7, name: '墓穴女巫', power: 3, faction: 'MONSTERS', type: 'UNIT', row: 'SIEGE' },
            { id: 8, name: '血魔', power: 12, faction: 'MONSTERS', type: 'UNIT', row: 'MELEE' },
            { id: 9, name: '瘟疫妖', power: 6, faction: 'MONSTERS', type: 'UNIT', row: 'RANGED' },
            { id: 10, name: '霜冻巨像', power: 9, faction: 'MONSTERS', type: 'UNIT', row: 'SIEGE' }
        ];
        
        // ==================== 战场布局数据 ====================
        const BoardLayout = {
            player: {
                melee: { cards: [], power: 0 },
                ranged: { cards: [], power: 0 },
                siege: { cards: [], power: 0 }
            },
            enemy: {
                melee: { cards: [], power: 0 },
                ranged: { cards: [], power: 0 },
                siege: { cards: [], power: 0 }
            },
            playerHand: [],
            enemyHand: [],
            playerDeck: 15,
            enemyDeck: 15,
            playerLeader: { name: '艾瑞汀', charges: 1 },
            enemyLeader: { name: '恩希尔', charges: 1 }
        };
        
        // 初始化手牌
        BoardLayout.playerHand = sampleCards.slice(0, 10).map((card, i) => ({
            ...card,
            handIndex: i,
            x: 0,
            y: 0,
            rotation: 0
        }));
        
        BoardLayout.enemyHand = sampleCards.slice(0, 7).map((card, i) => ({
            ...card,
            handIndex: i,
            faceDown: true
        }));
        
        // ==================== Canvas 初始化 ====================
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // ==================== 粒子系统 ====================
        class Particle {
            constructor(type) {
                this.type = type;
                this.reset();
            }
            
            reset() {
                this.x = Math.random() * canvas.width;
                this.y = -20;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = Math.random() * 2 + 1;
                this.size = Math.random() * 3 + 1;
                this.alpha = Math.random() * 0.5 + 0.3;
                this.life = 1;
                this.decay = Math.random() * 0.005 + 0.002;
                
                if (this.type === 'ash') {
                    this.color = `rgba(180, 160, 140, ${this.alpha})`;
                    this.vx = (Math.random() - 0.5) * 3;
                    this.vy = Math.random() * 1 + 0.5;
                    this.rotation = Math.random() * Math.PI * 2;
                    this.rotationSpeed = (Math.random() - 0.5) * 0.1;
                } else if (this.type === 'fog') {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.size = Math.random() * 100 + 50;
                    this.alpha = Math.random() * 0.15 + 0.05;
                    this.vx = (Math.random() - 0.5) * 0.5;
                    this.vy = (Math.random() - 0.5) * 0.2;
                    this.color = `rgba(60, 70, 90, ${this.alpha})`;
                } else if (this.type === 'rain') {
                    this.vx = -2;
                    this.vy = Math.random() * 15 + 10;
                    this.size = Math.random() * 2 + 1;
                    this.length = Math.random() * 20 + 10;
                    this.alpha = Math.random() * 0.4 + 0.2;
                } else if (this.type === 'ambient') {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.size = Math.random() * 2 + 0.5;
                    this.alpha = 0;
                    this.targetAlpha = Math.random() * 0.6 + 0.2;
                    this.pulse = Math.random() * Math.PI * 2;
                    this.color = Math.random() > 0.5 ? CONFIG.COLORS.GOLD_LIGHT : '#80a0c0';
                }
            }
            
            update() {
                if (this.type === 'fog') {
                    this.x += this.vx;
                    this.y += this.vy;
                    if (this.x < -this.size) this.x = canvas.width + this.size;
                    if (this.x > canvas.width + this.size) this.x = -this.size;
                    if (this.y < -this.size) this.y = canvas.height + this.size;
                    if (this.y > canvas.height + this.size) this.y = -this.size;
                } else if (this.type === 'ambient') {
                    this.pulse += 0.05;
                    this.alpha = (Math.sin(this.pulse) + 1) * 0.5 * this.targetAlpha;
                    this.y -= 0.2;
                    if (this.y < 0) {
                        this.y = canvas.height;
                        this.x = Math.random() * canvas.width;
                    }
                } else if (this.type === 'rain') {
                    this.x += this.vx;
                    this.y += this.vy;
                    if (this.y > canvas.height) {
                        this.reset();
                    }
                } else {
                    this.x += this.vx;
                    this.y += this.vy;
                    this.life -= this.decay;
                    if (this.type === 'ash') {
                        this.rotation += this.rotationSpeed;
                        this.x += Math.sin(this.y * 0.02) * 0.5;
                    }
                    if (this.life <= 0 || this.y > canvas.height + 20) {
                        this.reset();
                    }
                }
            }
            
            draw(ctx) {
                ctx.save();
                
                if (this.type === 'fog') {
                    const gradient = ctx.createRadialGradient(
                        this.x, this.y, 0,
                        this.x, this.y, this.size
                    );
                    gradient.addColorStop(0, `rgba(50, 60, 80, ${this.alpha})`);
                    gradient.addColorStop(1, 'rgba(50, 60, 80, 0)');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                } else if (this.type === 'rain') {
                    ctx.strokeStyle = `rgba(150, 170, 200, ${this.alpha})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.lineTo(this.x + this.vx * 2, this.y + this.length);
                    ctx.stroke();
                } else if (this.type === 'ash') {
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.rotation);
                    ctx.fillStyle = `rgba(180, 160, 140, ${this.life * this.alpha})`;
                    ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 0.6);
                } else if (this.type === 'ambient') {
                    ctx.globalAlpha = this.alpha;
                    ctx.fillStyle = this.color;
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                }
                
                ctx.restore();
            }
        }
        
        // 初始化粒子
        function initParticles() {
            GameState.particles = [];
            GameState.fogParticles = [];
            GameState.rainDrops = [];
            GameState.ashParticles = [];
            
            // 环境粒子（始终存在）
            for (let i = 0; i < 50; i++) {
                GameState.particles.push(new Particle('ambient'));
            }
            
            // 雾粒子
            for (let i = 0; i < 20; i++) {
                GameState.fogParticles.push(new Particle('fog'));
            }
            
            // 雨粒子
            for (let i = 0; i < 100; i++) {
                const p = new Particle('rain');
                p.y = Math.random() * canvas.height;
                GameState.rainDrops.push(p);
            }
            
            // 灰烬粒子
            for (let i = 0; i < 30; i++) {
                const p = new Particle('ash');
                p.y = Math.random() * canvas.height;
                GameState.ashParticles.push(p);
            }
        }
        
        // ==================== 渲染函数 ====================
        
        // 绘制背景
        function drawBackground() {
            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            gradient.addColorStop(0, '#0a0a12');
            gradient.addColorStop(0.5, '#0d0d18');
            gradient.addColorStop(1, '#08080c');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 暗黑幻想氛围纹理
            drawAtmosphereTexture();
        }
        
        function drawAtmosphereTexture() {
            ctx.save();
            ctx.globalAlpha = 0.03;
            
            // 绘制不规则的暗纹
            for (let i = 0; i < 5; i++) {
                const x = (Math.sin(GameState.time * 0.0003 + i) + 1) * canvas.width / 2;
                const y = (Math.cos(GameState.time * 0.0002 + i * 2) + 1) * canvas.height / 2;
                const radius = Math.max(100, 200 + Math.sin(GameState.time * 0.001 + i) * 50);
                
                const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
                gradient.addColorStop(0, '#c9a227');
                gradient.addColorStop(1, 'rgba(201, 162, 39, 0)');
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
            
            ctx.restore();
        }
        
        // 绘制战场格子
        function drawBattlefield() {
            const centerX = canvas.width / 2;
            const rowHeight = 90;
            const rowWidth = canvas.width * 0.6;
            const startX = centerX - rowWidth / 2;
            const centerY = canvas.height / 2;
            
            // 敌方区域 (上方)
            drawBattlefieldZone(startX, centerY - 200, rowWidth, 3, true);
            
            // 我方区域 (下方)
            drawBattlefieldZone(startX, centerY + 40, rowWidth, 3, false);
            
            // 中线装饰
            drawCenterLine(centerX, centerY - 30, rowWidth);
        }
        
        function drawBattlefieldZone(x, y, width, rows, isEnemy) {
            const rowHeight = 75;
            
            for (let i = 0; i < rows; i++) {
                const rowY = y + i * rowHeight;
                const rowName = isEnemy ? ['近战', '远程', '攻城'][i] : ['攻城', '远程', '近战'][i];
                const rowKey = isEnemy ? ['melee', 'ranged', 'siege'][i] : ['siege', 'ranged', 'melee'][i];
                
                // 行背景
                ctx.save();
                
                const bgGradient = ctx.createLinearGradient(x, rowY, x, rowY + rowHeight);
                if (isEnemy) {
                    bgGradient.addColorStop(0, 'rgba(40, 20, 25, 0.6)');
                    bgGradient.addColorStop(1, 'rgba(30, 15, 20, 0.4)');
                } else {
                    bgGradient.addColorStop(0, 'rgba(20, 30, 40, 0.4)');
                    bgGradient.addColorStop(1, 'rgba(25, 35, 45, 0.6)');
                }
                
                ctx.fillStyle = bgGradient;
                ctx.fillRect(x, rowY, width, rowHeight - 2);
                
                // 行边框
                ctx.strokeStyle = isEnemy ? 'rgba(139, 0, 0, 0.3)' : 'rgba(74, 85, 104, 0.3)';
                ctx.lineWidth = 1;
                ctx.strokeRect(x, rowY, width, rowHeight - 2);
                
                // 行名称
                ctx.fillStyle = CONFIG.COLORS.TEXT_SECONDARY;
                ctx.font = '11px Cinzel, serif';
                ctx.fillText(rowName, x + 8, rowY + 14);
                
                // 绘制该行的卡牌
                const zone = isEnemy ? BoardLayout.enemy[rowKey] : BoardLayout.player[rowKey];
                drawCardsInRow(zone.cards, x + 50, rowY + 5, width - 60, rowHeight - 10, isEnemy);
                
                // 行战力
                if (zone.cards.length > 0) {
                    const power = zone.cards.reduce((sum, c) => sum + c.power, 0);
                    drawRowPower(x + width - 45, rowY + rowHeight / 2, power, isEnemy);
                }
                
                ctx.restore();
            }
        }
        
        function drawCardsInRow(cards, startX, startY, width, height, isEnemy) {
            const cardW = 60;
            const cardH = height - 10;
            const gap = 5;
            const totalWidth = cards.length * (cardW + gap) - gap;
            let offsetX = startX + (width - totalWidth) / 2;
            
            cards.forEach((card, i) => {
                drawMiniCard(offsetX + i * (cardW + gap), startY + 5, cardW, cardH, card, isEnemy);
            });
        }
        
        function drawMiniCard(x, y, w, h, card, isEnemy) {
            ctx.save();
            
            // 卡牌背景
            const gradient = ctx.createLinearGradient(x, y, x, y + h);
            gradient.addColorStop(0, '#2a2520');
            gradient.addColorStop(1, '#1a1815');
            ctx.fillStyle = gradient;
            
            // 圆角矩形
            roundRect(ctx, x, y, w, h, 4);
            ctx.fill();
            
            // 边框
            ctx.strokeStyle = card.color === 'GOLD' ? CONFIG.COLORS.GOLD_PRIMARY : '#5a4a35';
            ctx.lineWidth = 1;
            roundRect(ctx, x, y, w, h, 4);
            ctx.stroke();
            
            // 战力数字
            ctx.fillStyle = CONFIG.COLORS.GOLD_LIGHT;
            ctx.font = 'bold 16px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.fillText(card.power, x + w / 2, y + h / 2 + 6);
            
            ctx.restore();
        }
        
        function drawRowPower(x, y, power, isEnemy) {
            ctx.save();
            
            // 战力背景圆
            ctx.beginPath();
            ctx.arc(x, y, 18, 0, Math.PI * 2);
            ctx.fillStyle = isEnemy ? 'rgba(139, 0, 0, 0.4)' : 'rgba(201, 162, 39, 0.2)';
            ctx.fill();
            ctx.strokeStyle = isEnemy ? CONFIG.COLORS.BLOOD_RED : CONFIG.COLORS.GOLD_PRIMARY;
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // 战力数字
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 14px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(power, x, y);
            
            ctx.restore();
        }
        
        function drawCenterLine(x, y, width) {
            ctx.save();
            
            // 分隔线
            const startX = x - width / 2;
            const endX = x + width / 2;
            
            ctx.strokeStyle = 'rgba(201, 162, 39, 0.3)';
            ctx.lineWidth = 2;
            ctx.setLineDash([10, 10]);
            ctx.beginPath();
            ctx.moveTo(startX, y);
            ctx.lineTo(endX, y);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // 中央装饰
            ctx.fillStyle = CONFIG.COLORS.GOLD_PRIMARY;
            ctx.font = '16px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.fillText('VS', x, y + 5);
            
            ctx.restore();
        }
        
        // 绘制手牌区（扇形展开）
        function drawHandArea() {
            const handY = canvas.height - 140;
            const centerX = canvas.width / 2;
            const cards = BoardLayout.playerHand;
            const cardCount = cards.length;
            
            if (cardCount === 0) return;
            
            const fanAngle = CONFIG.HAND_FAN_ANGLE;
            const totalAngle = fanAngle * (cardCount - 1);
            const startAngle = Math.PI / 2 - totalAngle / 2;
            
            cards.forEach((card, i) => {
                const angle = startAngle + fanAngle * i - Math.PI / 2;
                const fanRadius = 100 + Math.abs(i - (cardCount - 1) / 2) * 20;
                
                const x = centerX + Math.cos(angle + Math.PI / 2) * (i - (cardCount - 1) / 2) * 70;
                const y = handY + Math.abs(Math.sin(angle)) * 30;
                const rotation = angle * 0.3;
                
                card.x = x;
                card.y = y;
                card.rotation = rotation;
                
                const isHovered = GameState.hoveredCard === card;
                const isSelected = GameState.selectedCard === card;
                
                drawCard(x, y - (isHovered ? 30 : 0) - (isSelected ? 20 : 0), 
                         CONFIG.CARD_WIDTH, CONFIG.CARD_HEIGHT, card, rotation, isHovered || isSelected);
            });
        }
        
        function drawCard(x, y, w, h, card, rotation, highlighted) {
            ctx.save();
            ctx.translate(x + w / 2, y + h / 2);
            ctx.rotate(rotation);
            ctx.translate(-w / 2, -h / 2);
            
            // 发光效果
            if (highlighted) {
                ctx.shadowBlur = 20;
                ctx.shadowColor = CONFIG.COLORS.GOLD_PRIMARY;
            }
            
            // 卡牌主体
            const gradient = ctx.createLinearGradient(0, 0, 0, h);
            gradient.addColorStop(0, '#3a3530');
            gradient.addColorStop(0.3, '#2a2520');
            gradient.addColorStop(1, '#1a1510');
            ctx.fillStyle = gradient;
            roundRect(ctx, 0, 0, w, h, 6);
            ctx.fill();
            
            // 卡牌边框
            const borderColor = highlighted ? CONFIG.COLORS.GOLD_LIGHT : CONFIG.COLORS.CARD_BORDER;
            ctx.strokeStyle = borderColor;
            ctx.lineWidth = highlighted ? 2 : 1;
            roundRect(ctx, 0, 0, w, h, 6);
            ctx.stroke();
            
            // 卡牌图像区域
            ctx.fillStyle = '#1a1510';
            ctx.fillRect(5, 5, w - 10, h * 0.5);
            
            // 模拟卡牌图案
            drawCardArt(5, 5, w - 10, h * 0.5, card);
            
            // 卡牌名称
            ctx.fillStyle = CONFIG.COLORS.TEXT_PRIMARY;
            ctx.font = '10px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.fillText(card.name, w / 2, h * 0.65);
            
            // 战力框
            ctx.fillStyle = '#1a1510';
            roundRect(ctx, w / 2 - 15, h - 25, 30, 20, 3);
            ctx.fill();
            ctx.strokeStyle = CONFIG.COLORS.GOLD_PRIMARY;
            ctx.lineWidth = 1;
            roundRect(ctx, w / 2 - 15, h - 25, 30, 20, 3);
            ctx.stroke();
            
            // 战力数字
            ctx.fillStyle = CONFIG.COLORS.GOLD_LIGHT;
            ctx.font = 'bold 14px Cinzel, serif';
            ctx.fillText(card.power, w / 2, h - 10);
            
            ctx.restore();
        }
        
        function drawCardArt(x, y, w, h, card) {
            ctx.save();
            ctx.beginPath();
            ctx.rect(x, y, w, h);
            ctx.clip();
            
            // 根据阵营绘制不同的图案
            const faction = card.faction;
            
            if (faction === 'MONSTERS') {
                // 怪物风格的暗色调
                const gradient = ctx.createRadialGradient(x + w/2, y + h/2, 0, x + w/2, y + h/2, w);
                gradient.addColorStop(0, '#3a2525');
                gradient.addColorStop(1, '#1a1010');
                ctx.fillStyle = gradient;
                ctx.fillRect(x, y, w, h);
                
                // 绘制简单的怪物轮廓
                ctx.strokeStyle = 'rgba(139, 0, 0, 0.5)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(x + w/2, y + h/2, w * 0.3, 0, Math.PI * 2);
                ctx.stroke();
            }
            
            ctx.restore();
        }
        
        // 绘制牌库区
        function drawDeckAreas() {
            // 玩家牌库（左下）
            drawDeck(50, canvas.height - 200, BoardLayout.playerDeck, false);
            
            // 敌方牌库（左上）
            drawDeck(50, 80, BoardLayout.enemyDeck, true);
        }
        
        function drawDeck(x, y, count, isEnemy) {
            ctx.save();
            
            const w = 60;
            const h = 85;
            const stackOffset = 2;
            const stackCount = Math.min(5, count);
            
            // 绘制堆叠效果
            for (let i = 0; i < stackCount; i++) {
                const offsetY = -i * stackOffset;
                
                ctx.fillStyle = i === stackCount - 1 ? '#2a2520' : '#1a1815';
                roundRect(ctx, x, y + offsetY, w, h, 4);
                ctx.fill();
                ctx.strokeStyle = '#3a3530';
                ctx.lineWidth = 1;
                roundRect(ctx, x, y + offsetY, w, h, 4);
                ctx.stroke();
            }
            
            // 牌库图标
            ctx.fillStyle = CONFIG.COLORS.TEXT_SECONDARY;
            ctx.font = '20px serif';
            ctx.textAlign = 'center';
            ctx.fillText('☴', x + w / 2, y - stackCount * stackOffset + h / 2);
            
            // 剩余数量
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px Cinzel, serif';
            ctx.fillText(count, x + w / 2, y - stackCount * stackOffset + h - 10);
            
            // 标签
            ctx.fillStyle = CONFIG.COLORS.TEXT_SECONDARY;
            ctx.font = '10px Cinzel, serif';
            ctx.fillText(isEnemy ? '敌方牌库' : '我方牌库', x + w / 2, y + h + 15);
            
            ctx.restore();
        }
        
        // 绘制领袖技能区
        function drawLeaderAreas() {
            // 玩家领袖（右下）
            drawLeader(canvas.width - 120, canvas.height - 200, BoardLayout.playerLeader, false);
            
            // 敌方领袖（右上）
            drawLeader(canvas.width - 120, 80, BoardLayout.enemyLeader, true);
        }
        
        function drawLeader(x, y, leader, isEnemy) {
            ctx.save();
            
            const w = 80;
            const h = 100;
            
            // 背景框
            const gradient = ctx.createLinearGradient(x, y, x, y + h);
            gradient.addColorStop(0, '#3a3025');
            gradient.addColorStop(1, '#252015');
            ctx.fillStyle = gradient;
            roundRect(ctx, x, y, w, h, 6);
            ctx.fill();
            
            // 金色边框
            ctx.strokeStyle = CONFIG.COLORS.GOLD_PRIMARY;
            ctx.lineWidth = 2;
            roundRect(ctx, x, y, w, h, 6);
            ctx.stroke();
            
            // 领袖图标区域
            ctx.fillStyle = '#1a1510';
            ctx.fillRect(x + 5, y + 5, w - 10, h - 35);
            
            // 绘制皇冠图标
            ctx.fillStyle = CONFIG.COLORS.GOLD_PRIMARY;
            ctx.font = '30px serif';
            ctx.textAlign = 'center';
            ctx.fillText('♔', x + w / 2, y + 45);
            
            // 领袖名称
            ctx.fillStyle = CONFIG.COLORS.TEXT_PRIMARY;
            ctx.font = '11px Cinzel, serif';
            ctx.fillText(leader.name, x + w / 2, y + h - 18);
            
            // 技能次数
            ctx.fillStyle = leader.charges > 0 ? CONFIG.COLORS.GOLD_LIGHT : CONFIG.COLORS.TEXT_SECONDARY;
            ctx.font = 'bold 10px Cinzel, serif';
            ctx.fillText(`技能: ${leader.charges}`, x + w / 2, y + h - 5);
            
            ctx.restore();
        }
        
        // 绘制战力计分板
        function drawScoreBoard() {
            const centerX = canvas.width / 2;
            
            // 计算总战力
            const playerPower = calculateTotalPower(BoardLayout.player);
            const enemyPower = calculateTotalPower(BoardLayout.enemy);
            
            // 敌方战力（上方）
            drawPowerScore(centerX, 50, enemyPower, true);
            
            // 我方战力（下方）
            drawPowerScore(centerX, canvas.height - 50, playerPower, false);
            
            // 回合数显示
            drawRoundIndicator(centerX, 90);
        }
        
        function calculateTotalPower(zones) {
            return Object.values(zones).reduce((sum, zone) => {
                return sum + zone.cards.reduce((s, c) => s + c.power, 0);
            }, 0);
        }
        
        function drawPowerScore(x, y, power, isEnemy) {
            ctx.save();
            
            // 战力背景
            const width = 150;
            const height = 40;
            
            ctx.fillStyle = 'rgba(10, 10, 15, 0.8)';
            roundRect(ctx, x - width / 2, y - height / 2, width, height, 8);
            ctx.fill();
            
            ctx.strokeStyle = isEnemy ? 'rgba(139, 0, 0, 0.6)' : 'rgba(201, 162, 39, 0.6)';
            ctx.lineWidth = 2;
            roundRect(ctx, x - width / 2, y - height / 2, width, height, 8);
            ctx.stroke();
            
            // 战力数字
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 24px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(power, x, y);
            
            // 标签
            ctx.fillStyle = CONFIG.COLORS.TEXT_SECONDARY;
            ctx.font = '10px Cinzel, serif';
            ctx.fillText(isEnemy ? '敌方战力' : '我方战力', x, y - height / 2 - 10);
            
            ctx.restore();
        }
        
        function drawRoundIndicator(x, y) {
            ctx.save();
            
            ctx.fillStyle = CONFIG.COLORS.TEXT_SECONDARY;
            ctx.font = '12px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.fillText(`第 ${GameState.roundNumber} 回合`, x, y);
            
            // 回合胜利标记
            const wins = [0, 0]; // [玩家胜场, 敌方胜场]
            const gemY = y + 20;
            
            // 玩家宝石
            for (let i = 0; i < 2; i++) {
                ctx.beginPath();
                ctx.arc(x - 30 + i * 20, gemY, 6, 0, Math.PI * 2);
                ctx.fillStyle = i < wins[0] ? CONFIG.COLORS.GOLD_PRIMARY : 'rgba(90, 74, 53, 0.5)';
                ctx.fill();
            }
            
            // 敌方宝石
            for (let i = 0; i < 2; i++) {
                ctx.beginPath();
                ctx.arc(x + 30 + i * 20, gemY, 6, 0, Math.PI * 2);
                ctx.fillStyle = i < wins[1] ? CONFIG.COLORS.BLOOD_RED : 'rgba(90, 74, 53, 0.5)';
                ctx.fill();
            }
            
            ctx.restore();
        }
        
        // 绘制敌方手牌（背面）
        function drawEnemyHand() {
            const handY = 30;
            const centerX = canvas.width / 2;
            const cards = BoardLayout.enemyHand;
            const cardCount = cards.length;
            
            if (cardCount === 0) return;
            
            const cardW = 50;
            const gap = 10;
            const totalWidth = cardCount * cardW + (cardCount - 1) * gap;
            const startX = centerX - totalWidth / 2;
            
            cards.forEach((card, i) => {
                const x = startX + i * (cardW + gap);
                drawCardBack(x, handY, cardW, 70);
            });
        }
        
        function drawCardBack(x, y, w, h) {
            ctx.save();
            
            const gradient = ctx.createLinearGradient(x, y, x, y + h);
            gradient.addColorStop(0, '#2a2530');
            gradient.addColorStop(1, '#1a1520');
            ctx.fillStyle = gradient;
            roundRect(ctx, x, y, w, h, 4);
            ctx.fill();
            
            ctx.strokeStyle = '#4a3545';
            ctx.lineWidth = 1;
            roundRect(ctx, x, y, w, h, 4);
            ctx.stroke();
            
            // 卡背图案
            ctx.fillStyle = '#3a2535';
            ctx.beginPath();
            ctx.arc(x + w / 2, y + h / 2, w * 0.25, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.restore();
        }
        
        // 绘制天气效果
        function drawWeatherEffects() {
            if (GameState.weather === 'fog') {
                GameState.fogParticles.forEach(p => {
                    p.update();
                    p.draw(ctx);
                });
            } else if (GameState.weather === 'rain') {
                GameState.rainDrops.forEach(p => {
                    p.update();
                    p.draw(ctx);
                });
                
                // 雨天氛围
                ctx.fillStyle = 'rgba(40, 50, 70, 0.2)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
            
            // 环境粒子
            GameState.particles.forEach(p => {
                p.update();
                p.draw(ctx);
            });
            
            // 晴天时有金色光晕
            if (GameState.weather === 'clear') {
                const gradient = ctx.createRadialGradient(
                    canvas.width * 0.8, canvas.height * 0.1, 0,
                    canvas.width * 0.8, canvas.height * 0.1, 400
                );
                gradient.addColorStop(0, 'rgba(201, 162, 39, 0.1)');
                gradient.addColorStop(1, 'rgba(201, 162, 39, 0)');
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
        }
        
        // 绘制放弃按钮
        function drawPassButton() {
            const x = canvas.width - 60;
            const y = canvas.height / 2;
            
            ctx.save();
          
            const isHovered = Math.abs(GameState.mousePos.x - x) < 40 && 
                             Math.abs(GameState.mousePos.y - y) < 25;
            
            // 按钮背景
            ctx.fillStyle = isHovered ? 'rgba(60, 50, 40, 0.9)' : 'rgba(40, 35, 30, 0.9)';
            roundRect(ctx, x - 40, y - 25, 80, 50, 8);
            ctx.fill();
            
            ctx.strokeStyle = isHovered ? CONFIG.COLORS.GOLD_LIGHT : CONFIG.COLORS.GOLD_DARK;
            ctx.lineWidth = 2;
            roundRect(ctx, x - 40, y - 25, 80, 50, 8);
            ctx.stroke();
            
            // 按钮文字
            ctx.fillStyle = isHovered ? CONFIG.COLORS.GOLD_LIGHT : CONFIG.COLORS.TEXT_PRIMARY;
            ctx.font = 'bold 14px Cinzel, serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('放弃', x, y);
            
            ctx.restore();
        }
        
        // 辅助函数：绘制圆角矩形
        function roundRect(ctx, x, y, w, h, r) {
            ctx.beginPath();
            ctx.moveTo(x + r, y);
            ctx.lineTo(x + w - r, y);
            ctx.quadraticCurveTo(x + w, y, x + w, y + r);
            ctx.lineTo(x + w, y + h - r);
            ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
            ctx.lineTo(x + r, y + h);
            ctx.quadraticCurveTo(x, y + h, x, y + h - r);
            ctx.lineTo(x, y + r);
            ctx.quadraticCurveTo(x, y, x + r, y);
            ctx.closePath();
        }
        
        // ==================== 主渲染循环 ====================
        function render(timestamp) {
            GameState.time = timestamp;
            
            // 清空画布
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 绘制各层
            drawBackground();
            drawWeatherEffects();
            drawBattlefield();
            drawDeckAreas();
            drawLeaderAreas();
            drawEnemyHand();
            drawHandArea();
            drawScoreBoard();
            drawPassButton();
            
            requestAnimationFrame(render);
        }
        
        // ==================== 交互处理 ====================
        function handleMouseMove(e) {
            const rect = canvas.getBoundingClientRect();
            GameState.mousePos.x = e.clientX - rect.left;
            GameState.mousePos.y = e.clientY - rect.top;
            
            // 检测手牌悬停
            GameState.hoveredCard = null;
            BoardLayout.playerHand.forEach(card => {
                if (GameState.mousePos.x > card.x && 
                    GameState.mousePos.x < card.x + CONFIG.CARD_WIDTH &&
                    GameState.mousePos.y > card.y - 30 && 
                    GameState.mousePos.y < card.y + CONFIG.CARD_HEIGHT - 30) {
                    GameState.hoveredCard = card;
                }
            });
        }
        
        function handleClick(e) {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // 点击手牌
            if (GameState.hoveredCard) {
                if (GameState.selectedCard === GameState.hoveredCard) {
                    // 再次点击选中的牌，尝试打出
                    playCard(GameState.selectedCard);
                    GameState.selectedCard = null;
                } else {
                    GameState.selectedCard = GameState.hoveredCard;
                }
            } else {
                GameState.selectedCard = null;
            }
            
            // 点击放弃按钮
            if (Math.abs(x - (canvas.width - 60)) < 40 && 
                Math.abs(y - canvas.height / 2) < 25) {
                togglePass();
            }
        }
        
        function playCard(card) {
            // 根据卡牌类型决定放置位置
            const rowKey = card.row.toLowerCase();
            const targetRow = BoardLayout.player[rowKey];
            
            if (targetRow) {
                // 从手牌移除
                const index = BoardLayout.playerHand.indexOf(card);
                if (index > -1) {
                    BoardLayout.playerHand.splice(index, 1);
                }
                
                // 添加到战场
                targetRow.cards.push(card);
                
                // 重新索引手牌
                BoardLayout.playerHand.forEach((c, i) => c.handIndex = i);
            }
        }
        
        function togglePass() {
            GameState.playerPassed = !GameState.playerPassed;
            if (GameState.playerPassed) {
                console.log('玩家已放弃本回合');
            }
        }
        
        function handleKeyPress(e) {
            if (e.code === 'Space') {
                // 切换回合（用于测试）
                GameState.roundNumber = (GameState.roundNumber % 3) + 1;
                console.log(`切换到第 ${GameState.roundNumber} 回合`);
            }
        }
        
        // ==================== 天气控制 ====================
        function initWeatherControls() {
            const buttons = document.querySelectorAll('.weather-btn');
            buttons.forEach(btn => {
                btn.addEventListener('click', () => {
                    buttons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    GameState.weather = btn.dataset.weather;
                });
            });
        }
        
        // ==================== 初始化 ====================
        function init() {
            initParticles();
            initWeatherControls();
            
            canvas.addEventListener('mousemove', handleMouseMove);
            canvas.addEventListener('click', handleClick);
            document.addEventListener('keypress', handleKeyPress);
            
            requestAnimationFrame(render);
        }
        
        // 页面加载完成后初始化
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    })();
    </script>
</body>
</html>
```

## 设计说明

### 视觉风格
- **暗黑幻想配色**：以深灰黑(#0d0d12)为主背景，配合暗金(#c9a227)和血红(#8b0000)作为阵营区分色
- **层次感**：战场格子使用半透明渐变，敌方区域偏红、我方区域偏蓝
- **金色点缀**：所有交互元素都用金色高亮，增强高级感

### 布局结构
1. **战场区**：中央60%宽度，双方各3行（近战/远程/攻城）
2. **手牌区**：底部扇形展开，悬停时上浮+高亮
3. **牌库区**：左右两侧，带堆叠效果显示剩余数量
4. **领袖技能区**：右侧，显示技能可用次数
5. **战力计分板**：顶部中央，实时显示双方总战力

### 天气系统
- **晴天**：金色光晕从右上角洒下，环境粒子发光
- **迷雾**：大范围半透明云雾粒子缓慢飘动
- **暴雨**：倾斜雨滴+蓝灰色氛围滤镜

### 交互功能
- 鼠标悬停手牌会上浮并显示金色边框
- 点击选中卡牌（可再次点击打出）
- 点击"放弃"按钮放弃本回合
- 按空格键测试切换回合
- 右上角按钮切换天气效果

所有粒子效果都经过性能优化，使用对象池复用，不会造成内存泄漏。