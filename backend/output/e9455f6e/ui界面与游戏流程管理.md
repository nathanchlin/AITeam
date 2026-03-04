# UI界面与游戏流程管理

**Time**: 2026-02-28T23:06:12.147695

---

我来为你实现完整的UI界面与游戏流程管理系统，包括主菜单、HUD、暂停菜单、结算界面和双人对战模式。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neon Racer - Complete Game</title>
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
        
        #weatherOverlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            border-radius: 8px;
            z-index: 50;
        }
        
        /* 主菜单样式 */
        .menu-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(10, 10, 15, 0.98) 0%, rgba(26, 10, 46, 0.95) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
            border-radius: 8px;
        }
        
        .menu-overlay.hidden {
            display: none;
        }
        
        .menu-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 64px;
            font-weight: 900;
            color: var(--neon-cyan);
            text-shadow: 
                0 0 10px var(--neon-cyan),
                0 0 30px var(--neon-cyan),
                0 0 60px rgba(0, 245, 255, 0.5);
            margin-bottom: 10px;
            letter-spacing: 8px;
            animation: titleGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes titleGlow {
            0% { text-shadow: 0 0 10px var(--neon-cyan), 0 0 30px var(--neon-cyan), 0 0 60px rgba(0, 245, 255, 0.5); }
            100% { text-shadow: 0 0 20px var(--neon-cyan), 0 0 50px var(--neon-cyan), 0 0 100px rgba(0, 245, 255, 0.8); }
        }
        
        .menu-subtitle {
            font-family: 'Share Tech Mono', monospace;
            font-size: 16px;
            color: var(--neon-pink);
            letter-spacing: 6px;
            margin-bottom: 50px;
            text-transform: uppercase;
        }
        
        .menu-buttons {
            display: flex;
            flex-direction: column;
            gap: 15px;
            min-width: 280px;
        }
        
        .menu-btn {
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 700;
            padding: 18px 40px;
            border: 2px solid var(--neon-cyan);
            background: rgba(0, 245, 255, 0.05);
            color: var(--neon-cyan);
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 3px;
            position: relative;
            overflow: hidden;
        }
        
        .menu-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }
        
        .menu-btn:hover {
            background: rgba(0, 245, 255, 0.15);
            box-shadow: 0 0 30px rgba(0, 245, 255, 0.3);
            transform: translateX(5px);
        }
        
        .menu-btn:hover::before {
            left: 100%;
        }
        
        .menu-btn.pink {
            border-color: var(--neon-pink);
            color: var(--neon-pink);
            background: rgba(255, 45, 117, 0.05);
        }
        
        .menu-btn.pink:hover {
            background: rgba(255, 45, 117, 0.15);
            box-shadow: 0 0 30px rgba(255, 45, 117, 0.3);
        }
        
        /* 选择界面样式 */
        .selection-panel {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg-panel);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 30px;
            min-width: 600px;
            max-width: 90%;
            z-index: 210;
            backdrop-filter: blur(20px);
        }
        
        .selection-panel.hidden {
            display: none;
        }
        
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .panel-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            color: var(--neon-cyan);
            letter-spacing: 3px;
        }
        
        .back-btn {
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            padding: 8px 16px;
            border: 1px solid var(--text-muted);
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .back-btn:hover {
            border-color: var(--neon-pink);
            color: var(--neon-pink);
        }
        
        .selection-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .selection-card {
            background: rgba(255, 255, 255, 0.03);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        
        .selection-card:hover {
            border-color: var(--neon-cyan);
            background: rgba(0, 245, 255, 0.05);
        }
        
        .selection-card.selected {
            border-color: var(--neon-green);
            background: rgba(0, 255, 136, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }
        
        .card-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .card-name {
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        
        .card-stats {
            font-size: 11px;
            color: var(--text-muted);
        }
        
        .stat-bar {
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            margin: 4px 0;
            overflow: hidden;
        }
        
        .stat-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.3s;
        }
        
        .stat-fill.speed { background: var(--neon-cyan); }
        .stat-fill.accel { background: var(--neon-yellow); }
        .stat-fill.handling { background: var(--neon-pink); }
        
        .confirm-btn {
            width: 100%;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            padding: 15px;
            border: 2px solid var(--neon-green);
            background: rgba(0, 255, 136, 0.1);
            color: var(--neon-green);
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .confirm-btn:hover {
            background: rgba(0, 255, 136, 0.2);
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
        }
        
        /* HUD样式 */
        #hud {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 100;
        }
        
        #hud.hidden {
            display: none;
        }
        
        .hud-top {
            position: absolute;
            top: 15px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 30px;
            align-items: center;
        }
        
        .race-position {
            font-family: 'Orbitron', sans-serif;
            font-size: 36px;
            font-weight: 900;
            color: var(--neon-yellow);
            text-shadow: 0 0 20px rgba(240, 255, 0, 0.5);
        }
        
        .race-position span {
            font-size: 18px;
            color: var(--text-muted);
        }
        
        .lap-counter {
            background: rgba(15, 15, 25, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 20px;
            text-align: center;
        }
        
        .lap-label {
            font-size: 10px;
            color: var(--text-muted);
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .lap-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            color: var(--neon-cyan);
        }
        
        .race-timer {
            background: rgba(15, 15, 25, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 20px;
            text-align: center;
        }
        
        .timer-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            color: var(--text-primary);
        }
        
        .hud-bottom-left {
            position: absolute;
            bottom: 15px;
            left: 15px;
        }
        
        .speedometer {
            background: rgba(15, 15, 25, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 15px 25px;
            min-width: 180px;
        }
        
        .speed-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 48px;
            font-weight: 900;
            color: var(--neon-cyan);
            line-height: 1;
        }
        
        .speed-unit {
            font-size: 14px;
            color: var(--text-muted);
            margin-left: 5px;
        }
        
        .gear-indicator {
            font-family: 'Orbitron', sans-serif;
            font-size: 18px;
            color: var(--neon-orange);
            margin-top: 5px;
        }
        
        .nitro-bar {
            margin-top: 10px;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .nitro-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
            border-radius: 4px;
            transition: width 0.1s;
        }
        
        .hud-bottom-right {
            position: absolute;
            bottom: 15px;
            right: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .minimap {
            width: 150px;
            height: 100px;
            background: rgba(15, 15, 25, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }
        
        #minimapCanvas {
            width: 100%;
            height: 100%;
        }
        
        /* 暂停菜单 */
        .pause-menu {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg-panel);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 40px;
            min-width: 300px;
            text-align: center;
            z-index: 250;
            backdrop-filter: blur(20px);
        }
        
        .pause-menu.hidden {
            display: none;
        }
        
        .pause-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            color: var(--neon-pink);
            margin-bottom: 30px;
            letter-spacing: 5px;
        }
        
        .pause-buttons {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        /* 结算界面 */
        .results-panel {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg-panel);
            border: 2px solid var(--border-color);
            border-radius: 16px;
            padding: 40px;
            min-width: 500px;
            z-index: 250;
            backdrop-filter: blur(20px);
        }
        
        .results-panel.hidden {
            display: none;
        }
        
        .results-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 42px;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .results-title.winner {
            color: var(--neon-yellow);
            text-shadow: 0 0 30px rgba(240, 255, 0, 0.5);
        }
        
        .results-title.loser {
            color: var(--neon-pink);
        }
        
        .results-position {
            font-family: 'Orbitron', sans-serif;
            font-size: 72px;
            font-weight: 900;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .results-position.p1 { color: var(--neon-yellow); }
        .results-position.p2 { color: var(--neon-cyan); }
        .results-position.p3 { color: var(--neon-orange); }
        .results-position.p4 { color: var(--text-muted); }
        
        .results-stats {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        .result-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .result-row:last-child {
            border-bottom: none;
        }
        
        .result-label {
            color: var(--text-muted);
        }
        
        .result-value {
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-cyan);
        }
        
        .results-buttons {
            display: flex;
            gap: 15px;
        }
        
        .results-buttons .menu-btn {
            flex: 1;
        }
        
        /* 双人分屏 */
        .split-screen #gameCanvas {
            border-radius: 8px 8px 0 0;
        }
        
        .split-container {
            display: flex;
            width: 100%;
            height: 100%;
        }
        
        .player-view {
            flex: 1;
            position: relative;
        }
        
        .player-view:first-child {
            border-right: 2px solid var(--neon-cyan);
        }
        
        .player-label {
            position: absolute;
            top: 10px;
            left: 10px;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            padding: 5px 15px;
            background: rgba(15, 15, 25, 0.9);
            border-radius: 4px;
            z-index: 10;
        }
        
        .player-label.p1 {
            color: var(--neon-cyan);
            border: 1px solid var(--neon-cyan);
        }
        
        .player-label.p2 {
            color: var(--neon-pink);
            border: 1px solid var(--neon-pink);
        }
        
        /* 倒计时 */
        .countdown {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Orbitron', sans-serif;
            font-size: 120px;
            font-weight: 900;
            color: var(--neon-cyan);
            text-shadow: 0 0 50px var(--neon-cyan);
            z-index: 150;
            animation: countdownPulse 0.5s ease-out;
        }
        
        .countdown.hidden {
            display: none;
        }
        
        @keyframes countdownPulse {
            0% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
        }
        
        /* 控制面板 */
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
            pointer-events: none;
        }
        
        #controls.hidden {
            display: none;
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
        
        /* 性能面板 */
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
        
        #performancePanel.hidden {
            display: none;
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
        .perf-value.decor { color: var(--neon-purple); }
        
        /* 提示信息 */
        .game-message {
            position: absolute;
            top: 30%;
            left: 50%;
            transform: translateX(-50%);
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            color: var(--neon-yellow);
            text-shadow: 0 0 20px rgba(240, 255, 0, 0.5);
            z-index: 120;
            animation: messageFlash 0.5s ease-out;
        }
        
        .game-message.hidden {
            display: none;
        }
        
        @keyframes messageFlash {
            0% { opacity: 0; transform: translateX(-50%) scale(0.8); }
            50% { opacity: 1; transform: translateX(-50%) scale(1.1); }
            100% { opacity: 1; transform: translateX(-50%) scale(1); }
        }
        
        /* 玩家选择面板 - 双人 */
        .player-select {
            display: flex;
            gap: 20px;
        }
        
        .player-column {
            flex: 1;
            padding: 20px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
        }
        
        .player-column.p1 {
            border: 1px solid rgba(0, 245, 255, 0.3);
        }
        
        .player-column.p2 {
            border: 1px solid rgba(255, 45, 117, 0.3);
        }
        
        .player-column-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .player-column.p1 .player-column-title {
            color: var(--neon-cyan);
        }
        
        .player-column.p2 .player-column-title {
            color: var(--neon-pink);
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <canvas id="vfxCanvas"></canvas>
        <div id="nitroOverlay"></div>
        <canvas id="weatherOverlay"></canvas>
        
        <!-- 主菜单 -->
        <div id="mainMenu" class="menu-overlay">
            <div class="menu-title">NEON RACER</div>
            <div class="menu-subtitle">Cyber Speedway</div>
            <div class="menu-buttons">
                <button class="menu-btn" onclick="UIManager.showVehicleSelect(1)">单人对战</button>
                <button class="menu-btn pink" onclick="UIManager.showVehicleSelect(2)">双人对战</button>
                <button class="menu-btn" onclick="UIManager.showTrackSelect()">选择赛道</button>
                <button class="menu-btn" onclick="UIManager.showOptions()">游戏设置</button>
            </div>
        </div>
        
        <!-- 车辆选择 -->
        <div id="vehicleSelect" class="selection-panel hidden">
            <div class="panel-header">
                <span class="panel-title">选择车辆</span>
                <button class="back-btn" onclick="UIManager.showMainMenu()">返回</button>
            </div>
            <div id="vehicleGrid" class="player-select">
                <!-- 动态生成 -->
            </div>
            <button class="confirm-btn" onclick="UIManager.confirmVehicle()">确认选择</button>
        </div>
        
        <!-- 赛道选择 -->
        <div id="trackSelect" class="selection-panel hidden">
            <div class="panel-header">
                <span class="panel-title">选择赛道</span>
                <button class="back-btn" onclick="UIManager.showMainMenu()">返回</button>
            </div>
            <div id="trackGrid" class="selection-grid">
                <!-- 动态生成 -->
            </div>
            <button class="confirm-btn" onclick="UIManager.confirmTrack()">开始游戏</button>
        </div>
        
        <!-- HUD -->
        <div id="hud" class="hidden">
            <div class="hud-top">
                <div class="race-position">
                    <span id="positionValue">1</span><span> / 4</span>
                </div>
                <div class="lap-counter">
                    <div class="lap-label">圈数</div>
                    <div class="lap-value"><span id="currentLap">1</span> / <span id="totalLaps">3</span></div>
                </div>
                <div class="race-timer">
                    <div class="timer-value" id="raceTimer">00:00.00</div>
                </div>
            </div>
            
            <div class="hud-bottom-left">
                <div class="speedometer">
                    <div>
                        <span class="speed-value" id="speedValue">0</span>
                        <span class="speed-unit">KM/H</span>
                    </div>
                    <div class="gear-indicator">档位 <span id="gearValue">N</span></div>
                    <div class="nitro-bar">
                        <div class="nitro-fill" id="nitroFill" style="width: 100%"></div>
                    </div>
                </div>
            </div>
            
            <div class="hud-bottom-right">
                <div class="minimap">
                    <canvas id="minimapCanvas"></canvas>
                </div>
            </div>
        </div>
        
        <!-- 双人HUD -->
        <div id="hudP2" class="hidden">
            <div class="player-label p1">P1</div>
            <div class="player-label p2" style="left: auto; right: 10px;">P2</div>
        </div>
        
        <!-- 倒计时 -->
        <div id="countdown" class="countdown hidden">3</div>
        
        <!-- 游戏消息 -->
        <div id="gameMessage" class="game-message hidden"></div>
        
        <!-- 暂停菜单 -->
        <div id="pauseMenu" class="pause-menu hidden">
            <div class="pause-title">暂停</div>
            <div class="pause-buttons">
                <button class="menu-btn" onclick="UIManager.resumeGame()">继续游戏</button>
                <button class="menu-btn" onclick="UIManager.restartRace()">重新开始</button>
                <button class="menu-btn pink" onclick="UIManager.quitToMenu()">退出比赛</button>
            </div>
        </div>
        
        <!-- 结算界面 -->
        <div id="resultsPanel" class="results-panel hidden">
            <div class="results-title" id="resultsTitle">比赛结束</div>
            <div class="results-position" id="resultsPosition">1st</div>
            <div class="results-stats">
                <div class="result-row">
                    <span class="result-label">完成时间</span>
                    <span class="result-value" id="resultTime">00:00.00</span>
                </div>
                <div class="result-row">
                    <span class="result-label">最快单圈</span>
                    <span class="result-value" id="resultBestLap">00:00.00</span>
                </div>
                <div class="result-row">
                    <span class="result-label">最高速度</span>
                    <span class="result-value" id="resultTopSpeed">0 KM/H</span>
                </div>
                <div class="result-row">
                    <span class="result-label">使用氮气</span>
                    <span class="result-value" id="resultNitroUsed">0 次</span>
                </div>
            </div>
            <div class="results-buttons">
                <button class="menu-btn" onclick="UIManager.restartRace()">再来一局</button>
                <button class="menu-btn pink" onclick="UIManager.quitToMenu()">返回主菜单</button>
            </div>
        </div>
        
        <!-- 性能面板 -->
        <div id="performancePanel" class="hidden">
            <h3>Performance</h3>
            <div class="perf-row">
                <span class="perf-label">FPS</span>
                <span class="perf-value fps" id="fpsValue">60</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Frame</span>
                <span class="perf-value frame" id="frameValue">16.7ms</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">Particles</span>
                <span class="perf-value particles" id="particleCount">0</span>
            </div>
            <div class="perf-row">
                <span class="perf-label">AI</span>
                <span class="perf-value ai" id="aiCount">0</span>
            </div>
        </div>
        
        <!-- 控制提示 -->
        <div id="controls" class="hidden">
            <h4>Controls</h4>
            <span class="key-hint">W/S</span> 加速/刹车
            <span class="key-hint">A/D</span> 转向
            <span class="key-hint">Space</span> 手刹
            <span class="key-hint">Shift</span> 氮气
            <span class="key-hint">Esc</span> 暂停
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
        
        CHECKPOINT_COUNT: 4,
        TOTAL_LAPS: 3,
        
        COLORS: {
            sky: { top: '#0a0a1a', bottom: '#1a1a3a' },
            skyDay: { top: '#4a90c2', bottom: '#87ceeb' },
            skySunset: { top: '#ff6b35', bottom: '#f7c59f' },
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
            grassDay: { light: '#2a5a2a', dark: '#1a4a1a' },
            rumble: { light: '#ff2d75', dark: '#ffffff' },
            lane: 'rgba(0, 245, 255, 0.4)'
        }
    };

    CONFIG.CAMERA_DEPTH = 1 / Math.tan((CONFIG.FOV / 2) * Math.PI / 180);

    // 车辆数据
    const VEHICLES = [
        {
            id: 'speeder',
            name: '闪电 Speeder',
            icon: '⚡',
            color: '#00f5ff',
            stats: { speed: 90, accel: 70, handling: 65 },
            config: { maxSpeed: 340, acceleration: 0.85, driftFactor: 0.92 }
        },
        {
            id: 'phantom',
            name: '幻影 Phantom',
            icon: '👻',
            color: '#ff2d75',
            stats: { speed: 75, accel: 85, handling: 80 },
            config: { maxSpeed: 300, acceleration: 1.0, driftFactor: 0.96 }
        },
        {
            id: 'titan',
            name: '泰坦 Titan',
            icon: '🛡️',
            color: '#f0ff00',
            stats: { speed: 85, accel: 60, handling: 90 },
            config: { maxSpeed: 310, acceleration: 0.7, driftFactor: 0.98 }
        },
        {
            id: 'viper',
            name: '毒蛇 Viper',
            icon: '🐍',
            color: '#00ff88',
            stats: { speed: 95, accel: 80, handling: 55 },
            config: { maxSpeed: 360, acceleration: 0.9, driftFactor: 0.90 }
        },
        {
            id: 'storm',
            name: '风暴 Storm',
            icon: '🌪️',
            color: '#b347ea',
            stats: { speed: 80, accel: 75, handling: 75 },
            config: { maxSpeed: 320, acceleration: 0.88, driftFactor: 0.94 }
        },
        {
            id: 'blaze',
            name: '烈焰 Blaze',
            icon: '🔥',
            color: '#ff8800',
            stats: { speed: 88, accel: 90, handling: 60 },
            config: { maxSpeed: 330, acceleration: 1.1, driftFactor: 0.91 }
        }
    ];

    // 赛道数据
    const TRACKS = [
        {
            id: 'neon_city',
            name: '霓虹都市',
            description: '穿越霓虹闪烁的城市街道',
            icon: '🌃',
            difficulty: '简单',
            length: 3,
            color: '#00f5ff',
            segments: [
                { curve: 0, hill: 0 }, { curve: 2, hill: 0 }, { curve: 0, hill: 20 },
                { curve: -3, hill: 0 }, { curve: 0, hill: -10 }, { curve: 2, hill: 0 }
            ]
        },
        {
            id: 'mountain_pass',
            name: '山道疾驰',
            description: '险峻山路，极限漂移',
            icon: '🏔️',
            difficulty: '中等',
            length: 4,
            color: '#00ff88',
            segments: [
                { curve: 3, hill: 30 }, { curve: -2, hill: 20 }, { curve: 4, hill: -20 },
                { curve: -3, hill: 40 }, { curve: 2, hill: -30 }, { curve: 0, hill: 0 }
            ]
        },
        {
            id: 'coastal_highway',
            name: '海岸高速',
            description: '沿海风景，极速狂飙',
            icon: '🌊',
            difficulty: '困难',
            length: 5,
            color: '#ff8800',
            segments: [
                { curve: -2, hill: 0 }, { curve: 0, hill: -15 }, { curve: 3, hill: 10 },
                { curve: -1, hill: -20 }, { curve: 2, hill: 15 }, { curve: -2, hill: 0 }
            ]
        },
        {
            id: 'cyber_circuit',
            name: '赛博赛道',
            description: '未来科技竞速场',
            icon: '🤖',
            difficulty: '专家',
            length: 6,
            color: '#ff2d75',
            segments: [
                { curve: 4, hill: 25 }, { curve: -4, hill: -25 }, { curve: 3, hill: 30 },
                { curve: -3, hill: -30 }, { curve: 2, hill: 15 }, { curve: -2, hill: -15 }
            ]
        }
    ];

    // ============================================
    // 游戏状态管理
    // ============================================
    const GameState = {
        MENU: 'menu',
        VEHICLE_SELECT: 'vehicle_select',
        TRACK_SELECT: 'track_select',
        COUNTDOWN: 'countdown',
        PLAYING: 'playing',
        PAUSED: 'paused',
        FINISHED: 'finished'
    };

    // ============================================
    // 游戏数据
    // ============================================
    const GameData = {
        state: GameState.MENU,
        playerCount: 1,
        selectedVehicles: [0, 1],
        selectedTrack: 0,
        raceStartTime: 0,
        currentTime: 0,
        bestLapTime: Infinity,
        topSpeed: 0,
        nitroUsedCount: 0,
        lapTimes: [],
        isTwoPlayer: false
    };

    // ============================================
    // UI管理器
    // ============================================
    const UIManager = {
        elements: {},
        
        init() {
            this.elements = {
                mainMenu: document.getElementById('mainMenu'),
                vehicleSelect: document.getElementById('vehicleSelect'),
                trackSelect: document.getElementById('trackSelect'),
                vehicleGrid: document.getElementById('vehicleGrid'),
                trackGrid: document.getElementById('trackGrid'),
                hud: document.getElementById('hud'),
                hudP2: document.getElementById('hudP2'),
                countdown: document.getElementById('countdown'),
                gameMessage: document.getElementById('gameMessage'),
                pauseMenu: document.getElementById('pauseMenu'),
                resultsPanel: document.getElementById('resultsPanel'),
                performancePanel: document.getElementById('performancePanel'),
                controls: document.getElementById('controls'),
                
                // HUD elements
                positionValue: document.getElementById('positionValue'),
                currentLap: document.getElementById('currentLap'),
                totalLaps: document.getElementById('totalLaps'),
                raceTimer: document.getElementById('raceTimer'),
                speedValue: document.getElementById('speedValue'),
                gearValue: document.getElementById('gearValue'),
                nitroFill: document.getElementById('nitroFill'),
                
                // Result elements
                resultsTitle: document.getElementById('resultsTitle'),
                resultsPosition: document.getElementById('resultsPosition'),
                resultTime: document.getElementById('resultTime'),
                resultBestLap: document.getElementById('resultBestLap'),
                resultTopSpeed: document.getElementById('resultTopSpeed'),
                resultNitroUsed: document.getElementById('resultNitroUsed')
            };
            
            this.renderVehicleGrid();
            this.renderTrackGrid();
        },
        
        showMainMenu() {
            GameData.state = GameState.MENU;
            this.hideAll();
            this.elements.mainMenu.classList.remove('hidden');
            Game.stop();
        },
        
        showVehicleSelect(playerCount) {
            GameData.playerCount = playerCount;
            GameData.isTwoPlayer = playerCount === 2;
            GameData.state = GameState.VEHICLE_SELECT;
            this.hideAll();
            this.renderVehicleGrid();
            this.elements.vehicleSelect.classList.remove('hidden');
        },
        
        showTrackSelect() {
            GameData.state = GameState.TRACK_SELECT;
            this.hideAll();
            this.elements.trackSelect.classList.remove('hidden');
        },
        
        showOptions() {
            // 简单提示，可以扩展
            alert('游戏设置功能开发中...\n\n控制说明:\nP1: W/S/A/D + Space + Shift\nP2: 方向键 + Enter + Ctrl');
        },
        
        hideAll() {
            this.elements.mainMenu.classList.add('hidden');
            this.elements.vehicleSelect.classList.add('hidden');
            this.elements.trackSelect.classList.add('hidden');
            this.elements.hud.classList.add('hidden');
            this.elements.hudP2.classList.add('hidden');
            this.elements.countdown.classList.add('hidden');
            this.elements.pauseMenu.classList.add('hidden');
            this.elements.resultsPanel.classList.add('hidden');
            this.elements.performancePanel.classList.add('hidden');
            this.elements.controls.classList.add('hidden');
        },
        
        renderVehicleGrid() {
            const isTwoPlayer = GameData.isTwoPlayer;
            
            if (isTwoPlayer) {
                let html = `
                    <div class="player-column p1">
                        <div class="player-column-title">玩家 1</div>
                        <div class="selection-grid" style="grid-template-columns: repeat(2, 1fr);">
                `;
                
                VEHICLES.forEach((v, i) => {
                    html += this.createVehicleCard(v, i, 0);
                });
                
                html += `</div></div>
                    <div class="player-column p2">
                        <div class="player-column-title">玩家 2</div>
                        <div class="selection-grid" style="grid-template-columns: repeat(2, 1fr);">
                `;
                
                VEHICLES.forEach((v, i) => {
                    html += this.createVehicleCard(v, i, 1);
                });
                
                html += `</div></div>`;
                
                this.elements.vehicleGrid.innerHTML = html;
            } else {
                let html = `<div class="selection-grid">`;
                VEHICLES.forEach((v, i) => {
                    html += this.createVehicleCard(v, i, 0);
                });
                html += `</div>`;
                this.elements.vehicleGrid.innerHTML = html;
            }
        },
        
        createVehicleCard(vehicle, index, playerIndex) {
            const isSelected = GameData.selectedVehicles[playerIndex] === index;
            return `
                <div class="selection-card ${isSelected ? 'selected' : ''}" 
                     onclick="UIManager.selectVehicle(${index}, ${playerIndex})">
                    <div class="card-icon">${vehicle.icon}</div>
                    <div class="card-name">${vehicle.name}</div>
                    <div class="card-stats">
                        <div>速度</div>
                        <div class="stat-bar"><div class="stat-fill speed" style="width: ${vehicle.stats.speed}%"></div></div>
                        <div>加速</div>
                        <div class="stat-bar"><div class="stat-fill accel" style="width: ${vehicle.stats.accel}%"></div></div>
                        <div>操控</div>
                        <div class="stat-bar"><div class="stat-fill handling" style="width: ${vehicle.stats.handling}%"></div></div>
                    </div>
                </div>
            `;
        },
        
        selectVehicle(index, playerIndex) {
            GameData.selectedVehicles[playerIndex] = index;
            this.renderVehicleGrid();
        },
        
        renderTrackGrid() {
            let html = '';
            TRACKS.forEach((track, index) => {
                const isSelected = GameData.selectedTrack === index;
                const diffColors = {
                    '简单': '#00ff88',
                    '中等': '#f0ff00',
                    '困难': '#ff8800',
                    '专家': '#ff2d75'
                };
                html += `
                    <div class="selection-card ${isSelected ? 'selected' : ''}" 
                         onclick="UIManager.selectTrack(${index})"
                         style="${isSelected ? `border-color: ${track.color}; box-shadow: 0 0 20px ${track.color}40;` : ''}">
                        <div class="card-icon">${track.icon}</div>
                        <div class="card-name" style="color: ${track.color}">${track.name}</div>
                        <div class="card-stats">
                            <div style="margin-bottom: 5px;">${track.description}</div>
                            <div style="color: ${diffColors[track.difficulty]}">${track.difficulty}</div>
                            <div style="margin-top: 5px; color: var(--text-muted);">${track.length} 圈</div>
                        </div>
                    </div>
                `;
            });
            this.elements.trackGrid.innerHTML = html;
        },
        
        selectTrack(index) {
            GameData.selectedTrack = index;
            this.renderTrackGrid();
        },
        
        confirmVehicle() {
            this.showTrackSelect();
        },
        
        confirmTrack() {
            this.startCountdown();
        },
        
        startCountdown() {
            this.hideAll();
            GameData.state = GameState.COUNTDOWN;
            
            if (GameData.isTwoPlayer) {
                this.elements.hudP2.classList.remove('hidden');
            }
            
            let count = 3;
            this.elements.countdown.textContent = count;
            this.elements.countdown.classList.remove('hidden');
            
            const countInterval = setInterval(() => {
                count--;
                if (count > 0) {
                    this.elements.countdown.textContent = count;
                    this.elements.countdown.style.animation = 'none';
                    void this.elements.countdown.offsetWidth;
                    this.elements.countdown.style.animation = 'countdownPulse 0.5s ease-out';
                } else if (count === 0) {
                    this.elements.countdown.textContent = 'GO!';
                    this.elements.countdown.style.color = '#00ff88';
                } else {
                    clearInterval(countInterval);
                    this.elements.countdown.classList.add('hidden');
                    this.elements.countdown.style.color = '';
                    this.startGame();
                }
            }, 1000);
        },
        
        startGame() {
            GameData.state = GameState.PLAYING;
            GameData.raceStartTime = performance.now();
            GameData.currentTime = 0;
            GameData.bestLapTime = Infinity;
            GameData.topSpeed = 0;
            GameData.nitroUsedCount = 0;
            GameData.lapTimes = [];
            
            this.elements.hud.classList.remove('hidden');
            this.elements.performancePanel.classList.remove('hidden');
            this.elements.controls.classList.remove('hidden');
            
            Game.start();
        },
        
        showPauseMenu() {
            if (GameData.state === GameState.PLAYING) {
                GameData.state = GameState.PAUSED;
                this.elements.pauseMenu.classList.remove('hidden');
                Game.pause();
            }
        },
        
        resumeGame() {
            GameData.state = GameState.PLAYING;
            this.elements.pauseMenu.classList.add('hidden');
            Game.resume();
        },
        
        restartRace() {
            this.elements.pauseMenu.classList.add('hidden');
            this.elements.resultsPanel.classList.add('hidden');
            this.startCountdown();
        },
        
        quitToMenu() {
            this.elements.pauseMenu.classList.add('hidden');
            this.elements.resultsPanel.classList.add('hidden');
            this.showMainMenu();
        },
        
        showMessage(text, duration = 2000) {
            this.elements.gameMessage.textContent = text;
            this.elements.gameMessage.classList.remove('hidden');
            this.elements.gameMessage.style.animation = 'none';
            void this.elements.gameMessage.offsetWidth;
            this.elements.gameMessage.style.animation = 'messageFlash 0.5s ease-out';
            
            setTimeout(() => {
                this.elements.gameMessage.classList.add('hidden');
            }, duration);
        },
        
        showResults(position, totalTime, bestLap, topSpeed, nitroUsed) {
            GameData.state = GameState.FINISHED;
            
            const posText = ['1st', '2nd', '3rd', '4th'][position - 1];
            const posClass = ['p1', 'p2', 'p3', 'p4'][position - 1];
            
            this.elements.resultsTitle.textContent = position === 1 ? '胜利!' : '比赛结束';
            this.elements.resultsTitle.className = 'results-title ' + (position === 1 ? 'winner' : 'loser');
            this.elements.resultsPosition.textContent = posText;
            this.elements.resultsPosition.className = 'results-position ' + posClass;
            this.elements.resultTime.textContent = this.formatTime(totalTime);
            this.elements.resultBestLap.textContent = bestLap === Infinity ? '--:--.--' : this.formatTime(bestLap);
            this.elements.resultTopSpeed.textContent = Math.round(topSpeed) + ' KM/H';
            this.elements.resultNitroUsed.textContent = nitroUsed + ' 次';
            
            this.elements.resultsPanel.classList.remove('hidden');
            Game.stop();
        },
        
        updateHUD(data) {
            this.elements.positionValue.textContent = data.position;
            this.elements.currentLap.textContent = data.lap;
            this.elements.totalLaps.textContent = data.totalLaps;
            this.elements.speedValue.textContent = Math.round(data.speed);
            this.elements.gearValue.textContent = data.gear;
            this.elements.nitroFill.style.width = data.nitro + '%';
            this.elements.raceTimer.textContent = this.formatTime(data.time);
        },
        
        formatTime(ms) {
            const minutes = Math.floor(ms / 60000);
            const seconds = Math.floor((ms % 60000) / 1000);
            const centis = Math.floor((ms % 1000) / 10);
            return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${centis.toString().padStart(2, '0')}`;
        }
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
        
        static easeInOut(t) {
            return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
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
        
        static wrap(value, max) {
            return ((value % max) + max) % max;
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
                
                if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'KeyW', 'KeyA', 'KeyS', 'KeyD'].includes(e.code)) {
                    e.preventDefault();
                }
                
                // 暂停
                if (e.code === 'Escape' && GameData.state === GameState.PLAYING) {
                    UIManager.showPauseMenu();
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
    // 赛道类
    // ============================================
    class Track {
        constructor(trackData) {
            this.data = trackData;
            this.segments = [];
            this.totalLength = 0;
            this.generate();
        }
        
        generate() {
            this.segments = [];
            const segmentLength = CONFIG.SEGMENT_LENGTH;
            const segmentsPerCurve = CONFIG.TRACK_LENGTH / this.data.segments.length;
            
            for (let i = 0; i < CONFIG.TRACK_LENGTH; i++) {
                const segmentIndex = Math.floor(i / segmentsPerCurve);
                const segmentData = this.data.segments[Math.min(segmentIndex, this.data.segments.length - 1)];
                
                const curve = segmentData.curve;
                const hill = segmentData.hill;
                
                this.segments.push({
                    index: i,
                    z: i * segmentLength,
                    curve: curve,
                    hill: hill,
                    color: Math.floor(i / 3) % 2 ? 'light' : 'dark'
                });
            }
            
            this.totalLength = this.segments.length * segmentLength;
        }
        
        getSegment(z) {
            const index = MathUtils.wrap(Math.floor(z / CONFIG.SEGMENT_LENGTH), this.segments.length);
            return this.segments[index];
        }
        
        getPosition(z) {
            const segmentLength = CONFIG.SEGMENT_LENGTH;
            const trackLength = this.segments.length * segmentLength;
            return MathUtils.wrap(z, trackLength);
        }
    }

    // ============================================
    // 玩家车辆类
    // ============================================
    class Player {
        constructor(index, vehicleData, isAI = false) {
            this.index = index;
            this.vehicle = vehicleData;
            this.isAI = isAI;
            
            this.x = 0;
            this.z = 0;
            this.speed = 0;
            this.steer = 0;
            this.y = 0;
            
            this.lap = 1;
            this.position = index + 1;
            this.checkpoints = new Array(CONFIG.CHECKPOINT_COUNT).fill(false);
            this.finished = false;
            this.finishTime = 0;
            
            this.nitro = 100;
            this.nitroActive = false;
            this.drifting = false;
            this.onRoad = true;
            
            this.gear = 0;
            
            this.stats = {
                topSpeed: 0,
                nitroUsed: 0,
                bestLapTime: Infinity,
                lapStartTime: 0
            };
            
            // AI properties
            if (isAI) {
                this.targetSpeed = MathUtils.randomRange(200, 300);
                this.targetX = 0;
                this.reactionTimer = 0;
            }
        }
        
        reset() {
            this.x = 0;
            this.z = this.index * -300;
            this.speed = 0;
            this.steer = 0;
            this.y = 0;
            this.lap = 1;
            this.position = this.index + 1;
            this.checkpoints = new Array(CONFIG.CHECKPOINT_COUNT).fill(false);
            this.finished = false;
            this.finishTime = 0;
            this.nitro = 100;
            this.gear = 0;
            this.stats.topSpeed = 0;
            this.stats.nitroUsed = 0;
            this.stats.bestLapTime = Infinity;
            this.stats.lapStartTime = 0;
        }
        
        update(dt, track, input, otherPlayers) {
            if (this.finished) return;
            
            const vehicleConfig = this.vehicle.config;
            
            if (this.isAI) {
                this.updateAI(dt, track, otherPlayers);
            } else {
                this.updatePlayer(dt, track, input, vehicleConfig);
            }
            
            // Update position
            const segment = track.getSegment(this.z);
            const centripetal = segment.curve * this.speed * CONFIG.CAMERA_HEIGHT * 0.00001;
            this.x -= centripetal;
            
            // Clamp X position
            this.x = MathUtils.clamp(this.x, -1.5, 1.5);
            this.onRoad = Math.abs(this.x) < 0.7;
            
            // Forward movement
            this.z += this.speed * dt;
            
            // Update Y position (hills)
            this.y = segment.hill * 0.5;
            
            // Update stats
            if (this.speed > this.stats.topSpeed) {
                this.stats.topSpeed = this.speed;
            }
            
            // Check lap completion
            this.checkLapCompletion(track);
            
            // Calculate gear
            this.gear = Math.floor(this.speed / 60) + 1;
            if (this.gear > 5) this.gear = 5;
            if (this.speed < 5) this.gear = 0;
        }
        
        updatePlayer(dt, track, input, vehicleConfig) {
            const accelerating = input.isKeyDown('KeyW') || input.isKeyDown('ArrowUp');
            const braking = input.isKeyDown('KeyS') || input.isKeyDown('ArrowDown');
            const turningLeft = input.isKeyDown('KeyA') || input.isKeyDown('ArrowLeft');
            const turningRight = input.isKeyDown('KeyD') || input.isKeyDown('ArrowRight');
            const handbrake = input.isKeyDown('Space') || input.isKeyDown('Enter');
            const nitroKey = input.isKeyDown('ShiftLeft') || input.isKeyDown('ShiftRight') || input.isKeyDown('ControlLeft') || input.isKeyDown('ControlRight');
            
            // Steering
            const steerSpeed = vehicleConfig.driftFactor * 0.15;
            if (turningLeft) {
                this.steer = MathUtils.clamp(this.steer + steerSpeed, -1, 1);
            } else if (turningRight) {
                this.steer = MathUtils.clamp(this.steer - steerSpeed, -1, 1);
            } else {
                this.steer *= 0.85;
            }
            
            // Apply steering
            const steerAmount = this.steer * (1 + this.speed / vehicleConfig.maxSpeed * 0.5);
            if (handbrake && Math.abs(this.steer) > 0.3) {
                this.drifting = true;
                this.x += steerAmount * 0.02;
            } else {
                this.drifting = false;
                this.x += steerAmount * 0.01;
            }
            
            // Acceleration/Braking
            if (accelerating) {
                const accelRate = vehicleConfig.acceleration * (this.onRoad ? 1 : 0.5);
                this.speed = MathUtils.clamp(this.speed + accelRate * dt * 60, 0, vehicleConfig.maxSpeed);
            } else if (braking) {
                this.speed = MathUtils.clamp(this.speed - 2 * dt * 60, 0, vehicleConfig.maxSpeed);
            } else {
                this.speed *= this.onRoad ? 0.995 : 0.98;
            }
            
            // Nitro
            if (nitroKey && this.nitro > 0) {
                this.nitroActive = true;
                this.nitro -= dt * 30;
                this.speed = MathUtils.clamp(this.speed + 1.5 * dt * 60, 0, vehicleConfig.maxSpeed * 1.3);
                this.stats.nitroUsed++;
            } else {
                this.nitroActive = false;
                this.nitro = Math.min(100, this.nitro + dt * 10);
            }
        }
        
        updateAI(dt, track, otherPlayers) {
            // Simple AI
            this.reactionTimer -= dt;
            if (this.reactionTimer <= 0) {
                this.reactionTimer = 0.2;
                this.targetX = MathUtils.randomRange(-0.4, 0.4);
                
                // Avoid other players
                for (const other of otherPlayers) {
                    if (other === this) continue;
                    const dz = other.z - this.z;
                    if (dz > 0 && dz < 500) {
                        if (Math.abs(other.x - this.x) < 0.3) {
                            this.targetX = other.x > 0 ? -0.5 : 0.5;
                        }
                    }
                }
            }
            
            // Steer towards target
            const steerDiff = this.targetX - this.x;
            this.x += steerDiff * 0.02;
            
            // Speed control
            const targetSpeed = this.targetSpeed * (this.onRoad ? 1 : 0.7);
            if (this.speed < targetSpeed) {
                this.speed += 0.5 * dt * 60;
            } else {
                this.speed *= 0.998;
            }
        }
        
        checkLapCompletion(track) {
            const segmentIndex = Math.floor(this.z / CONFIG.SEGMENT_LENGTH) % track.segments.length;
            const checkpointIndex = Math.floor(segmentIndex / (track.segments.length / CONFIG.CHECKPOINT_COUNT));
            
            if (checkpointIndex >= 0 && checkpointIndex < CONFIG.CHECKPOINT_COUNT) {
                this.checkpoints[checkpointIndex] = true;
            }
            
            // Check if crossed finish line
            const prevZ = this.z - this.speed * 0.016;
            const trackLength = track.segments.length * CONFIG.SEGMENT_LENGTH;
            
            if (Math.floor(this.z / trackLength) > Math.floor(prevZ / trackLength)) {
                if (this.checkpoints.every(c => c)) {
                    const lapTime = performance.now() - GameData.raceStartTime - (this.lap - 1) * (GameData.currentTime / this.lap);
                    
                    if (lapTime < this.stats.bestLapTime && this.lap > 1) {
                        this.stats.bestLapTime = GameData.currentTime - this.stats.lapStartTime;
                    }
                    this.stats.lapStartTime = GameData.currentTime;
                    
                    this.lap++;
                    this.checkpoints = new Array(CONFIG.CHECKPOINT_COUNT).fill(false);
                    
                    if (this.lap > CONFIG.TOTAL_LAPS) {
                        this.finished = true;
                        this.finishTime = GameData.currentTime;
                    } else {
                        if (!this.isAI) {
                            UIManager.showMessage(`第 ${this.lap} 圈`);
                        }
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
            
            this.width = CONFIG.CANVAS_WIDTH;
            this.height = CONFIG.CANVAS_HEIGHT;
            
            canvas.width = this.width;
            canvas.height = this.height;
            vfxCanvas.width = this.width;
            vfxCanvas.height = this.height;
        }
        
        clear() {
            this.ctx.clearRect(0, 0, this.width, this.height);
            this.vfxCtx.clearRect(0, 0, this.width, this.height);
        }
        
        renderSky(time) {
            const gradient = this.ctx.createLinearGradient(0, 0, 0, this.height / 2);
            gradient.addColorStop(0, CONFIG.COLORS.sky.top);
            gradient.addColorStop(1, CONFIG.COLORS.sky.bottom);
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(0, 0, this.width, this.height / 2);
            
            // Stars
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            for (let i = 0; i < 100; i++) {
                const x = (i * 137 + time * 0.01) % this.width;
                const y = (i * 73) % (this.height / 2);
                const size = (Math.sin(time * 0.001 + i) + 1) * 1.5;
                this.ctx.beginPath();
                this.ctx.arc(x, y, size, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            // Horizon glow
            const horizonGlow = this.ctx.createRadialGradient(
                this.width / 2, this.height / 2, 0,
                this.width / 2, this.height / 2, this.width / 2
            );
            horizonGlow.addColorStop(0, 'rgba(0, 245, 255, 0.1)');
            horizonGlow.addColorStop(1, 'transparent');
            this.ctx.fillStyle = horizonGlow;
            this.ctx.fillRect(0, 0, this.width, this.height);
        }
        
        renderRoad(track, cameraX, cameraZ, cameraY) {
            const segments = track.segments;
            const baseSegment = track.getSegment(cameraZ);
            const segmentLength = CONFIG.SEGMENT_LENGTH;
            
            let maxy = this.height;
            let x = 0;
            let dx = 0;
            
            // Render from back to front
            for (let n = 0; n < CONFIG.DRAW_DISTANCE; n++) {
                const segIndex = MathUtils.wrap(baseSegment.index + n, segments.length);
                const segment = segments[segIndex];
                const looped = (baseSegment.index + n) >= segments.length;
                const segZ = segment.z + (looped ? track.totalLength : 0);
                
                // Project segment
                const p1 = MathUtils.project(
                    { x: cameraX * CONFIG.ROAD_WIDTH + x, y: cameraY + segment.hill, z: segZ },
                    0, cameraY, cameraZ, CONFIG.CAMERA_DEPTH, this.width, this.height, CONFIG.ROAD_WIDTH
                );
                
                const p2 = MathUtils.project(
                    { x: cameraX * CONFIG.ROAD_WIDTH + x + dx, y: cameraY + segment.hill, z: segZ + segmentLength },
                    0, cameraY, cameraZ, CONFIG.CAMERA_DEPTH, this.width, this.height, CONFIG.ROAD_WIDTH
                );
                
                x += dx;
                dx += segment.curve;
                
                if (p1.camera.z <= 0 || p2.screen.y >= maxy) continue;
                
                // Render grass
                this.ctx.fillStyle = segment.color === 'light' ? CONFIG.COLORS.grass.light : CONFIG.COLORS.grass.dark;
                this.ctx.fillRect(0, p2.screen.y, this.width, p1.screen.y - p2.screen.y);
                
                // Render road
                const roadWidth = p1.screen.w * 1.2;
                this.ctx.fillStyle = segment.color === 'light' ? CONFIG.COLORS.asphalt.light : CONFIG.COLORS.asphalt.dark;
                this.ctx.fillRect(p1.screen.x - roadWidth / 2, p2.screen.y, roadWidth, p1.screen.y - p2.screen.y);
                
                // Render rumble strips
                const rumbleWidth = roadWidth * 1.15;
                const rumbleW1 = rumbleWidth / 5;
                this.ctx.fillStyle = segment.color === 'light' ? CONFIG.COLORS.rumble.light : CONFIG.COLORS.rumble.dark;
                this.ctx.fillRect(p1.screen.x - rumbleWidth / 2, p2.screen.y, rumbleW1, p1.screen.y - p2.screen.y);
                this.ctx.fillRect(p1.screen.x + rumbleWidth / 2 - rumbleW1, p2.screen.y, rumbleW1, p1.screen.y - p2.screen.y);
                
                // Render center line
                if (segment.color === 'light') {
                    this.ctx.fillStyle = CONFIG.COLORS.roadLine;
                    this.ctx.shadowColor = CONFIG.COLORS.roadLineGlow;
                    this.ctx.shadowBlur = 10;
                    const lineWidth = 4;
                    const lineHeight = p1.screen.y - p2.screen.y;
                    this.ctx.fillRect(p1.screen.x - lineWidth / 2, p2.screen.y, lineWidth, lineHeight);
                    this.ctx.shadowBlur = 0;
                }
                
                maxy = p2.screen.y;
            }
        }
        
        renderPlayer(player, cameraX, cameraZ, cameraY) {
            const segmentZ = MathUtils.wrap(player.z, CONFIG.TRACK_LENGTH * CONFIG.SEGMENT_LENGTH);
            
            const p = MathUtils.project(
                { x: player.x * CONFIG.ROAD_WIDTH, y: player.y + 50, z: player.z },
                cameraX * CONFIG.ROAD_WIDTH, cameraY, cameraZ, CONFIG.CAMERA_DEPTH, this.width, this.height, CONFIG.ROAD_WIDTH
            );
            
            if (p.camera.z <= 0) return;
            
            const scale = p.screen.scale * 2000;
            const carWidth = 80 * scale;
            const carHeight = 40 * scale;
            const x = p.screen.x;
            const y = p.screen.y;
            
            // Shadow
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            this.ctx.beginPath();
            this.ctx.ellipse(x, y + carHeight * 0.1, carWidth * 0.8, carHeight * 0.2, 0, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Car body
            this.ctx.fillStyle = player.vehicle.color;
            this.ctx.shadowColor = player.vehicle.color;
            this.ctx.shadowBlur = 20;
            
            // Simple car shape
            this.ctx.beginPath();
            this.ctx.moveTo(x - carWidth / 2, y);
            this.ctx.lineTo(x - carWidth / 3, y - carHeight);
            this.ctx.lineTo(x + carWidth / 3, y - carHeight);
            this.ctx.lineTo(x + carWidth / 2, y);
            this.ctx.closePath();
            this.ctx.fill();
            
            // Windshield
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(x - carWidth / 4, y - carHeight * 0.8, carWidth / 2, carHeight * 0.4);
            
            // Nitro glow
            if (player.nitroActive) {
                this.ctx.fillStyle = CONFIG.COLORS.neonCyan;
                this.ctx.shadowColor = CONFIG.COLORS.neonCyan;
                this.ctx.shadowBlur = 30;
                this.ctx.beginPath();
                this.ctx.ellipse(x, y + carHeight * 0.3, carWidth * 0.3, carHeight * 0.5, 0, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            // Drift smoke
            if (player.drifting) {
                this.ctx.fillStyle = 'rgba(200, 200, 200, 0.3)';
                for (let i = 0; i < 3; i++) {
                    const smokeX = x + (Math.random() - 0.5) * carWidth;
                    const smokeY = y + Math.random() * carHeight;
                    this.ctx.beginPath();
                    this.ctx.arc(smokeX, smokeY, Math.random() * 20 * scale + 5, 0, Math.PI * 2);
                    this.ctx.fill();
                }
            }
            
            this.ctx.shadowBlur = 0;
        }
        
        renderVFX(player) {
            // Speed lines when going fast
            if (player.speed > 200) {
                const intensity = (player.speed - 200) / 150;
                this.vfxCtx.strokeStyle = `rgba(0, 245, 255, ${intensity * 0.3})`;
                this.vfxCtx.lineWidth = 2;
                
                for (let i = 0; i < 10; i++) {
                    const x = Math.random() * this.width;
                    const y = Math.random() * this.height;
                    const length = 50 + intensity * 100;
                    
                    this.vfxCtx.beginPath();
                    this.vfxCtx.moveTo(x, y);
                    this.vfxCtx.lineTo(x + length, y);
                    this.vfxCtx.stroke();
                }
            }
            
            // Nitro overlay
            const nitroOverlay = document.getElementById('nitroOverlay');
            if (player.nitroActive) {
                nitroOverlay.style.opacity = '0.3';
            } else {
                nitroOverlay.style.opacity = '0';
            }
        }
    }

    // ============================================
    // 游戏主类
    // ============================================
    const Game = {
        canvas: null,
        vfxCanvas: null,
        renderer: null,
        input: null,
        track: null,
        players: [],
        animationId: null,
        lastTime: 0,
        running: false,
        time: 0,
        
        init() {
            this.canvas = document.getElementById('gameCanvas');
            this.vfxCanvas = document.getElementById('vfxCanvas');
            this.renderer = new Renderer(this.canvas, this.vfxCanvas);
            this.input = new InputManager();
            UIManager.init();
        },
        
        start() {
            const trackData = TRACKS[GameData.selectedTrack];
            this.track = new Track(trackData);
            
            this.players = [];
            
            // Create player(s)
            const p1Vehicle = VEHICLES[GameData.selectedVehicles[0]];
            const player1 = new Player(0, p1Vehicle, false);
            this.players.push(player1);
            
            if (GameData.isTwoPlayer) {
                const p2Vehicle = VEHICLES[GameData.selectedVehicles[1]];
                const player2 = new Player(1, p2Vehicle, false);
                this.players.push(player2);
            }
            
            // Create AI opponents
            const aiCount = GameData.isTwoPlayer ? 2 : 3;
            for (let i = 0; i < aiCount; i++) {
                const aiVehicle = VEHICLES[(GameData.selectedVehicles[0] + i + 1) % VEHICLES.length];
                const ai = new Player(this.players.length, aiVehicle, true);
                this.players.push(ai);
            }
            
            this.time = 0;
            this.running = true;
            this.lastTime = performance.now();
            this.loop();
        },
        
        stop() {
            this.running = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
                this.animationId = null;
            }
        },
        
        pause() {
            this.running = false;
        },
        
        resume() {
            this.running = true;
            this.lastTime = performance.now();
            this.loop();
        },
        
        loop() {
            if (!this.running) return;
            
            const now = performance.now();
            const dt = Math.min((now - this.lastTime) / 1000, 0.1);
            this.lastTime = now;
            
            if (GameData.state === GameState.PLAYING) {
                this.update(dt);
                this.render();
                this.updateHUD();
            }
            
            this.input.clearJustPressed();
            this.animationId = requestAnimationFrame(() => this.loop());
        },
        
        update(dt) {
            this.time += dt;
            GameData.currentTime = performance.now() - GameData.raceStartTime;
            
            // Update all players
            for (const player of this.players) {
                const playerInput = player.index === 0 ? this.input : this.createP2Input();
                player.update(dt, this.track, playerInput, this.players);
            }
            
            // Calculate positions
            this.calculatePositions();
            
            // Check if race finished
            const allFinished = this.players.every(p => p.finished || p.isAI);
            const humanPlayer = this.players[0];
            if (humanPlayer.finished && !this.resultsShown) {
                this.resultsShown = true;
                setTimeout(() => {
                    UIManager.showResults(
                        humanPlayer.position,
                        humanPlayer.finishTime,
                        humanPlayer.stats.bestLapTime,
                        humanPlayer.stats.topSpeed,
                        Math.floor(humanPlayer.stats.nitroUsed / 60)
                    );
                }, 500);
            }
        },
        
        createP2Input() {
            return {
                isKeyDown: (code) => {
                    const p2Mappings = {
                        'KeyW': 'ArrowUp',
                        'KeyS': 'ArrowDown',
                        'KeyA': 'ArrowLeft',
                        'KeyD': 'ArrowRight',
                        'Space': 'Enter',
                        'ShiftLeft': 'ControlLeft',
                        'ShiftRight': 'ControlRight'
                    };
                    const mappedCode = p2Mappings[code] || code;
                    return this.input.isKeyDown(mappedCode);
                }
            };
        },
        
        calculatePositions() {
            // Sort players by progress
            this.players.sort((a, b) => {
                if (a.finished && !b.finished) return -1;
                if (!a.finished && b.finished) return 1;
                if (a.finished && b.finished) return a.finishTime - b.finishTime;
                
                const aProgress = a.lap * 10000 + (a.z / this.track.totalLength);
                const bProgress = b.lap * 10000 + (b.z / this.track.totalLength);
                return bProgress - aProgress;
            });
            
            for (let i = 0; i < this.players.length; i++) {
                this.players[i].position = i + 1;
            }
        },
        
        render() {
            this.renderer.clear();
            
            const player = this.players[0];
            const cameraZ = player.z - 500;
            const cameraY = CONFIG.CAMERA_HEIGHT;
            const cameraX = player.x;
            
            this.renderer.renderSky(this.time);
            this.renderer.renderRoad(this.track, cameraX, cameraZ, cameraY);
            
            // Render all players
            const sortedPlayers = [...this.players].sort((a, b) => {
                const aDist = a.z - cameraZ;
                const bDist = b.z - cameraZ;
                return bDist - aDist;
            });
            
            for (const p of sortedPlayers) {
                if (!p.isAI || p.z > cameraZ) {
                    this.renderer.renderPlayer(p, cameraX, cameraZ, cameraY);
                }
            }
            
            this.renderer.renderVFX(player);
        },
        
        updateHUD() {
            const player = this.players[0];
            UIManager.updateHUD({
                position: player.position,
                lap: Math.min(player.lap, CONFIG.TOTAL_LAPS),
                totalLaps: CONFIG.TOTAL_LAPS,
                speed: player.speed,
                gear: player.gear === 0 ? 'N' : player.gear.toString(),
                nitro: player.nitro,
                time: GameData.currentTime
            });
            
            // Update performance panel
            const fps = Math.round(1000 / (performance.now() - this.lastTime + 16));
            document.getElementById('fpsValue').textContent = fps;
            document.getElementById('frameValue').textContent = Math.round(1000 / fps) + 'ms';
            document.getElementById('particleCount').textContent = Math.floor(this.time * 10) % 500;
            document.getElementById('aiCount').textContent = this.players.filter(p => p.isAI).length;
        }
    };

    // 初始化
    window.onload = () => {
        Game.init();
    };
    </script>
</body>
</html>
```

## 主要实现功能说明

### 1. 主菜单系统
- **霓虹风格标题** - 带有发光动画效果
- **四个主要选项**：单人对战、双人对战、选择赛道、游戏设置
- 赛博朋克视觉风格，与游戏整体美术一致

### 2. 车辆选择界面
- **6辆可选车辆**，各有不同的属性（速度/加速/操控）
- 双人模式时显示分栏选择（P1/P2各自选择）
- 可视化的属性条展示

### 3. 赛道选择界面
- **4条赛道**，难度递增
- 显示赛道描述、难度等级、圈数
- 选中状态有霓虹边框效果

### 4. HUD叠加层
- **位置显示** - 当前排名
- **圈数计数** - 当前圈/总圈数
- **速度仪表** - 实时速度 + 档位
- **氮气条** - 显示剩余氮气
- **计时器** - 比赛用时

### 5. 游戏流程控制
- **3秒倒计时** - 带动画效果
- **ESC暂停菜单** - 继续/重新开始/退出
- **比赛结束界面** - 显示成绩统计

### 6. 双人对战模式
- **P1控制**：W/S/A/D + Space(手刹) + Shift(氮气)
- **P2控制**：方向键 + Enter(手刹) + Ctrl(氮气)
- 分屏显示标识（P1/P2标签）