# UI界面与视觉 polish

**Time**: 2026-03-01T18:46:23.187899

---

我来为你完成UI界面与视觉polish任务。这将包括完整的菜单系统、动画效果、拖尾特效和卡通风格的视觉呈现。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Angry Birds - Complete Game</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent: #FF6B35;
            --accent-secondary: #4ECDC4;
            --accent-glow: rgba(255, 107, 53, 0.4);
            --text: #ffffff;
            --text-muted: #8892a0;
            --success: #7ED321;
            --warning: #F5A623;
            --danger: #E94560;
        }

        @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Nunito', system-ui, sans-serif;
            overflow: hidden;
        }

        .game-container {
            position: relative;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 
                0 0 80px rgba(255, 107, 53, 0.3),
                0 25px 80px rgba(0, 0, 0, 0.4),
                inset 0 0 0 3px rgba(255,255,255,0.1);
        }

        canvas {
            display: block;
            cursor: crosshair;
        }

        /* ===== UI Overlay ===== */
        .ui-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            z-index: 100;
        }

        /* ===== Main Menu ===== */
        .main-menu {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            pointer-events: auto;
            z-index: 200;
        }

        .main-menu.hidden {
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s ease;
        }

        .game-title {
            font-family: 'Fredoka One', cursive;
            font-size: 72px;
            color: #fff;
            text-shadow: 
                0 4px 0 #E94560,
                0 8px 0 #c73e54,
                0 12px 20px rgba(0,0,0,0.3);
            margin-bottom: 10px;
            animation: titleBounce 2s ease-in-out infinite;
        }

        .game-title span {
            color: #FFD93D;
        }

        @keyframes titleBounce {
            0%, 100% { transform: translateY(0) rotate(-2deg); }
            50% { transform: translateY(-15px) rotate(2deg); }
        }

        .subtitle {
            font-size: 18px;
            color: rgba(255,255,255,0.8);
            margin-bottom: 50px;
            letter-spacing: 3px;
        }

        .menu-buttons {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .menu-btn {
            padding: 18px 60px;
            font-family: 'Fredoka One', cursive;
            font-size: 22px;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            position: relative;
            overflow: hidden;
        }

        .menu-btn.primary {
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: #fff;
            box-shadow: 
                0 6px 0 #c45a2a,
                0 10px 30px rgba(255, 107, 53, 0.4);
        }

        .menu-btn.secondary {
            background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
            color: #fff;
            box-shadow: 
                0 6px 0 #3aa89e,
                0 10px 30px rgba(78, 205, 196, 0.4);
        }

        .menu-btn:hover {
            transform: translateY(-4px) scale(1.05);
        }

        .menu-btn:active {
            transform: translateY(2px) scale(0.98);
            box-shadow: 
                0 2px 0 currentColor,
                0 5px 15px rgba(0,0,0,0.2);
        }

        .menu-btn::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.4s, height 0.4s;
        }

        .menu-btn:active::after {
            width: 300px;
            height: 300px;
        }

        /* ===== Level Select ===== */
        .level-select {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(78, 205, 196, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 60px;
            pointer-events: auto;
            z-index: 200;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        .level-select.visible {
            opacity: 1;
            transform: translateX(0);
        }

        .level-select.hidden {
            pointer-events: none;
        }

        .level-title {
            font-family: 'Fredoka One', cursive;
            font-size: 42px;
            color: #fff;
            text-shadow: 0 4px 0 rgba(0,0,0,0.2);
            margin-bottom: 40px;
        }

        .level-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 20px;
        }

        .level-card {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 
                0 6px 0 #ccc,
                0 10px 20px rgba(0,0,0,0.15);
            position: relative;
        }

        .level-card:hover {
            transform: translateY(-8px) rotate(-3deg);
            box-shadow: 
                0 14px 0 #ccc,
                0 20px 30px rgba(0,0,0,0.2);
        }

        .level-card:active {
            transform: translateY(2px);
            box-shadow: 
                0 2px 0 #ccc,
                0 5px 10px rgba(0,0,0,0.15);
        }

        .level-card.locked {
            background: linear-gradient(135deg, #aaa 0%, #888 100%);
            cursor: not-allowed;
        }

        .level-card.locked:hover {
            transform: none;
        }

        .level-number {
            font-family: 'Fredoka One', cursive;
            font-size: 36px;
            color: #667eea;
        }

        .level-card.locked .level-number {
            color: #555;
        }

        .level-stars {
            display: flex;
            gap: 2px;
            margin-top: 5px;
        }

        .star {
            font-size: 14px;
            color: #ddd;
        }

        .star.filled {
            color: #FFD93D;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }

        .back-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 50px;
            height: 50px;
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            color: #fff;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .back-btn:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.1);
        }

        /* ===== Pause Menu ===== */
        .pause-menu {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(240,240,240,0.95) 100%);
            border-radius: 30px;
            padding: 40px 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            pointer-events: auto;
            z-index: 300;
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.3),
                inset 0 0 0 4px rgba(102, 126, 234, 0.3);
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        .pause-menu.visible {
            transform: translate(-50%, -50%) scale(1);
        }

        .pause-title {
            font-family: 'Fredoka One', cursive;
            font-size: 36px;
            color: #667eea;
            margin-bottom: 30px;
        }

        .pause-btn {
            width: 200px;
            padding: 15px;
            margin: 8px 0;
            font-family: 'Nunito', sans-serif;
            font-size: 18px;
            font-weight: 700;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .pause-btn.resume {
            background: linear-gradient(135deg, #7ED321 0%, #5CB85C 100%);
            color: #fff;
        }

        .pause-btn.restart {
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: #fff;
        }

        .pause-btn.quit {
            background: linear-gradient(135deg, #E94560 0%, #c73e54 100%);
            color: #fff;
        }

        .pause-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }

        /* ===== Result Popup ===== */
        .result-popup {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: linear-gradient(135deg, #fff 0%, #f8f8f8 100%);
            border-radius: 30px;
            padding: 40px 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            pointer-events: auto;
            z-index: 300;
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.3),
                inset 0 0 0 4px rgba(255, 215, 0, 0.5);
            transition: transform 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            opacity: 0;
        }

        .result-popup.visible {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
        }

        .result-title {
            font-family: 'Fredoka One', cursive;
            font-size: 42px;
            margin-bottom: 20px;
        }

        .result-title.win {
            color: #7ED321;
        }

        .result-title.lose {
            color: #E94560;
        }

        .result-stars {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .result-star {
            font-size: 50px;
            color: #ddd;
            transition: all 0.3s;
            opacity: 0;
            transform: scale(0) rotate(-180deg);
        }

        .result-star.animate {
            opacity: 1;
            transform: scale(1) rotate(0deg);
        }

        .result-star.filled {
            color: #FFD93D;
            text-shadow: 0 3px 10px rgba(255, 217, 61, 0.5);
            animation: starPop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        @keyframes starPop {
            0% { transform: scale(0) rotate(-180deg); }
            50% { transform: scale(1.3) rotate(10deg); }
            100% { transform: scale(1) rotate(0deg); }
        }

        .result-score {
            font-family: 'Fredoka One', cursive;
            font-size: 28px;
            color: #667eea;
            margin-bottom: 30px;
        }

        .result-score span {
            color: #FF6B35;
        }

        /* ===== Game HUD ===== */
        .game-hud {
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

        .hud-panel {
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,248,248,0.95) 100%);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 12px 20px;
            box-shadow: 
                0 4px 0 rgba(0,0,0,0.1),
                0 8px 20px rgba(0,0,0,0.1);
            pointer-events: auto;
        }

        .hud-panel h3 {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #888;
            margin-bottom: 4px;
            font-weight: 700;
        }

        .hud-panel .value {
            font-family: 'Fredoka One', cursive;
            font-size: 28px;
            color: #667eea;
        }

        .score-display {
            display: flex;
            align-items: baseline;
            gap: 5px;
        }

        .score-display .label {
            font-size: 14px;
            color: #888;
        }

        .birds-remaining {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }

        .bird-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 3px 0 rgba(0,0,0,0.2);
        }

        .bird-icon.available {
            transform: scale(1);
        }

        .bird-icon.used {
            opacity: 0.3;
            transform: scale(0.8);
        }

        .bird-icon.red { background: linear-gradient(135deg, #FF6B6B 0%, #E94560 100%); }
        .bird-icon.yellow { background: linear-gradient(135deg, #FFE66D 0%, #F4D35E 100%); }
        .bird-icon.black { background: linear-gradient(135deg, #555 0%, #333 100%); }

        .pause-btn-hud {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            border: none;
            border-radius: 12px;
            color: #fff;
            font-size: 20px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 0 #c45a2a;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .pause-btn-hud:hover {
            transform: translateY(-2px);
        }

        .pause-btn-hud:active {
            transform: translateY(2px);
            box-shadow: 0 2px 0 #c45a2a;
        }

        /* ===== Power Indicator ===== */
        .power-indicator {
            position: absolute;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,248,248,0.95) 100%);
            border-radius: 20px;
            padding: 12px 24px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }

        .power-indicator.visible {
            opacity: 1;
        }

        .power-bar {
            width: 200px;
            height: 16px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }

        .power-fill {
            height: 100%;
            width: 0%;
            border-radius: 10px;
            background: linear-gradient(90deg, #7ED321 0%, #FFE66D 50%, #E94560 100%);
            transition: width 0.05s;
            position: relative;
        }

        .power-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 50%;
            background: rgba(255,255,255,0.3);
            border-radius: 10px 10px 0 0;
        }

        /* ===== Controls Hint ===== */
        .controls-hint {
            position: absolute;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255,255,255,0.9);
            border-radius: 12px;
            padding: 10px 24px;
            color: #666;
            font-size: 13px;
            font-weight: 600;
            pointer-events: none;
            display: flex;
            gap: 24px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .controls-hint kbd {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 3px 10px;
            border-radius: 6px;
            font-family: inherit;
            font-weight: 700;
            margin-right: 4px;
        }

        /* ===== Level Transition ===== */
        .level-transition {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            z-index: 400;
            opacity: 0;
            transition: opacity 0.5s;
        }

        .level-transition.visible {
            opacity: 1;
            pointer-events: auto;
        }

        .transition-number {
            font-family: 'Fredoka One', cursive;
            font-size: 150px;
            color: rgba(255,255,255,0.9);
            text-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: numberPulse 0.5s ease-out;
        }

        @keyframes numberPulse {
            0% { transform: scale(0); opacity: 0; }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); opacity: 1; }
        }

        .transition-text {
            font-family: 'Fredoka One', cursive;
            font-size: 36px;
            color: #fff;
            margin-bottom: 20px;
        }

        /* ===== Damage Popup ===== */
        .damage-popup {
            position: absolute;
            font-family: 'Fredoka One', cursive;
            font-size: 24px;
            pointer-events: none;
            animation: damageFloat 1s ease-out forwards;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            z-index: 150;
        }

        @keyframes damageFloat {
            0% { 
                opacity: 1; 
                transform: translateY(0) scale(0.5); 
            }
            20% {
                transform: translateY(-10px) scale(1.2);
            }
            100% { 
                opacity: 0; 
                transform: translateY(-60px) scale(0.8); 
            }
        }

        /* ===== Floating decorations ===== */
        .floating-birds {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            pointer-events: none;
        }

        .float-bird {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            animation: floatBird 3s ease-in-out infinite;
        }

        .float-bird:nth-child(2) { animation-delay: 0.5s; }
        .float-bird:nth-child(3) { animation-delay: 1s; }

        @keyframes floatBird {
            0%, 100% { transform: translateY(0) rotate(-5deg); }
            50% { transform: translateY(-15px) rotate(5deg); }
        }

        /* ===== Toast Notifications ===== */
        .toast-container {
            position: absolute;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 500;
            pointer-events: none;
        }

        .toast {
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,248,248,0.95) 100%);
            border-radius: 16px;
            padding: 16px 32px;
            margin-bottom: 10px;
            font-weight: 700;
            font-size: 18px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
            animation: toastIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .toast.success { border-left: 5px solid #7ED321; }
        .toast.warning { border-left: 5px solid #F5A623; }
        .toast.error { border-left: 5px solid #E94560; }

        @keyframes toastIn {
            0% { 
                opacity: 0; 
                transform: translateY(-30px) scale(0.8); 
            }
            100% { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }

        .toast.hide {
            animation: toastOut 0.3s ease-in forwards;
        }

        @keyframes toastOut {
            to { 
                opacity: 0; 
                transform: translateY(-20px) scale(0.8); 
            }
        }

        /* ===== Skill Button ===== */
        .skill-btn {
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            border: 4px solid #fff;
            cursor: pointer;
            transition: all 0.3s;
            pointer-events: auto;
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        .skill-btn:hover:not(.cooldown) {
            transform: scale(1.1);
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }

        .skill-btn:active:not(.cooldown) {
            transform: scale(0.95);
        }

        .skill-btn.cooldown {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .skill-btn.red-skill { background: linear-gradient(135deg, #FF6B6B 0%, #E94560 100%); }
        .skill-btn.yellow-skill { background: linear-gradient(135deg, #FFE66D 0%, #F4D35E 100%); }
        .skill-btn.black-skill { background: linear-gradient(135deg, #555 0%, #333 100%); }

        .cooldown-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 50%;
            background: rgba(0,0,0,0.6);
            clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 0%);
            transform-origin: center;
        }

        /* ===== Combo Display ===== */
        .combo-display {
            position: absolute;
            top: 50%;
            right: 30px;
            transform: translateY(-50%);
            font-family: 'Fredoka One', cursive;
            font-size: 48px;
            color: #FF6B35;
            text-shadow: 
                0 4px 0 #c45a2a,
                0 8px 20px rgba(0,0,0,0.3);
            opacity: 0;
            transform: translateY(-50%) scale(0);
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            pointer-events: none;
            z-index: 60;
        }

        .combo-display.visible {
            opacity: 1;
            transform: translateY(-50%) scale(1);
        }

        .combo-display .multiplier {
            display: block;
            font-size: 24px;
            color: #FFE66D;
        }
    </style>
</head>
<body>
    <div class="game-container" id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        
        <!-- UI Overlay -->
        <div class="ui-overlay" id="uiOverlay">
            <!-- Main Menu -->
            <div class="main-menu" id="mainMenu">
                <h1 class="game-title">ANGRY <span>BIRDS</span></h1>
                <p class="subtitle">Physics-based destruction</p>
                <div class="menu-buttons">
                    <button class="menu-btn primary" onclick="Game.showLevelSelect()">Play</button>
                    <button class="menu-btn secondary" onclick="Game.showTutorial()">How to Play</button>
                </div>
            </div>
            
            <!-- Level Select -->
            <div class="level-select hidden" id="levelSelect">
                <button class="back-btn" onclick="Game.hideLevelSelect()">←</button>
                <h2 class="level-title">Select Level</h2>
                <div class="level-grid" id="levelGrid"></div>
            </div>
            
            <!-- Pause Menu -->
            <div class="pause-menu" id="pauseMenu">
                <h2 class="pause-title">Paused</h2>
                <button class="pause-btn resume" onclick="Game.resume()">Resume</button>
                <button class="pause-btn restart" onclick="Game.restart()">Restart</button>
                <button class="pause-btn quit" onclick="Game.quit()">Quit</button>
            </div>
            
            <!-- Result Popup -->
            <div class="result-popup" id="resultPopup">
                <h2 class="result-title win" id="resultTitle">Victory!</h2>
                <div class="result-stars" id="resultStars"></div>
                <p class="result-score">Score: <span id="finalScore">0</span></p>
                <div class="menu-buttons">
                    <button class="menu-btn secondary" onclick="Game.restart()">Retry</button>
                    <button class="menu-btn primary" onclick="Game.nextLevel()">Next Level</button>
                </div>
            </div>
            
            <!-- Level Transition -->
            <div class="level-transition" id="levelTransition">
                <p class="transition-text">Level</p>
                <p class="transition-number" id="transitionNumber">1</p>
            </div>
            
            <!-- Game HUD -->
            <div class="game-hud" id="gameHud" style="display: none;">
                <div class="hud-panel">
                    <h3>Score</h3>
                    <div class="score-display">
                        <span class="value" id="scoreValue">0</span>
                    </div>
                </div>
                
                <div class="hud-panel">
                    <h3>Birds</h3>
                    <div class="birds-remaining" id="birdsRemaining"></div>
                </div>
                
                <button class="pause-btn-hud" onclick="Game.pause()">⏸</button>
            </div>
            
            <!-- Power Indicator -->
            <div class="power-indicator" id="powerIndicator">
                <div class="power-bar">
                    <div class="power-fill" id="powerFill"></div>
                </div>
            </div>
            
            <!-- Controls Hint -->
            <div class="controls-hint" id="controlsHint" style="display: none;">
                <span><kbd>Drag</kbd> Aim & Shoot</span>
                <span><kbd>Space</kbd> Skill</span>
                <span><kbd>Esc</kbd> Pause</span>
            </div>
            
            <!-- Skill Button -->
            <button class="skill-btn red-skill" id="skillBtn" style="display: none;" onclick="Game.useSkill()">
                💥
            </button>
            
            <!-- Combo Display -->
            <div class="combo-display" id="comboDisplay">
                <span class="multiplier" id="comboMultiplier">x2</span>
                COMBO
            </div>
            
            <!-- Toast Container -->
            <div class="toast-container" id="toastContainer"></div>
        </div>
    </div>

    <script>
// ============================================
// 游戏配置常量
// ============================================
const CONFIG = {
    CANVAS_WIDTH: 1200,
    CANVAS_HEIGHT: 700,
    GROUND_HEIGHT: 120,
    TARGET_FPS: 60,
    WORLD_WIDTH: 2400,
    CAMERA_LERP: 0.08,
    MIN_ZOOM: 0.5,
    MAX_ZOOM: 2.0,
    
    SLINGSHOT: {
        X: 200,
        Y: 0,
        MAX_STRETCH: 120,
        REST_LENGTH: 40,
        BAND_WIDTH: 6,
        BAND_COLOR: '#8B4513',
        BAND_STRETCH_COLOR: '#A0522D'
    },
    
    BIRD: {
        RADIUS: 18,
        LAUNCH_POWER: 0.18,
        MIN_POWER: 2,
        MAX_POWER: 22,
        COLORS: {
            red: { main: '#e94560', dark: '#c73e54', light: '#ff6b8a' },
            yellow: { main: '#ffd93d', dark: '#e6c235', light: '#ffe066' },
            black: { main: '#2d3436', dark: '#1e2324', light: '#4a5355' }
        }
    },
    
    TRAJECTORY: {
        POINT_COUNT: 40,
        POINT_SPACING: 8,
        POINT_SIZE_START: 4,
        POINT_SIZE_END: 1
    },
    
    PHYSICS: {
        GRAVITY: 0.4,
        AIR_RESISTANCE: 0.995,
        GROUND_FRICTION: 0.85,
        ANGULAR_DAMPING: 0.98,
        POSITION_CORRECTION: 0.7,
        ALLOW_SLEEP: true,
        SLEEP_THRESHOLD: 0.15,
        SLEEP_TIME: 120,
        COLLISION_ITERATIONS: 4
    },
    
    MATERIALS: {
        wood: {
            name: 'wood',
            health: 80,
            destructionThreshold: 25,
            density: 0.6,
            restitution: 0.3,
            friction: 0.5,
            colors: {
                main: '#8B5A2B',
                dark: '#6B4423',
                light: '#A0724C',
                damaged: '#5C3D1E'
            },
            particles: {
                type: 'debris',
                colors: ['#8B5A2B', '#A0724C', '#6B4423', '#D2691E', '#CD853F'],
                count: { min: 8, max: 15 },
                size: { min: 3, max: 8 },
                speed: { min: 2, max: 6 },
                life: { min: 40, max: 80 },
                gravity: 0.15,
                rotation: true
            }
        },
        glass: {
            name: 'glass',
            health: 40,
            destructionThreshold: 15,
            density: 0.4,
            restitution: 0.1,
            friction: 0.3,
            colors: {
                main: '#87CEEB',
                dark: '#5F9EA0',
                light: '#B0E0E6',
                damaged: '#4682B4'
            },
            particles: {
                type: 'shard',
                colors: ['#87CEEB', '#B0E0E6', '#E0FFFF', '#AFEEEE', '#FFFFFF'],
                count: { min: 12, max: 25 },
                size: { min: 2, max: 6 },
                speed: { min: 3, max: 8 },
                life: { min: 50, max: 100 },
                gravity: 0.12,
                rotation: true,
                shimmer: true
            }
        },
        stone: {
            name: 'stone',
            health: 200,
            destructionThreshold: 50,
            density: 1.2,
            restitution: 0.2,
            friction: 0.7,
            colors: {
                main: '#708090',
                dark: '#4A5568',
                light: '#A0AEC0',
                damaged: '#4A5568'
            },
            particles: {
                type: 'dust',
                colors: ['#708090', '#A0AEC0', '#CBD5E0', '#E2E8F0', '#9CA3AF'],
                count: { min: 15, max: 30 },
                size: { min: 2, max: 5 },
                speed: { min: 1, max: 4 },
                life: { min: 60, max: 120 },
                gravity: 0.05,
                rotation: false,
                fadeOut: true
            }
        },
        tnt: {
            name: 'tnt',
            health: 30,
            destructionThreshold: 20,
            density: 0.5,
            restitution: 0.1,
            friction: 0.4,
            colors: {
                main: '#DC2626',
                dark: '#991B1B',
                light: '#EF4444',
                damaged: '#7F1D1D'
            },
            particles: {
                type: 'explosion',
                colors: ['#FF4500', '#FF6347', '#FFD700', '#FFA500', '#FF0000'],
                count: { min: 30, max: 50 },
                size: { min: 4, max: 12 },
                speed: { min: 5, max: 15 },
                life: { min: 30, max: 60 },
                gravity: 0.08,
                rotation: true,
                glow: true
            },
            explosionRadius: 150,
            explosionDamage: 100
        }
    },
    
    PARTICLES: {
        MAX_PARTICLES: 500,
        EMITTER_POOL_SIZE: 50
    },
    
    UI: {
        ANIMATION_DURATION: 300,
        TOAST_DURATION: 2000
    }
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
    
    safeColor: (r, g, b, a = 1) => {
        r = Utils.clamp(Math.round(r), 0, 255);
        g = Utils.clamp(Math.round(g), 0, 255);
        b = Utils.clamp(Math.round(b), 0, 255);
        a = Utils.clamp(a, 0, 1);
        return `rgba(${r},${g},${b},${a})`;
    },
    
    pickRandom: (arr) => arr[Math.floor(Math.random() * arr.length)],
    
    easeOutCubic: (t) => 1 - Math.pow(1 - t, 3),
    easeOutElastic: (t) => {
        const c4 = (2 * Math.PI) / 3;
        return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
    },
    easeOutBack: (t) => {
        const c1 = 1.70158;
        const c3 = c1 + 1;
        return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
    },
    easeInQuad: (t) => t * t,
    easeOutQuad: (t) => 1 - (1 - t) * (1 - t),
    easeOutBounce: (t) => {
        const n1 = 7.5625;
        const d1 = 2.75;
        if (t < 1 / d1) return n1 * t * t;
        if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
        if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
        return n1 * (t -= 2.625 / d1) * t + 0.984375;
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

    add(v) { return new Vector2(this.x + v.x, this.y + v.y); }
    sub(v) { return new Vector2(this.x - v.x, this.y - v.y); }
    mul(s) { return new Vector2(this.x * s, this.y * s); }
    dot(v) { return this.x * v.x + this.y * v.y; }
    cross(v) { return this.x * v.y - this.y * v.x; }
    length() { return Math.sqrt(this.x * this.x + this.y * this.y); }
    lengthSq() { return this.x * this.x + this.y * this.y; }

    normalize() {
        const len = this.length();
        if (len === 0) return new Vector2(0, 0);
        return new Vector2(this.x / len, this.y / len);
    }

    rotate(angle) {
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        return new Vector2(this.x * cos - this.y * sin, this.x * sin + this.y * cos);
    }

    clone() { return new Vector2(this.x, this.y); }
    set(x, y) { this.x = x; this.y = y; return this; }

    static fromAngle(angle, length = 1) {
        return new Vector2(Math.cos(angle) * length, Math.sin(angle) * length);
    }
}

// ============================================
// 粒子类
// ============================================
class Particle {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = 0;
        this.y = 0;
        this.vx = 0;
        this.vy = 0;
        this.size = 5;
        this.color = '#fff';
        this.alpha = 1;
        this.life = 60;
        this.maxLife = 60;
        this.gravity = 0.1;
        this.rotation = 0;
        this.rotationSpeed = 0;
        this.type = 'circle';
        this.shimmer = false;
        this.glow = false;
        this.fadeOut = true;
        this.active = false;
    }

    init(x, y, vx, vy, size, color, life, options = {}) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.size = size;
        this.color = color;
        this.life = life;
        this.maxLife = life;
        this.alpha = 1;
        this.rotation = options.rotation || 0;
        this.rotationSpeed = options.rotationSpeed || 0;
        this.gravity = options.gravity ?? 0.1;
        this.type = options.type || 'circle';
        this.shimmer = options.shimmer || false;
        this.glow = options.glow || false;
        this.fadeOut = options.fadeOut !== false;
        this.active = true;
    }

    update() {
        if (!this.active) return;

        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity;
        this.vx *= 0.98;
        this.rotation += this.rotationSpeed;
        this.life--;

        if (this.fadeOut) {
            this.alpha = Math.max(0, this.life / this.maxLife);
        }

        if (this.life <= 0) {
            this.active = false;
        }
    }

    render(ctx) {
        if (!this.active || this.alpha <= 0) return;

        ctx.save();
        ctx.globalAlpha = this.alpha;
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);

        if (this.glow) {
            ctx.shadowBlur = 15;
            ctx.shadowColor = this.color;
        }

        if (this.shimmer) {
            const shimmerAlpha = 0.5 + Math.sin(Date.now() * 0.02 + this.x) * 0.5;
            ctx.globalAlpha = this.alpha * shimmerAlpha;
        }

        ctx.fillStyle = this.color;

        switch (this.type) {
            case 'circle':
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;

            case 'shard':
                ctx.beginPath();
                ctx.moveTo(0, -this.size);
                ctx.lineTo(this.size * 0.5, this.size * 0.5);
                ctx.lineTo(-this.size * 0.5, this.size * 0.5);
                ctx.closePath();
                ctx.fill();
                break;

            case 'debris':
                ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 0.6);
                break;

            case 'dust':
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;

            case 'spark':
                ctx.beginPath();
                ctx.moveTo(-this.size, 0);
                ctx.lineTo(0, -this.size * 0.3);
                ctx.lineTo(this.size, 0);
                ctx.lineTo(0, this.size * 0.3);
                ctx.closePath();
                ctx.fill();
                break;

            case 'flame':
                const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size);
                gradient.addColorStop(0, this.color);
                gradient.addColorStop(0.5, this.color + '80');
                gradient.addColorStop(1, 'transparent');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;

            case 'trail':
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;
        }

        ctx.restore();
    }
}

// ============================================
// 粒子系统
// ============================================
class ParticleSystem {
    constructor(maxParticles = 500) {
        this.particles = [];
        this.maxParticles = maxParticles;
        
        for (let i = 0; i < maxParticles; i++) {
            this.particles.push(new Particle());
        }
        
        this.activeCount = 0;
    }

    emit(x, y, config, velocity = null) {
        const count = Utils.randomInt(config.count.min, config.count.max);
        let emitted = 0;

        for (const particle of this.particles) {
            if (!particle.active) {
                const angle = velocity ? 
                    Math.atan2(velocity.y, velocity.x) + Utils.randomRange(-0.5, 0.5) :
                    Utils.randomRange(0, Math.PI * 2);
                const speed = Utils.randomRange(config.speed.min, config.speed.max);
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed;
                const size = Utils.randomRange(config.size.min, config.size.max);
                const life = Utils.randomInt(config.life.min, config.life.max);
                const color = Utils.pickRandom(config.colors);

                particle.init(x, y, vx, vy, size, color, life, {
                    gravity: config.gravity ?? 0.1,
                    rotation: Utils.randomRange(0, Math.PI * 2),
                    rotationSpeed: config.rotation ? Utils.randomRange(-0.2, 0.2) : 0,
                    type: config.type || 'circle',
                    shimmer: config.shimmer || false,
                    glow: config.glow || false,
                    fadeOut: config.fadeOut !== false
                });

                emitted++;
                if (emitted >= count) break;
            }
        }

        this.activeCount += emitted;
    }

    emitTrail(x, y, color, size = 4) {
        for (const particle of this.particles) {
            if (!particle.active) {
                particle.init(x, y, 0, 0, size, color, 20, {
                    gravity: 0,
                    type: 'trail',
                    fadeOut: true
                });
                break;
            }
        }
    }

    update() {
        this.activeCount = 0;
        for (const particle of this.particles) {
            if (particle.active) {
                particle.update();
                if (particle.active) this.activeCount++;
            }
        }
    }

    render(ctx, camera) {
        ctx.save();
        for (const particle of this.particles) {
            if (particle.active) {
                const screenX = particle.x - camera.x;
                const screenY = particle.y - camera.y;
                
                if (screenX > -50 && screenX < CONFIG.CANVAS_WIDTH + 50 &&
                    screenY > -50 && screenY < CONFIG.CANVAS_HEIGHT + 50) {
                    ctx.save();
                    ctx.globalAlpha = particle.alpha;
                    ctx.translate(screenX, screenY);
                    ctx.rotate(particle.rotation);
                    ctx.fillStyle = particle.color;
                    ctx.beginPath();
                    ctx.arc(0, 0, particle.size, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
            }
        }
        ctx.restore();
    }
}

// ============================================
// 刚体类
// ============================================
class RigidBody {
    constructor(x, y, width, height, material = 'wood') {
        this.position = new Vector2(x, y);
        this.velocity = new Vector2(0, 0);
        this.width = width;
        this.height = height;
        this.angle = 0;
        this.angularVelocity = 0;
        this.material = CONFIG.MATERIALS[material];
        this.mass = width * height * this.material.density;
        this.invMass = 1 / this.mass;
        this.health = this.material.health;
        this.maxHealth = this.material.health;
        this.destroyed = false;
        this.sleeping = false;
        this.sleepTimer = 0;
        this.damageFlash = 0;
    }

    update() {
        if (this.destroyed) return;

        // 睡眠检测
        if (CONFIG.PHYSICS.ALLOW_SLEEP) {
            const speed = this.velocity.length();
            if (speed < CONFIG.PHYSICS.SLEEP_THRESHOLD) {
                this.sleepTimer++;
                if (this.sleepTimer > CONFIG.PHYSICS.SLEEP_TIME) {
                    this.sleeping = true;
                }
            } else {
                this.sleepTimer = 0;
                this.sleeping = false;
            }
        }

        if (this.sleeping) return;

        // 应用重力
        this.velocity.y += CONFIG.PHYSICS.GRAVITY;
        
        // 空气阻力
        this.velocity.x *= CONFIG.PHYSICS.AIR_RESISTANCE;
        this.velocity.y *= CONFIG.PHYSICS.AIR_RESISTANCE;

        // 更新位置
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;
        this.angle += this.angularVelocity;
        this.angularVelocity *= CONFIG.PHYSICS.ANGULAR_DAMPING;

        // 地面碰撞
        const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT;
        if (this.position.y + this.height / 2 > groundY) {
            this.position.y = groundY - this.height / 2;
            this.velocity.y *= -this.material.restitution * 0.5;
            this.velocity.x *= CONFIG.PHYSICS.GROUND_FRICTION;
            this.angularVelocity *= 0.9;
        }

        // 伤害闪烁
        if (this.damageFlash > 0) {
            this.damageFlash -= 0.1;
        }
    }

    takeDamage(damage) {
        this.health -= damage;
        this.damageFlash = 1;
        this.sleeping = false;
        this.sleepTimer = 0;

        if (this.health <= 0) {
            this.destroyed = true;
            return true;
        }
        return false;
    }

    render(ctx, camera) {
        if (this.destroyed) return;

        const screenX = this.position.x - camera.x;
        const screenY = this.position.y - camera.y;

        ctx.save();
        ctx.translate(screenX, screenY);
        ctx.rotate(this.angle);

        const healthRatio = this.health / this.maxHealth;
        const colors = this.material.colors;

        // 阴影
        ctx.shadowColor = 'rgba(0,0,0,0.3)';
        ctx.shadowBlur = 10;
        ctx.shadowOffsetY = 5;

        // 主体
        let fillColor = colors.main;
        if (healthRatio < 0.5) {
            fillColor = colors.damaged;
        }
        
        if (this.damageFlash > 0) {
            ctx.fillStyle = `rgba(255,255,255,${this.damageFlash})`;
        } else {
            ctx.fillStyle = fillColor;
        }

        // 绘制圆角矩形
        this.roundRect(ctx, -this.width/2, -this.height/2, this.width, this.height, 4);
        ctx.fill();

        // 高光
        ctx.shadowColor = 'transparent';
        const gradient = ctx.createLinearGradient(0, -this.height/2, 0, this.height/2);
        gradient.addColorStop(0, colors.light);
        gradient.addColorStop(0.5, 'transparent');
        ctx.fillStyle = gradient;
        this.roundRect(ctx, -this.width/2, -this.height/2, this.width, this.height, 4);
        ctx.fill();

        // 裂缝效果
        if (healthRatio < 0.7) {
            ctx.strokeStyle = 'rgba(0,0,0,0.4)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            const cracks = Math.floor((1 - healthRatio) * 5);
            for (let i = 0; i < cracks; i++) {
                const startX = Utils.randomRange(-this.width/2, this.width/2);
                const startY = Utils.randomRange(-this.height/2, this.height/2);
                ctx.moveTo(startX, startY);
                ctx.lineTo(startX + Utils.randomRange(-10, 10), startY + Utils.randomRange(-10, 10));
            }
            ctx.stroke();
        }

        ctx.restore();

        // 血条
        if (healthRatio < 1) {
            const barWidth = this.width;
            const barHeight = 6;
            const barX = screenX - barWidth/2;
            const barY = screenY - this.height/2 - 12;

            ctx.fillStyle = 'rgba(0,0,0,0.5)';
            ctx.fillRect(barX, barY, barWidth, barHeight);

            const healthColor = healthRatio > 0.5 ? '#7ED321' : healthRatio > 0.25 ? '#F5A623' : '#E94560';
            ctx.fillStyle = healthColor;
            ctx.fillRect(barX, barY, barWidth * healthRatio, barHeight);
        }
    }

    roundRect(ctx, x, y, w, h, r) {
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

    getBounds() {
        return {
            left: this.position.x - this.width / 2,
            right: this.position.x + this.width / 2,
            top: this.position.y - this.height / 2,
            bottom: this.position.y + this.height / 2
        };
    }
}

// ============================================
// 小鸟类
// ============================================
class Bird {
    constructor(x, y, type = 'red') {
        this.position = new Vector2(x, y);
        this.velocity = new Vector2(0, 0);
        this.radius = CONFIG.BIRD.RADIUS;
        this.type = type;
        this.colors = CONFIG.BIRD.COLORS[type];
        this.launched = false;
        this.stopped = false;
        this.rotation = 0;
        this.skillUsed = false;
        this.trailPoints = [];
        this.skillActive = false;
        this.skillTimer = 0;
    }

    update(camera) {
        if (!this.launched || this.stopped) return;

        // 保存轨迹点
        if (this.trailPoints.length === 0 || 
            Utils.distance(this.position.x, this.position.y, 
                this.trailPoints[this.trailPoints.length - 1].x, 
                this.trailPoints[this.trailPoints.length - 1].y) > 10) {
            this.trailPoints.push({ x: this.position.x, y: this.position.y, alpha: 1 });
            if (this.trailPoints.length > 20) {
                this.trailPoints.shift();
            }
        }

        // 更新轨迹透明度
        for (let point of this.trailPoints) {
            point.alpha -= 0.03;
        }
        this.trailPoints = this.trailPoints.filter(p => p.alpha > 0);

        // 应用重力
        this.velocity.y += CONFIG.PHYSICS.GRAVITY;
        
        // 空气阻力
        this.velocity.x *= CONFIG.PHYSICS.AIR_RESISTANCE;
        this.velocity.y *= CONFIG.PHYSICS.AIR_RESISTANCE;

        // 更新位置
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;

        // 旋转
        this.rotation = Math.atan2(this.velocity.y, this.velocity.x);

        // 技能计时
        if (this.skillActive) {
            this.skillTimer--;
            if (this.skillTimer <= 0) {
                this.skillActive = false;
            }
        }

        // 地面碰撞
        const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT;
        if (this.position.y + this.radius > groundY) {
            this.position.y = groundY - this.radius;
            this.velocity.y *= -0.3;
            this.velocity.x *= 0.7;
            
            if (Math.abs(this.velocity.x) < 0.5 && Math.abs(this.velocity.y) < 1) {
                this.stopped = true;
            }
        }

        // 边界检测
        if (this.position.x < -100 || this.position.x > CONFIG.WORLD_WIDTH + 100 ||
            this.position.y > CONFIG.CANVAS_HEIGHT + 100) {
            this.stopped = true;
        }
    }

    useSkill() {
        if (this.skillUsed || !this.launched || this.stopped) return null;
        
        this.skillUsed = true;
        this.skillActive = true;
        this.skillTimer = 30;

        switch (this.type) {
            case 'yellow':
                // 加速
                this.velocity.x *= 2;
                this.velocity.y *= 0.5;
                return { type: 'speed', position: this.position.clone() };
            
            case 'black':
                // 爆炸
                return { type: 'explode', position: this.position.clone(), radius: 150 };
            
            default:
                // 红鸟 - 普通增强
                this.velocity.x *= 1.5;
                return { type: 'boost', position: this.position.clone() };
        }
    }

    render(ctx, camera) {
        const screenX = this.position.x - camera.x;
        const screenY = this.position.y - camera.y;

        // 绘制轨迹
        ctx.save();
        for (let i = 0; i < this.trailPoints.length; i++) {
            const point = this.trailPoints[i];
            const px = point.x - camera.x;
            const py = point.y - camera.y;
            const size = (i / this.trailPoints.length) * this.radius * 0.6;
            
            ctx.globalAlpha = point.alpha * 0.5;
            ctx.fillStyle = this.colors.main;
            ctx.beginPath();
            ctx.arc(px, py, size, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();

        ctx.save();
        ctx.translate(screenX, screenY);
        ctx.rotate(this.rotation);

        // 技能光环
        if (this.skillActive) {
            ctx.shadowBlur = 30;
            ctx.shadowColor = this.colors.light;
        }

        // 身体
        ctx.fillStyle = this.colors.main;
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // 高光
        const bodyGrad = ctx.createRadialGradient(-5, -5, 0, 0, 0, this.radius);
        bodyGrad.addColorStop(0, this.colors.light);
        bodyGrad.addColorStop(0.5, 'transparent');
        ctx.fillStyle = bodyGrad;
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // 眼睛
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.ellipse(-4, -3, 6, 7, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(6, -3, 6, 7, 0, 0, Math.PI * 2);
        ctx.fill();

        // 瞳孔
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.arc(-3, -2, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(7, -2, 3, 0, Math.PI * 2);
        ctx.fill();

        // 眉毛（愤怒表情）
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-10, -12);
        ctx.lineTo(-2, -8);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(12, -12);
        ctx.lineTo(4, -8);
        ctx.stroke();

        // 嘴巴
        ctx.fillStyle = '#FF8C00';
        ctx.beginPath();
        ctx.moveTo(0, 5);
        ctx.lineTo(-6, 10);
        ctx.lineTo(0, 8);
        ctx.lineTo(6, 10);
        ctx.closePath();
        ctx.fill();

        // 类型标识
        if (this.type === 'yellow') {
            // 头顶羽毛
            ctx.fillStyle = this.colors.main;
            ctx.beginPath();
            ctx.moveTo(-3, -this.radius + 2);
            ctx.lineTo(0, -this.radius - 10);
            ctx.lineTo(3, -this.radius + 2);
            ctx.closePath();
            ctx.fill();
        } else if (this.type === 'black') {
            // 爆炸符号
            if (!this.skillUsed) {
                ctx.fillStyle = '#FFD700';
                ctx.font = 'bold 14px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('💥', 0, -this.radius - 5);
            }
        }

        ctx.restore();
    }
}

// ============================================
// 绿猪类
// ============================================
class Pig {
    constructor(x, y, size = 'medium') {
        this.position = new Vector2(x, y);
        const sizeMultiplier = size === 'small' ? 0.7 : size === 'large' ? 1.4 : 1;
        this.radius = 25 * sizeMultiplier;
        this.health = 50 * sizeMultiplier;
        this.maxHealth = this.health;
        this.alive = true;
        this.damageFlash = 0;
        this.size = size;
        this.blinkTimer = 0;
    }

    takeDamage(damage) {
        this.health -= damage;
        this.damageFlash = 1;
        
        if (this.health <= 0) {
            this.alive = false;
            return true;
        }
        return false;
    }

    update() {
        if (!this.alive) return;
        
        if (this.damageFlash > 0) {
            this.damageFlash -= 0.1;
        }

        this.blinkTimer++;
    }

    render(ctx, camera) {
        if (!this.alive) return;

        const screenX = this.position.x - camera.x;
        const screenY = this.position.y - camera.y;

        ctx.save();
        ctx.translate(screenX, screenY);

        // 身体
        const bodyColor = this.damageFlash > 0 ? 
            `rgba(255,255,255,${this.damageFlash})` : '#7CB342';
        ctx.fillStyle = bodyColor;
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // 高光
        const bodyGrad = ctx.createRadialGradient(-this.radius * 0.3, -this.radius * 0.3, 0, 0, 0, this.radius);
        bodyGrad.addColorStop(0, '#9CCC65');
        bodyGrad.addColorStop(0.5, 'transparent');
        ctx.fillStyle = bodyGrad;
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // 耳朵
        ctx.fillStyle = '#7CB342';
        ctx.beginPath();
        ctx.arc(-this.radius * 0.7, -this.radius * 0.5, this.radius * 0.3, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(this.radius * 0.7, -this.radius * 0.5, this.radius * 0.3, 0, Math.PI * 2);
        ctx.fill();

        // 眼睛
        const blinking = this.blinkTimer % 200 < 10;
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.ellipse(-this.radius * 0.3, -this.radius * 0.1, this.radius * 0.25, this.radius * 0.3, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(this.radius * 0.3, -this.radius * 0.1, this.radius * 0.25, this.radius * 0.3, 0, 0, Math.PI * 2);
        ctx.fill();

        // 瞳孔
        if (!blinking) {
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(-this.radius * 0.3, 0, this.radius * 0.12, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(this.radius * 0.3, 0, this.radius * 0.12, 0, Math.PI * 2);
            ctx.fill();
        }

        // 鼻子
        ctx.fillStyle = '#558B2F';
        ctx.beginPath();
        ctx.ellipse(0, this.radius * 0.3, this.radius * 0.35, this.radius * 0.2, 0, 0, Math.PI * 2);
        ctx.fill();

        // 鼻孔
        ctx.fillStyle = '#33691E';
        ctx.beginPath();
        ctx.arc(-this.radius * 0.12, this.radius * 0.3, this.radius * 0.08, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(this.radius * 0.12, this.radius * 0.3, this.radius * 0.08, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // 血条
        const healthRatio = this.health / this.maxHealth;
        if (healthRatio < 1) {
            const barWidth = this.radius * 2;
            const barHeight = 6;
            const barX = screenX - barWidth/2;
            const barY = screenY - this.radius - 12;

            ctx.fillStyle = 'rgba(0,0,0,0.5)';
            ctx.fillRect(barX, barY, barWidth, barHeight);

            ctx.fillStyle = '#7ED321';
            ctx.fillRect(barX, barY, barWidth * healthRatio, barHeight);
        }
    }
}

// ============================================
// 弹弓类
// ============================================
class Slingshot {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.pulling = false;
        this.pullX = x;
        this.pullY = y;
    }

    render(ctx, camera, bird = null) {
        const screenX = this.x - camera.x;
        const screenY = this.y - camera.y;

        // 后皮筋
        if (this.pulling && bird) {
            ctx.strokeStyle = CONFIG.SLINGSHOT.BAND_STRETCH_COLOR;
            ctx.lineWidth = CONFIG.SLINGSHOT.BAND_WIDTH;
            ctx.beginPath();
            ctx.moveTo(screenX - 15, screenY - 40);
            ctx.lineTo(this.pullX - camera.x, this.pullY - camera.y);
            ctx.stroke();
        }

        // 左支架
        ctx.fillStyle = '#5D4037';
        ctx.beginPath();
        ctx.moveTo(screenX - 20, screenY + 60);
        ctx.lineTo(screenX - 25, screenY - 50);
        ctx.lineTo(screenX - 10, screenY - 45);
        ctx.lineTo(screenX - 5, screenY + 60);
        ctx.closePath();
        ctx.fill();

        // 右支架
        ctx.beginPath();
        ctx.moveTo(screenX + 5, screenY + 60);
        ctx.lineTo(screenX + 10, screenY - 45);
        ctx.lineTo(screenX + 25, screenY - 50);
        ctx.lineTo(screenX + 20, screenY + 60);
        ctx.closePath();
        ctx.fill();

        // Y形顶部
        ctx.fillStyle = '#6D4C41';
        ctx.beginPath();
        ctx.arc(screenX - 18, screenY - 45, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(screenX + 18, screenY - 45, 8, 0, Math.PI * 2);
        ctx.fill();

        // 前皮筋
        if (this.pulling && bird) {
            ctx.strokeStyle = CONFIG.SLINGSHOT.BAND_COLOR;
            ctx.lineWidth = CONFIG.SLINGSHOT.BAND_WIDTH;
            ctx.beginPath();
            ctx.moveTo(screenX + 15, screenY - 40);
            ctx.lineTo(this.pullX - camera.x, this.pullY - camera.y);
            ctx.stroke();
        } else {
            // 静态皮筋
            ctx.strokeStyle = CONFIG.SLINGSHOT.BAND_COLOR;
            ctx.lineWidth = CONFIG.SLINGSHOT.BAND_WIDTH;
            ctx.beginPath();
            ctx.moveTo(screenX - 15, screenY - 40);
            ctx.lineTo(screenX, screenY - 20);
            ctx.lineTo(screenX + 15, screenY - 40);
            ctx.stroke();
        }
    }

    renderTrajectory(ctx, camera, velocity) {
        if (!velocity) return;

        ctx.save();
        const startX = this.pullX;
        const startY = this.pullY;
        
        let x = startX;
        let y = startY;
        let vx = velocity.x;
        let vy = velocity.y;

        for (let i = 0; i < CONFIG.TRAJECTORY.POINT_COUNT; i++) {
            vy += CONFIG.PHYSICS.GRAVITY;
            x += vx;
            y += vy;

            if (y > CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT) break;

            const screenX = x - camera.x;
            const screenY = y - camera.y;
            
            const progress = i / CONFIG.TRAJECTORY.POINT_COUNT;
            const size = Utils.lerp(CONFIG.TRAJECTORY.POINT_SIZE_START, CONFIG.TRAJECTORY.POINT_SIZE_END, progress);
            const alpha = 1 - progress;

            ctx.fillStyle = `rgba(255,255,255,${alpha * 0.8})`;
            ctx.beginPath();
            ctx.arc(screenX, screenY, size, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }
}

// ============================================
// 关卡数据
// ============================================
const LEVELS = [
    {
        id: 1,
        name: "Getting Started",
        birds: ['red', 'red', 'red'],
        structures: [
            { type: 'block', x: 800, y: 520, w: 20, h: 100, material: 'wood' },
            { type: 'block', x: 900, y: 520, w: 20, h: 100, material: 'wood' },
            { type: 'block', x: 850, y: 460, w: 120, h: 20, material: 'wood' },
            { type: 'pig', x: 850, y: 530, size: 'medium' }
        ],
        starScores: [1000, 2500, 4000]
    },
    {
        id: 2,
        name: "Glass House",
        birds: ['red', 'yellow', 'red'],
        structures: [
            { type: 'block', x: 750, y: 540, w: 20, h: 80, material: 'glass' },
            { type: 'block', x: 850, y: 540, w: 20, h: 80, material: 'glass' },
            { type: 'block', x: 950, y: 540, w: 20, h: 80, material: 'glass' },
            { type: 'block', x: 800, y: 490, w: 120, h: 15, material: 'glass' },
            { type: 'block', x: 900, y: 490, w: 120, h: 15, material: 'glass' },
            { type: 'pig', x: 800, y: 545, size: 'small' },
            { type: 'pig', x: 900, y: 545, size: 'small' }
        ],
        starScores: [1500, 3000, 5000]
    },
    {
        id: 3,
        name: "Stone Fortress",
        birds: ['red', 'red', 'black'],
        structures: [
            { type: 'block', x: 700, y: 520, w: 30, h: 100, material: 'stone' },
            { type: 'block', x: 850, y: 520, w: 30, h: 100, material: 'stone' },
            { type: 'block', x: 1000, y: 520, w: 30, h: 100, material: 'stone' },
            { type: 'block', x: 775, y: 460, w: 180, h: 25, material: 'wood' },
            { type: 'block', x: 925, y: 460, w: 180, h: 25, material: 'wood' },
            { type: 'block', x: 850, y: 400, w: 320, h: 20, material: 'stone' },
            { type: 'pig', x: 775, y: 540, size: 'medium' },
            { type: 'pig', x: 925, y: 540, size: 'medium' },
            { type: 'pig', x: 850, y: 365, size: 'large' }
        ],
        starScores: [2000, 4500, 7000]
    },
    {
        id: 4,
        name: "TNT Surprise",
        birds: ['yellow', 'red', 'yellow'],
        structures: [
            { type: 'block', x: 800, y: 540, w: 20, h: 80, material: 'wood' },
            { type: 'block', x: 900, y: 540, w: 20, h: 80, material: 'wood' },
            { type: 'block', x: 850, y: 490, w: 120, h: 15, material: 'wood' },
            { type: 'tnt', x: 850, y: 460, w: 30, h: 30 },
            { type: 'pig', x: 800, y: 545, size: 'small' },
            { type: 'pig', x: 900, y: 545, size: 'small' }
        ],
        starScores: [1500, 3500, 5500]
    },
    {
        id: 5,
        name: "Tower Challenge",
        birds: ['red', 'black', 'yellow', 'red'],
        structures: [
            { type: 'block', x: 850, y: 540, w: 25, h: 80, material: 'stone' },
            { type: 'block', x: 950, y: 540, w: 25, h: 80, material: 'stone' },
            { type: 'block', x: 900, y: 490, w: 130, h: 20, material: 'wood' },
            { type: 'block', x: 875, y: 430, w: 20, h: 80, material: 'glass' },
            { type: 'block', x: 925, y: 430, w: 20, h: 80, material: 'glass' },
            { type: 'block', x: 900, y: 380, w: 80, h: 15, material: 'wood' },
            { type: 'tnt', x: 900, y: 350, w: 25, h: 25 },
            { type: 'pig', x: 900, y: 540, size: 'large' },
            { type: 'pig', x: 900, y: 330, size: 'small' }
        ],
        starScores: [2500, 5000, 8000]
    },
    {
        id: 6,
        name: "Glass Castle",
        birds: ['yellow', 'yellow', 'red'],
        structures: [
            { type: 'block', x: 700, y: 550, w: 15, h: 60, material: 'glass' },
            { type: 'block', x: 800, y: 550, w: 15, h: 60, material: 'glass' },
            { type: 'block', x: 900, y: 550, w: 15, h: 60, material: 'glass' },
            { type: 'block', x: 1000, y: 550, w: 15, h: 60, material: 'glass' },
            { type: 'block', x: 750, y: 510, w: 120, h: 12, material: 'glass' },
            { type: 'block', x: 950, y: 510, w: 120, h: 12, material: 'glass' },
            { type: 'block', x: 750, y: 460, w: 15, h: 80, material: 'glass' },
            { type: 'block', x: 950, y: 460, w: 15, h: 80, material: 'glass' },
            { type: 'block', x: 850, y: 410, w: 230, h: 12, material: 'glass' },
            { type: 'pig', x: 750, y: 555, size: 'small' },
            { type: 'pig', x: 850, y: 555, size: 'small' },
            { type: 'pig', x: 950, y: 555, size: 'small' },
            { type: 'pig', x: 850, y: 385, size: 'medium' }
        ],
        starScores: [2000, 4000, 6500]
    }
];

// ============================================
// 游戏主类
// ============================================
const Game = {
    canvas: null,
    ctx: null,
    camera: { x: 0, y: 0 },
    particles: null,
    slingshot: null,
    birds: [],
    currentBirdIndex: 0,
    currentBird: null,
    blocks: [],
    pigs: [],
    score: 0,
    combo: 0,
    comboTimer: 0,
    gameState: 'menu', // menu, playing, paused, ended
    currentLevel: null,
    levelStars: [0, 0, 0, 0, 0, 0],
    isPulling: false,
    pullStart: null,
    mousePos: { x: 0, y: 0 },
    animationFrame: null,
    damagePopups: [],

    init() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = CONFIG.CANVAS_WIDTH;
        this.canvas.height = CONFIG.CANVAS_HEIGHT;

        this.particles = new ParticleSystem(500);
        this.slingshot = new Slingshot(
            CONFIG.SLINGSHOT.X, 
            CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT - 60
        );

        this.setupEventListeners();
        this.generateLevelGrid();
        this.gameLoop();
    },

    setupEventListeners() {
        // 鼠标事件
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));

        // 触摸事件
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            this.onMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
        });
        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            this.onMouseMove({ clientX: touch.clientX, clientY: touch.clientY });
        });
        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.onMouseUp({});
        });

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                this.useSkill();
            }
            if (e.code === 'Escape') {
                if (this.gameState === 'playing') {
                    this.pause();
                } else if (this.gameState === 'paused') {
                    this.resume();
                }
            }
        });
    },

    onMouseDown(e) {
        if (this.gameState !== 'playing') return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (this.currentBird && !this.currentBird.launched) {
            const birdScreenX = this.slingshot.pullX - this.camera.x;
            const birdScreenY = this.slingshot.pullY - this.camera.y;
            const dist = Utils.distance(x, y, birdScreenX, birdScreenY);

            if (dist < 40) {
                this.isPulling = true;
                this.pullStart = { x: this.slingshot.pullX, y: this.slingshot.pullY };
                document.getElementById('powerIndicator').classList.add('visible');
            }
        }
    },

    onMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.mousePos.x = e.clientX - rect.left;
        this.mousePos.y = e.clientY - rect.top;

        if (this.isPulling && this.currentBird) {
            let pullX = this.mousePos.x + this.camera.x;
            let pullY = this.mousePos.y + this.camera.y;

            // 限制拉伸范围
            const dx = pullX - this.slingshot.x;
            const dy = pullY - this.slingshot.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > CONFIG.SLINGSHOT.MAX_STRETCH) {
                const angle = Math.atan2(dy, dx);
                pullX = this.slingshot.x + Math.cos(angle) * CONFIG.SLINGSHOT.MAX_STRETCH;
                pullY = this.slingshot.y + Math.sin(angle) * CONFIG.SLINGSHOT.MAX_STRETCH;
            }

            this.slingshot.pullX = pullX;
            this.slingshot.pullY = pullY;
            this.currentBird.position.x = pullX;
            this.currentBird.position.y = pullY;
            this.slingshot.pulling = true;

            // 更新力量条
            const power = Utils.clamp(dist / CONFIG.SLINGSHOT.MAX_STRETCH * 100, 0, 100);
            document.getElementById('powerFill').style.width = power + '%';
        }
    },

    onMouseUp(e) {
        if (!this.isPulling || !this.currentBird) return;

        this.isPulling = false;
        document.getElementById('powerIndicator').classList.remove('visible');

        const dx = this.slingshot.x - this.slingshot.pullX;
        const dy = this.slingshot.y - this.slingshot.pullY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > 10) {
            // 发射小鸟
            const power = Math.min(dist * CONFIG.BIRD.LAUNCH_POWER, CONFIG.BIRD.MAX_POWER);
            const angle = Math.atan2(dy, dx);
            
            this.currentBird.velocity.x = Math.cos(angle) * power;
            this.currentBird.velocity.y = Math.sin(angle) * power;
            this.currentBird.launched = true;

            this.showToast(`${this.currentBird.type.toUpperCase()} BIRD LAUNCHED!`, 'success');
        } else {
            // 重置位置
            this.currentBird.position.x = this.slingshot.x;
            this.currentBird.position.y = this.slingshot.y - 20;
            this.slingshot.pullX = this.slingshot.x;
            this.slingshot.pullY = this.slingshot.y - 20;
        }

        this.slingshot.pulling = false;
    },

    useSkill() {
        if (this.gameState !== 'playing') return;
        if (!this.currentBird || !this.currentBird.launched || this.currentBird.skillUsed) return;

        const result = this.currentBird.useSkill();
        if (result) {
            this.showToast('SKILL ACTIVATED!', 'warning');
            
            if (result.type === 'explode') {
                // 爆炸效果
                this.particles.emit(result.position.x, result.position.y, CONFIG.MATERIALS.tnt.particles);
                
                // 对范围内物体造成伤害
                for (const block of this.blocks) {
                    if (block.destroyed) continue;
                    const dist = Utils.distance(result.position.x, result.position.y, 
                        block.position.x, block.position.y);
                    if (dist < result.radius) {
                        const damage = (1 - dist / result.radius) * 80;
                        if (block.takeDamage(damage)) {
                            this.particles.emit(block.position.x, block.position.y, block.material.particles);
                            this.addScore(100);
                        }
                    }
                }

                for (const pig of this.pigs) {
                    if (!pig.alive) continue;
                    const dist = Utils.distance(result.position.x, result.position.y, 
                        pig.position.x, pig.position.y);
                    if (dist < result.radius) {
                        if (pig.takeDamage(100)) {
                            this.addScore(500);
                        }
                    }
                }
            } else {
                // 加速/增强效果
                this.particles.emit(result.position.x, result.position.y, {
                    type: 'spark',
                    colors: ['#FFD700', '#FFA500', '#FF6347'],
                    count: { min: 15, max: 25 },
                    size: { min: 3, max: 8 },
                    speed: { min: 3, max: 8 },
                    life: { min: 20, max: 40 },
                    gravity: 0.05
                });
            }

            // 更新技能按钮
            document.getElementById('skillBtn').classList.add('cooldown');
        }
    },

    generateLevelGrid() {
        const grid = document.getElementById('levelGrid');
        grid.innerHTML = '';

        for (let i = 0; i < 6; i++) {
            const card = document.createElement('div');
            card.className = 'level-card' + (i > 0 && this.levelStars[i-1] === 0 ? ' locked' : '');
            
            const number = document.createElement('div');
            number.className = 'level-number';
            number.textContent = i + 1;
            card.appendChild(number);

            const stars = document.createElement('div');
            stars.className = 'level-stars';
            for (let j = 0; j < 3; j++) {
                const star = document.createElement('span');
                star.className = 'star' + (j < this.levelStars[i] ? ' filled' : '');
                star.textContent = '★';
                stars.appendChild(star);
            }
            card.appendChild(stars);

            if (!card.classList.contains('locked')) {
                card.onclick = () => this.startLevel(i);
            }

            grid.appendChild(card);
        }
    },

    showLevelSelect() {
        document.getElementById('mainMenu').classList.add('hidden');
        document.getElementById('levelSelect').classList.add('visible');
        document.getElementById('levelSelect').classList.remove('hidden');
        this.generateLevelGrid();
    },

    hideLevelSelect() {
        document.getElementById('levelSelect').classList.remove('visible');
        document.getElementById('levelSelect').classList.add('hidden');
        setTimeout(() => {
            document.getElementById('mainMenu').classList.remove('hidden');
        }, 300);
    },

    showTutorial() {
        this.showToast('Drag the bird to aim, release to launch!', 'success');
        this.showLevelSelect();
    },

    startLevel(index) {
        this.currentLevel = LEVELS[index];
        this.currentLevelIndex = index;
        
        document.getElementById('levelSelect').classList.remove('visible');
        document.getElementById('levelSelect').classList.add('hidden');
        
        // 显示关卡过渡
        const transition = document.getElementById('levelTransition');
        document.getElementById('transitionNumber').textContent = index + 1;
        transition.classList.add('visible');

        setTimeout(() => {
            transition.classList.remove('visible');
            this.loadLevel(this.currentLevel);
        }, 1500);
    },

    loadLevel(level) {
        // 清理旧数据
        this.birds = [];
        this.blocks = [];
        this.pigs = [];
        this.score = 0;
        this.combo = 0;
        this.currentBirdIndex = 0;
        this.damagePopups = [];

        // 创建小鸟
        for (const birdType of level.birds) {
            const bird = new Bird(
                this.slingshot.x,
                this.slingshot.y - 20,
                birdType
            );
            this.birds.push(bird);
        }

        // 创建结构
        for (const struct of level.structures) {
            if (struct.type === 'block') {
                this.blocks.push(new RigidBody(struct.x, struct.y, struct.w, struct.h, struct.material));
            } else if (struct.type === 'pig') {
                this.pigs.push(new Pig(struct.x, struct.y, struct.size));
            } else if (struct.type === 'tnt') {
                const tnt = new RigidBody(struct.x, struct.y, struct.w, struct.h, 'tnt');
                tnt.isTNT = true;
                this.blocks.push(tnt);
            }
        }

        // 准备第一只小鸟
        this.currentBird = this.birds[0];
        this.slingshot.pullX = this.slingshot.x;
        this.slingshot.pullY = this.slingshot.y - 20;

        // 显示游戏UI
        document.getElementById('gameHud').style.display = 'flex';
        document.getElementById('controlsHint').style.display = 'flex';
        document.getElementById('skillBtn').style.display = 'flex';
        document.getElementById('skillBtn').classList.remove('cooldown');

        this.updateHUD();
        this.gameState = 'playing';

        // 重置相机
        this.camera.x = 0;
    },

    pause() {
        if (this.gameState !== 'playing') return;
        this.gameState = 'paused';
        document.getElementById('pauseMenu').classList.add('visible');
    },

    resume() {
        if (this.gameState !== 'paused') return;
        this.gameState = 'playing';
        document.getElementById('pauseMenu').classList.remove('visible');
    },

    restart() {
        document.getElementById('pauseMenu').classList.remove('visible');
        document.getElementById('resultPopup').classList.remove('visible');
        if (this.currentLevel) {
            this.loadLevel(this.currentLevel);
        }
    },

    quit() {
        document.getElementById('pauseMenu').classList.remove('visible');
        document.getElementById('resultPopup').classList.remove('visible');
        document.getElementById('gameHud').style.display = 'none';
        document.getElementById('controlsHint').style.display = 'none';
        document.getElementById('skillBtn').style.display = 'none';
        document.getElementById('mainMenu').classList.remove('hidden');
        this.gameState = 'menu';
    },

    nextLevel() {
        document.getElementById('resultPopup').classList.remove('visible');
        const nextIndex = this.currentLevelIndex + 1;
        if (nextIndex < LEVELS.length) {
            this.startLevel(nextIndex);
        } else {
            this.quit();
            this.showToast('Congratulations! You completed all levels!', 'success');
        }
    },

    addScore(points) {
        this.combo++;
        this.comboTimer = 120;
        const multiplier = Math.min(this.combo, 5);
        this.score += points * multiplier;
        this.updateHUD();

        // 显示连击
        if (this.combo >= 2) {
            const comboDisplay = document.getElementById('comboDisplay');
            document.getElementById('comboMultiplier').textContent = `x${multiplier}`;
            comboDisplay.classList.add('visible');
        }
    },

    updateHUD() {
        document.getElementById('scoreValue').textContent = this.score.toLocaleString();
        
        // 更新小鸟显示
        const birdsDiv = document.getElementById('birdsRemaining');
        birdsDiv.innerHTML = '';
        for (let i = 0; i < this.birds.length; i++) {
            const icon = document.createElement('div');
            icon.className = 'bird-icon ' + this.birds[i].type + (i < this.currentBirdIndex ? ' used' : ' available');
            icon.textContent = '🐦';
            birdsDiv.appendChild(icon);
        }

        // 更新技能按钮
        const skillBtn = document.getElementById('skillBtn');
        skillBtn.className = 'skill-btn ' + this.currentBird?.type + '-skill';
        if (this.currentBird?.skillUsed) {
            skillBtn.classList.add('cooldown');
        }
    },

    showDamagePopup(x, y, damage, color = '#FF6B35') {
        const popup = document.createElement('div');
        popup.className = 'damage-popup';
        popup.textContent = '+' + damage;
        popup.style.left = (x - this.camera.x) + 'px';
        popup.style.top = (y - this.camera.y) + 'px';
        popup.style.color = color;
        document.getElementById('uiOverlay').appendChild(popup);

        setTimeout(() => popup.remove(), 1000);
    },

    showResult(won) {
        const popup = document.getElementById('resultPopup');
        const title = document.getElementById('resultTitle');
        
        title.textContent = won ? 'Victory!' : 'Level Failed';
        title.className = 'result-title ' + (won ? 'win' : 'lose');
        
        document.getElementById('finalScore').textContent = this.score.toLocaleString();

        // 计算星星
        let stars = 0;
        if (won) {
            const levelScores = this.currentLevel.starScores;
            if (this.score >= levelScores[0]) stars = 1;
            if (this.score >= levelScores[1]) stars = 2;
            if (this.score >= levelScores[2]) stars = 3;
            
            this.levelStars[this.currentLevelIndex] = Math.max(this.levelStars[this.currentLevelIndex], stars);
        }

        // 显示星星动画
        const starsDiv = document.getElementById('resultStars');
        starsDiv.innerHTML = '';
        for (let i = 0; i < 3; i++) {
            const star = document.createElement('span');
            star.className = 'result-star' + (i < stars ? ' filled' : '');
            star.textContent = '★';
            starsDiv.appendChild(star);

            setTimeout(() => {
                star.classList.add('animate');
            }, 200 + i * 200);
        }

        popup.classList.add('visible');
    },

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = 'toast ' + type;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
        }, CONFIG.UI.TOAST_DURATION);
    },

    checkCollisions() {
        if (!this.currentBird || !this.currentBird.launched || this.currentBird.stopped) return;

        const bird = this.currentBird;
        
        // 小鸟与方块碰撞
        for (const block of this.blocks) {
            if (block.destroyed) continue;

            const bounds = block.getBounds();
            const closestX = Utils.clamp(bird.position.x, bounds.left, bounds.right);
            const closestY = Utils.clamp(bird.position.y, bounds.top, bounds.bottom);
            const dist = Utils.distance(bird.position.x, bird.position.y, closestX, closestY);

            if (dist < bird.radius) {
                // 碰撞发生
                const impactSpeed = bird.velocity.length();
                const damage = impactSpeed * 5 * (bird.skillActive ? 2 : 1);

                if (block.takeDamage(damage)) {
                    // 方块被摧毁
                    this.particles.emit(block.position.x, block.position.y, block.material.particles);
                    
                    // TNT爆炸
                    if (block.isTNT) {
                        this.handleExplosion(block.position.x, block.position.y);
                    }
                    
                    this.addScore(100);
                    this.showDamagePopup(block.position.x, block.position.y, 100);
                } else {
                    // 碰撞粒子
                    this.particles.emit(closestX, closestY, {
                        type: 'spark',
                        colors: [block.material.colors.light],
                        count: { min: 5, max: 10 },
                        size: { min: 2, max: 5 },
                        speed: { min: 2, max: 5 },
                        life: { min: 15, max: 30 },
                        gravity: 0.1
                    });
                }

                // 反弹
                const normal = new Vector2(bird.position.x - closestX, bird.position.y - closestY).normalize();
                const relVel = bird.velocity;
                const velAlongNormal = relVel.dot(normal);
                
                if (velAlongNormal < 0) {
                    const restitution = block.material.restitution;
                    bird.velocity.x -= (1 + restitution) * velAlongNormal * normal.x;
                    bird.velocity.y -= (1 + restitution) * velAlongNormal * normal.y;
                }

                // 推动方块
                block.velocity.x += bird.velocity.x * 0.3;
                block.velocity.y += bird.velocity.y * 0.3;
                block.angularVelocity += (closestX - block.position.x) * 0.01;
            }
        }

        // 小鸟与猪碰撞
        for (const pig of this.pigs) {
            if (!pig.alive) continue;

            const dist = Utils.distance(bird.position.x, bird.position.y, 
                pig.position.x, pig.position.y);

            if (dist < bird.radius + pig.radius) {
                const impactSpeed = bird.velocity.length();
                const damage = impactSpeed * 8 * (bird.skillActive ? 2 : 1);

                if (pig.takeDamage(damage)) {
                    // 猪被消灭
                    this.particles.emit(pig.position.x, pig.position.y, {
                        type: 'feather',
                        colors: ['#7CB342', '#9CCC65', '#C5E1A5'],
                        count: { min: 15, max: 25 },
                        size: { min: 4, max: 10 },
                        speed: { min: 3, max: 8 },
                        life: { min: 40, max: 80 },
                        gravity: 0.15,
                        rotation: true
                    });
                    this.addScore(500);
                    this.showDamagePopup(pig.position.x, pig.position.y, 500, '#7ED321');
                }

                // 反弹
                bird.velocity.x *= -0.5;
                bird.velocity.y *= -0.5;
            }
        }
    },

    handleExplosion(x, y) {
        this.particles.emit(x, y, CONFIG.MATERIALS.tnt.particles);
        
        // 对范围内物体造成伤害
        for (const block of this.blocks) {
            if (block.destroyed) continue;
            const dist = Utils.distance(x, y, block.position.x, block.position.y);
            if (dist < CONFIG.MATERIALS.tnt.explosionRadius) {
                const damage = (1 - dist / CONFIG.MATERIALS.tnt.explosionRadius) * CONFIG.MATERIALS.tnt.explosionDamage;
                if (block.takeDamage(damage)) {
                    this.particles.emit(block.position.x, block.position.y, block.material.particles);
                    this.addScore(100);
                }
            }
        }

        for (const pig of this.pigs) {
            if (!pig.alive) continue;
            const dist = Utils.distance(x, y, pig.position.x, pig.position.y);
            if (dist < CONFIG.MATERIALS.tnt.explosionRadius) {
                if (pig.takeDamage(CONFIG.MATERIALS.tnt.explosionDamage)) {
                    this.addScore(500);
                }
            }
        }
    },

    checkGameState() {
        // 检查是否所有猪都被消灭
        const allPigsDead = this.pigs.every(p => !p.alive);
        
        // 检查是否所有小鸟都用完了
        const allBirdsUsed = this.currentBirdIndex >= this.birds.length - 1 && 
            this.currentBird && this.currentBird.stopped;

        if (allPigsDead) {
            setTimeout(() => this.showResult(true), 1000);
            this.gameState = 'ended';
            return;
        }

        if (allBirdsUsed && !allPigsDead) {
            setTimeout(() => this.showResult(false), 1000);
            this.gameState = 'ended';
            return;
        }

        // 检查是否需要切换小鸟
        if (this.currentBird && this.currentBird.stopped && !allPigsDead) {
            this.currentBirdIndex++;
            if (this.currentBirdIndex < this.birds.length) {
                this.currentBird = this.birds[this.currentBirdIndex];
                this.currentBird.position.x = this.slingshot.x;
                this.currentBird.position.y = this.slingshot.y - 20;
                this.slingshot.pullX = this.slingshot.x;
                this.slingshot.pullY = this.slingshot.y - 20;
                
                document.getElementById('skillBtn').classList.remove('cooldown');
                this.updateHUD();

                // 重置相机
                this.camera.x = 0;
            }
        }
    },

    update() {
        if (this.gameState !== 'playing') return;

        // 更新连击计时
        if (this.comboTimer > 0) {
            this.comboTimer--;
            if (this.comboTimer <= 0) {
                this.combo = 0;
                document.getElementById('comboDisplay').classList.remove('visible');
            }
        }

        // 更新粒子
        this.particles.update();

        // 更新方块
        for (const block of this.blocks) {
            block.update();
        }

        // 清理被摧毁的方块
        this.blocks = this.blocks.filter(b => !b.destroyed);

        // 更新猪
        for (const pig of this.pigs) {
            pig.update();
        }

        // 更新小鸟
        if (this.currentBird) {
            this.currentBird.update(this.camera);

            // 跟随相机
            if (this.currentBird.launched && !this.currentBird.stopped) {
                const targetX = this.currentBird.position.x - CONFIG.CANVAS_WIDTH / 3;
                this.camera.x = Utils.lerp(this.camera.x, targetX, CONFIG.CAMERA_LERP);
                this.camera.x = Utils.clamp(this.camera.x, 0, CONFIG.WORLD_WIDTH - CONFIG.CANVAS_WIDTH);
            }

            // 发射拖尾
            if (this.currentBird.launched && !this.currentBird.stopped) {
                this.particles.emitTrail(
                    this.currentBird.position.x,
                    this.currentBird.position.y,
                    this.currentBird.colors.light,
                    5
                );
            }
        }

        // 碰撞检测
        this.checkCollisions();

        // 检查游戏状态
        this.checkGameState();
    },

    render() {
        const ctx = this.ctx;

        // 清空画布
        ctx.clearRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

        // 绘制天空渐变背景
        const skyGradient = ctx.createLinearGradient(0, 0, 0, CONFIG.CANVAS_HEIGHT);
        skyGradient.addColorStop(0, '#87CEEB');
        skyGradient.addColorStop(0.5, '#B0E0E6');
        skyGradient.addColorStop(1, '#E0F7FA');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

        // 绘制云朵
        this.renderClouds(ctx);

        // 绘制远山
        this.renderMountains(ctx);

        // 绘制地面
        const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT;
        
        // 草地
        const grassGradient = ctx.createLinearGradient(0, groundY, 0, CONFIG.CANVAS_HEIGHT);
        grassGradient.addColorStop(0, '#7CB342');
        grassGradient.addColorStop(0.2, '#689F38');
        grassGradient.addColorStop(1, '#558B2F');
        ctx.fillStyle = grassGradient;
        ctx.fillRect(0, groundY, CONFIG.CANVAS_WIDTH, CONFIG.GROUND_HEIGHT);

        // 草地纹理
        ctx.strokeStyle = '#8BC34A';
        ctx.lineWidth = 2;
        for (let x = 0; x < CONFIG.CANVAS_WIDTH; x += 15) {
            const height = 5 + Math.sin(x * 0.1 + Date.now() * 0.001) * 3;
            ctx.beginPath();
            ctx.moveTo(x, groundY);
            ctx.lineTo(x + 3, groundY - height);
            ctx.stroke();
        }

        // 绘制方块
        for (const block of this.blocks) {
            block.render(ctx, this.camera);
        }

        // 绘制猪
        for (const pig of this.pigs) {
            pig.render(ctx, this.camera);
        }

        // 绘制弹弓
        this.slingshot.render(ctx, this.camera, this.currentBird);

        // 绘制轨迹预测
        if (this.isPulling && this.currentBird) {
            const dx = this.slingshot.x - this.slingshot.pullX;
            const dy = this.slingshot.y - this.slingshot.pullY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            if (dist > 10) {
                const power = Math.min(dist * CONFIG.BIRD.LAUNCH_POWER, CONFIG.BIRD.MAX_POWER);
                const angle = Math.atan2(dy, dx);
                const velocity = new Vector2(Math.cos(angle) * power, Math.sin(angle) * power);
                this.slingshot.renderTrajectory(ctx, this.camera, velocity);
            }
        }

        // 绘制当前小鸟（在弹弓上的）
        if (this.currentBird && !this.currentBird.launched) {
            this.currentBird.render(ctx, this.camera);
        }

        // 绘制已发射的小鸟
        for (const bird of this.birds) {
            if (bird.launched) {
                bird.render(ctx, this.camera);
            }
        }

        // 绘制粒子
        this.particles.render(ctx, this.camera);
    },

    renderClouds(ctx) {
        ctx.fillStyle = 'rgba(255,255,255,0.8)';
        
        const clouds = [
            { x: 100, y: 80, scale: 1 },
            { x: 400, y: 120, scale: 0.8 },
            { x: 700, y: 60, scale: 1.2 },
            { x: 1000, y: 100, scale: 0.9 }
        ];

        for (const cloud of clouds) {
            const x = (cloud.x - this.camera.x * 0.1) % (CONFIG.CANVAS_WIDTH + 200);
            
            ctx.beginPath();
            ctx.arc(x, cloud.y, 30 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(x + 25 * cloud.scale, cloud.y - 10, 25 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(x + 50 * cloud.scale, cloud.y, 30 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(x + 25 * cloud.scale, cloud.y + 10, 20 * cloud.scale, 0, Math.PI * 2);
            ctx.fill();
        }
    },

    renderMountains(ctx) {
        const groundY = CONFIG.CANVAS_HEIGHT - CONFIG.GROUND_HEIGHT;

        // 远山
        ctx.fillStyle = '#A5D6A7';
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        
        for (let x = 0; x <= CONFIG.CANVAS_WIDTH; x += 50) {
            const y = groundY - 80 - Math.sin((x + this.camera.x * 0.05) * 0.01) * 40;
            ctx.lineTo(x, y);
        }
        
        ctx.lineTo(CONFIG.CANVAS_WIDTH, groundY);
        ctx.closePath();
        ctx.fill();

        // 近山
        ctx.fillStyle = '#81C784';
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        
        for (let x = 0; x <= CONFIG.CANVAS_WIDTH; x += 30) {
            const y = groundY - 40 - Math.sin((x + this.camera.x * 0.1) * 0.02) * 20;
            ctx.lineTo(x, y);
        }
        
        ctx.lineTo(CONFIG.CANVAS_WIDTH, groundY);
        ctx.closePath();
        ctx.fill();
    },

    gameLoop() {
        this.update();
        this.render();
        this.animationFrame = requestAnimationFrame(() => this.gameLoop());
    }
};

// 初始化游戏
window.onload = () => Game.init();
    </script>
</body>
</html>
```

这个完整的愤怒的小鸟游戏包含了以下UI和视觉polish功能：

**UI系统：**
1. **开始菜单** - 带有弹跳动画的标题，渐变背景，3D风格按钮
2. **关卡选择** - 网格布局的关卡卡片，星星评分显示，锁定机制
3. **暂停界面** - 居中弹窗，带弹性动画
4. **结算弹窗** - 胜利/失败状态，星星动画，分数显示

**动画效果：**
1. **弹性动画** - 使用cubic-bezier实现弹性过渡
2. **按钮反馈** - 悬停放大、按下缩小、涟漪效果
3. **分数弹出** - 伤害数字浮动动画
4. **星星动画** - 旋转弹入效果
5. **关卡过渡** - 数字脉冲动画

**视觉特效：**
1. **飞行拖尾** - 小鸟飞行时的渐变轨迹
2. **技能触发** - 闪光粒子效果
3. **破坏粒子** - 多种类型（碎片、玻璃、灰尘、爆炸）
4. **卡通风格** - 明快的色彩、圆角设计、渐变高光

**交互反馈：**
1. **Toast通知** - 滑入滑出动画
2. **连击显示** - 缩放弹出效果
3. **力量指示器** - 实时显示发射力度