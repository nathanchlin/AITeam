# UI界面系统与交互设计

**Time**: 2026-03-01T00:48:28.868357

---

我来为你完成游戏的全流程UI系统。这将包含主菜单、游戏HUD、系统菜单、对话框样式、选项按钮动效、提示气泡以及界面缩放适配。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>心跳回忆 - 校园物语</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-dark: #1a1a2e;
            --bg-medium: #16213e;
            --accent-sakura: #ffb7c5;
            --accent-gold: #ffd700;
            --text-light: #f0e6d3;
            --ui-glass: rgba(255, 255, 255, 0.1);
            --stat-knowledge: #6b8cce;
            --stat-charm: #ff6b8a;
            --stat-stamina: #4ecdc4;
            --stat-social: #ffd700;
            --stat-art: #9b59b6;
            --stat-fitness: #e67e22;
            --glass-bg: linear-gradient(135deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95));
            --glass-border: rgba(255, 183, 197, 0.3);
        }

        body {
            background: var(--bg-dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Hiragino Sans', 'Microsoft YaHei', sans-serif;
            overflow: hidden;
        }

        /* 游戏容器与缩放适配 */
        .game-wrapper {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .game-container {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 
                0 0 60px rgba(255, 183, 197, 0.3),
                0 20px 60px rgba(0, 0, 0, 0.5);
            transform-origin: center center;
            transition: transform 0.3s ease;
        }

        #gameCanvas {
            display: block;
            cursor: pointer;
        }

        /* ============================================
           主菜单界面
        ============================================ */
        .main-menu {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
            background: linear-gradient(180deg, 
                rgba(26, 26, 46, 0.95) 0%,
                rgba(22, 33, 62, 0.9) 50%,
                rgba(26, 26, 46, 0.95) 100%);
        }

        .main-menu.hidden {
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s ease;
        }

        .menu-bg-decor {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
        }

        .menu-title {
            position: relative;
            z-index: 10;
            text-align: center;
            margin-bottom: 60px;
        }

        .menu-title h1 {
            font-size: 56px;
            font-weight: 300;
            color: var(--accent-sakura);
            text-shadow: 
                0 0 40px rgba(255, 183, 197, 0.5),
                0 4px 20px rgba(0, 0, 0, 0.3);
            letter-spacing: 8px;
            animation: titleGlow 3s ease-in-out infinite;
        }

        .menu-title .subtitle {
            font-size: 18px;
            color: var(--text-light);
            opacity: 0.7;
            letter-spacing: 12px;
            margin-top: 10px;
        }

        @keyframes titleGlow {
            0%, 100% { text-shadow: 0 0 40px rgba(255, 183, 197, 0.5), 0 4px 20px rgba(0, 0, 0, 0.3); }
            50% { text-shadow: 0 0 60px rgba(255, 183, 197, 0.8), 0 4px 20px rgba(0, 0, 0, 0.3); }
        }

        .menu-buttons {
            display: flex;
            flex-direction: column;
            gap: 16px;
            position: relative;
            z-index: 10;
        }

        .menu-btn {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 30px;
            padding: 16px 60px;
            color: var(--text-light);
            font-size: 18px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            min-width: 280px;
            text-align: center;
            position: relative;
            overflow: hidden;
            letter-spacing: 4px;
        }

        .menu-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 183, 197, 0.2), 
                transparent);
            transition: left 0.5s ease;
        }

        .menu-btn:hover::before {
            left: 100%;
        }

        .menu-btn:hover {
            background: linear-gradient(135deg, rgba(255, 183, 197, 0.2), rgba(22, 33, 62, 0.95));
            border-color: var(--accent-sakura);
            transform: translateX(10px);
            box-shadow: 0 0 30px rgba(255, 183, 197, 0.3);
        }

        .menu-btn:active {
            transform: translateX(10px) scale(0.98);
        }

        .menu-btn.primary {
            background: linear-gradient(135deg, rgba(255, 183, 197, 0.3), rgba(255, 107, 138, 0.2));
            border-color: var(--accent-sakura);
        }

        .menu-footer {
            position: absolute;
            bottom: 30px;
            color: var(--text-light);
            opacity: 0.4;
            font-size: 12px;
            letter-spacing: 2px;
        }

        /* ============================================
           游戏HUD - 属性快捷显示
        ============================================ */
        .game-hud {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            pointer-events: none;
            z-index: 50;
        }

        .hud-left {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .hud-right {
            display: flex;
            gap: 10px;
            pointer-events: auto;
        }

        /* 时间面板 */
        .time-panel {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 12px 18px;
            backdrop-filter: blur(10px);
            pointer-events: auto;
            min-width: 160px;
        }

        .date-display {
            font-size: 13px;
            color: var(--accent-sakura);
            margin-bottom: 2px;
            letter-spacing: 1px;
        }

        .time-display {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent-gold);
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
            letter-spacing: 2px;
        }

        .period-display {
            font-size: 11px;
            color: var(--text-light);
            opacity: 0.7;
            letter-spacing: 2px;
        }

        /* 属性快捷条 */
        .stats-quick-bar {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 10px 15px;
            backdrop-filter: blur(10px);
            display: flex;
            gap: 15px;
            pointer-events: auto;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .stats-quick-bar:hover {
            border-color: var(--accent-sakura);
        }

        .stat-quick-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .stat-quick-icon {
            font-size: 16px;
        }

        .stat-quick-value {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-light);
        }

        .stat-quick-bar .stat-quick-item:nth-child(1) .stat-quick-value { color: var(--stat-knowledge); }
        .stat-quick-bar .stat-quick-item:nth-child(2) .stat-quick-value { color: var(--stat-charm); }
        .stat-quick-bar .stat-quick-item:nth-child(3) .stat-quick-value { color: var(--stat-stamina); }
        .stat-quick-bar .stat-quick-item:nth-child(4) .stat-quick-value { color: #f1c40f; }

        /* HUD按钮 */
        .hud-btn {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 10px 14px;
            color: var(--text-light);
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .hud-btn:hover {
            background: linear-gradient(135deg, rgba(255, 183, 197, 0.2), rgba(22, 33, 62, 0.95));
            border-color: var(--accent-sakura);
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255, 183, 197, 0.2);
        }

        .hud-btn:active {
            transform: translateY(0) scale(0.98);
        }

        .hud-btn .icon {
            font-size: 16px;
        }

        /* ============================================
           系统菜单
        ============================================ */
        .system-menu {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(26, 26, 46, 0.9);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 150;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .system-menu.active {
            opacity: 1;
            pointer-events: auto;
        }

        .system-panel {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 30px;
            min-width: 400px;
            max-width: 500px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        }

        .system-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--glass-border);
        }

        .system-panel-title {
            font-size: 22px;
            color: var(--accent-sakura);
            letter-spacing: 4px;
        }

        .close-btn {
            background: none;
            border: none;
            color: var(--text-light);
            font-size: 24px;
            cursor: pointer;
            opacity: 0.6;
            transition: all 0.3s ease;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .close-btn:hover {
            opacity: 1;
            background: rgba(255, 107, 138, 0.2);
            transform: rotate(90deg);
        }

        .system-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .system-tab {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid transparent;
            border-radius: 10px;
            padding: 12px;
            color: var(--text-light);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        .system-tab:hover {
            background: rgba(255, 183, 197, 0.1);
        }

        .system-tab.active {
            background: rgba(255, 183, 197, 0.2);
            border-color: var(--accent-sakura);
        }

        .system-content {
            min-height: 200px;
        }

        .save-slots {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }

        .save-slot {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .save-slot:hover {
            border-color: var(--accent-sakura);
            background: rgba(255, 183, 197, 0.1);
            transform: translateY(-2px);
        }

        .save-slot-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .save-slot-name {
            font-size: 14px;
            color: var(--accent-sakura);
            font-weight: 600;
        }

        .save-slot-date {
            font-size: 11px;
            color: var(--text-light);
            opacity: 0.5;
        }

        .save-slot-info {
            font-size: 12px;
            color: var(--text-light);
            opacity: 0.7;
        }

        .save-slot.empty {
            opacity: 0.5;
        }

        .save-slot.empty .save-slot-info {
            opacity: 0.4;
        }

        /* 设置面板 */
        .settings-group {
            margin-bottom: 20px;
        }

        .settings-label {
            font-size: 13px;
            color: var(--text-light);
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }

        .settings-slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.1);
            appearance: none;
            outline: none;
            cursor: pointer;
        }

        .settings-slider::-webkit-slider-thumb {
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-sakura);
            cursor: pointer;
            box-shadow: 0 0 10px rgba(255, 183, 197, 0.5);
            transition: transform 0.2s ease;
        }

        .settings-slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }

        .settings-toggle {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .toggle-switch {
            width: 48px;
            height: 26px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 13px;
            position: relative;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        .toggle-switch.active {
            background: rgba(255, 183, 197, 0.5);
        }

        .toggle-switch::after {
            content: '';
            position: absolute;
            top: 3px;
            left: 3px;
            width: 20px;
            height: 20px;
            background: var(--text-light);
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .toggle-switch.active::after {
            left: 25px;
            background: var(--accent-sakura);
        }

        /* ============================================
           对话框样式
        ============================================ */
        .dialogue-container {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            pointer-events: none;
            z-index: 60;
        }

        .dialogue-box {
            background: linear-gradient(180deg, 
                rgba(26, 26, 46, 0.95) 0%,
                rgba(22, 33, 62, 0.98) 100%);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 20px 25px;
            backdrop-filter: blur(15px);
            box-shadow: 
                0 -10px 40px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            pointer-events: auto;
            position: relative;
            overflow: hidden;
        }

        .dialogue-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--accent-sakura), 
                transparent);
            opacity: 0.5;
        }

        .dialogue-speaker {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .speaker-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-sakura), #ff69b4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 15px rgba(255, 183, 197, 0.4);
        }

        .speaker-name {
            font-size: 16px;
            font-weight: 600;
            color: var(--accent-sakura);
            text-shadow: 0 0 10px rgba(255, 183, 197, 0.3);
        }

        .dialogue-text {
            font-size: 16px;
            line-height: 1.8;
            color: var(--text-light);
            min-height: 60px;
            position: relative;
        }

        .dialogue-text .typing-cursor {
            display: inline-block;
            width: 2px;
            height: 1em;
            background: var(--accent-sakura);
            margin-left: 2px;
            animation: cursorBlink 0.8s infinite;
            vertical-align: text-bottom;
        }

        @keyframes cursorBlink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }

        .dialogue-continue {
            position: absolute;
            bottom: 10px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 5px;
            color: var(--accent-sakura);
            font-size: 12px;
            opacity: 0.6;
            animation: continuePulse 1.5s ease-in-out infinite;
        }

        @keyframes continuePulse {
            0%, 100% { opacity: 0.4; transform: translateY(0); }
            50% { opacity: 0.8; transform: translateY(3px); }
        }

        /* ============================================
           选项按钮
        ============================================ */
        .choices-container {
            position: absolute;
            bottom: 180px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            flex-direction: column;
            gap: 12px;
            pointer-events: auto;
            z-index: 70;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .choices-container.active {
            opacity: 1;
        }

        .choice-btn {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 14px 30px;
            color: var(--text-light);
            font-size: 15px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            min-width: 300px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .choice-btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            width: 3px;
            height: 0;
            background: var(--accent-sakura);
            transform: translateY(-50%);
            transition: height 0.3s ease;
        }

        .choice-btn::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 183, 197, 0.15), 
                transparent);
            transition: left 0.5s ease;
        }

        .choice-btn:hover {
            background: linear-gradient(135deg, rgba(255, 183, 197, 0.15), rgba(22, 33, 62, 0.95));
            border-color: var(--accent-sakura);
            transform: translateX(15px);
            box-shadow: 
                0 0 25px rgba(255, 183, 197, 0.25),
                inset 0 0 20px rgba(255, 183, 197, 0.05);
        }

        .choice-btn:hover::before {
            height: 70%;
        }

        .choice-btn:hover::after {
            left: 100%;
        }

        .choice-btn:active {
            transform: translateX(15px) scale(0.98);
        }

        .choice-btn .choice-icon {
            margin-right: 8px;
        }

        /* ============================================
           提示气泡
        ============================================ */
        .tooltip {
            position: absolute;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 10px 15px;
            backdrop-filter: blur(10px);
            z-index: 200;
            max-width: 250px;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .tooltip.active {
            opacity: 1;
        }

        .tooltip-title {
            font-size: 13px;
            color: var(--accent-sakura);
            font-weight: 600;
            margin-bottom: 5px;
        }

        .tooltip-content {
            font-size: 12px;
            color: var(--text-light);
            line-height: 1.5;
        }

        .tooltip-arrow {
            position: absolute;
            width: 10px;
            height: 10px;
            background: var(--bg-medium);
            border-left: 1px solid var(--glass-border);
            border-bottom: 1px solid var(--glass-border);
            transform: rotate(-45deg);
        }

        .tooltip[data-position="top"] .tooltip-arrow {
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%) rotate(-45deg);
        }

        /* 通知气泡 */
        .notification {
            position: fixed;
            top: 80px;
            right: 20px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 15px 20px;
            backdrop-filter: blur(10px);
            z-index: 300;
            display: flex;
            align-items: center;
            gap: 12px;
            transform: translateX(120%);
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification-icon {
            font-size: 24px;
        }

        .notification-content {
            display: flex;
            flex-direction: column;
        }

        .notification-title {
            font-size: 14px;
            color: var(--accent-sakura);
            font-weight: 600;
        }

        .notification-text {
            font-size: 12px;
            color: var(--text-light);
            opacity: 0.8;
        }

        /* ============================================
           属性面板（详细）
        ============================================ */
        .stats-panel {
            position: absolute;
            top: 70px;
            left: 20px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(15px);
            z-index: 80;
            min-width: 280px;
            opacity: 0;
            pointer-events: none;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        }

        .stats-panel.active {
            opacity: 1;
            pointer-events: auto;
            transform: translateY(0);
        }

        .stats-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .stats-panel-title {
            font-size: 16px;
            color: var(--accent-sakura);
            letter-spacing: 2px;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }

        .stat-icon {
            font-size: 18px;
            width: 24px;
            text-align: center;
        }

        .stat-info {
            flex: 1;
        }

        .stat-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .stat-name {
            font-size: 12px;
            color: var(--text-light);
            opacity: 0.8;
        }

        .stat-value {
            font-size: 12px;
            font-weight: 600;
        }

        .stat-bar-bg {
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
        }

        .stat-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s ease;
        }

        /* ============================================
           Bloom泛光叠加层
        ============================================ */
        .bloom-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            mix-blend-mode: screen;
            opacity: 0;
            transition: opacity 0.5s ease;
        }

        .bloom-overlay.active {
            opacity: 0.6;
            animation: bloomPulse 2s ease-in-out infinite;
        }

        @keyframes bloomPulse {
            0%, 100% { opacity: 0.4; filter: blur(20px); }
            50% { opacity: 0.7; filter: blur(30px); }
        }

        /* ============================================
           场景转场层
        ============================================ */
        .transition-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }

        .transition-overlay .soft-light {
            position: absolute;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at center, 
                rgba(255, 183, 197, 0.9) 0%, 
                rgba(255, 215, 224, 0.7) 30%,
                rgba(255, 255, 255, 0) 70%);
            opacity: 0;
            transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .transition-overlay.transitioning .soft-light {
            opacity: 1;
            animation: transitionPulse 1.6s ease-in-out;
        }

        @keyframes transitionPulse {
            0% { opacity: 0; transform: scale(0.5); }
            50% { opacity: 1; transform: scale(1.2); }
            100% { opacity: 0; transform: scale(1.5); }
        }

        /* ============================================
           心跳脉冲效果
        ============================================ */
        .heartbeat-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 50;
        }

        .heartbeat-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100px;
            height: 100px;
            border: 3px solid rgba(255, 107, 138, 0.8);
            border-radius: 50%;
            opacity: 0;
        }

        .heartbeat-container.pulsing .heartbeat-ring {
            animation: heartbeatRing 1.2s ease-out forwards;
        }

        .heartbeat-container.pulsing .heartbeat-ring:nth-child(2) {
            animation-delay: 0.2s;
        }

        .heartbeat-container.pulsing .heartbeat-ring:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes heartbeatRing {
            0% {
                width: 60px;
                height: 60px;
                opacity: 1;
                border-color: rgba(255, 107, 138, 1);
            }
            100% {
                width: 200px;
                height: 200px;
                opacity: 0;
                border-color: rgba(255, 183, 197, 0);
            }
        }

        /* ============================================
           心形爆炸粒子
        ============================================ */
        .heart-particle {
            position: absolute;
            font-size: 20px;
            pointer-events: none;
            animation: heartFloat 2s ease-out forwards;
        }

        @keyframes heartFloat {
            0% {
                opacity: 1;
                transform: translate(0, 0) scale(1) rotate(0deg);
            }
            100% {
                opacity: 0;
                transform: translate(var(--tx), var(--ty)) scale(0.3) rotate(var(--rot));
            }
        }

        /* ============================================
           行动选择面板
        ============================================ */
        .action-panel {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(15px);
            z-index: 90;
            min-width: 600px;
            max-width: 800px;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
        }

        .action-panel.active {
            opacity: 1;
            pointer-events: auto;
        }

        .action-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .action-panel-title {
            font-size: 18px;
            color: var(--accent-sakura);
            letter-spacing: 3px;
        }

        .action-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }

        .action-tab {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid transparent;
            border-radius: 20px;
            padding: 8px 20px;
            color: var(--text-light);
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .action-tab:hover {
            background: rgba(255, 183, 197, 0.1);
        }

        .action-tab.active {
            background: rgba(255, 183, 197, 0.2);
            border-color: var(--accent-sakura);
        }

        .action-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }

        .action-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .action-card:hover {
            border-color: var(--accent-sakura);
            background: rgba(255, 183, 197, 0.1);
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(255, 183, 197, 0.15);
        }

        .action-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 183, 197, 0.1), transparent);
            transition: left 0.5s ease;
        }

        .action-card:hover::before {
            left: 100%;
        }

        .action-card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .action-card-icon {
            font-size: 24px;
        }

        .action-card-name {
            font-size: 14px;
            color: var(--text-light);
            font-weight: 500;
        }

        .action-card-desc {
            font-size: 11px;
            color: var(--text-light);
            opacity: 0.6;
            margin-bottom: 10px;
        }

        .action-card-effects {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }

        .effect-tag {
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
        }

        .effect-tag.positive {
            color: #4ecdc4;
        }

        .effect-tag.negative {
            color: #ff6b6b;
        }

        /* ============================================
           好感度面板
        ============================================ */
        .affection-panel {
            position: absolute;
            top: 70px;
            right: 20px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(15px);
            z-index: 80;
            min-width: 220px;
            opacity: 0;
            pointer-events: none;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        }

        .affection-panel.active {
            opacity: 1;
            pointer-events: auto;
            transform: translateY(0);
        }

        .affection-panel-title {
            font-size: 14px;
            color: var(--accent-sakura);
            letter-spacing: 2px;
            margin-bottom: 15px;
        }

        .affection-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .affection-item:last-child {
            border-bottom: none;
        }

        .affection-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }

        .affection-info {
            flex: 1;
        }

        .affection-name {
            font-size: 13px;
            color: var(--text-light);
            margin-bottom: 4px;
        }

        .affection-bar {
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            overflow: hidden;
        }

        .affection-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-sakura), #ff69b4);
            border-radius: 2px;
            transition: width 0.5s ease;
        }

        .affection-hearts {
            display: flex;
            gap: 2px;
        }

        .heart-icon {
            font-size: 12px;
            opacity: 0.3;
        }

        .heart-icon.filled {
            opacity: 1;
        }

        /* ============================================
           响应式缩放
        ============================================ */
        @media (max-width: 1300px) {
            .game-container {
                transform: scale(0.9);
            }
        }

        @media (max-width: 1100px) {
            .game-container {
                transform: scale(0.8);
            }
        }

        @media (max-width: 900px) {
            .game-container {
                transform: scale(0.7);
            }
        }

        @media (max-width: 700px) {
            .game-container {
                transform: scale(0.5);
            }
        }

        /* 缩放指示器 */
        .scale-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 8px 15px;
            color: var(--text-light);
            font-size: 12px;
            opacity: 0.5;
            z-index: 400;
        }
    </style>
</head>
<body>
    <div class="game-wrapper">
        <div class="game-container" id="gameContainer">
            <canvas id="gameCanvas" width="1200" height="700"></canvas>
            
            <!-- 主菜单 -->
            <div class="main-menu" id="mainMenu">
                <div class="menu-bg-decor">
                    <canvas id="menuCanvas" width="1200" height="700"></canvas>
                </div>
                <div class="menu-title">
                    <h1>心跳回忆</h1>
                    <div class="subtitle">校园物语</div>
                </div>
                <div class="menu-buttons">
                    <button class="menu-btn primary" onclick="startNewGame()">开始新游戏</button>
                    <button class="menu-btn" onclick="continueGame()">继续游戏</button>
                    <button class="menu-btn" onclick="showLoadMenu()">读取存档</button>
                    <button class="menu-btn" onclick="showSettings()">游戏设置</button>
                </div>
                <div class="menu-footer">© 2024 Tokimeki Memorial Fan Project</div>
            </div>

            <!-- 游戏HUD -->
            <div class="game-hud" id="gameHud" style="display: none;">
                <div class="hud-left">
                    <!-- 时间面板 -->
                    <div class="time-panel" id="timePanel">
                        <div class="date-display" id="dateDisplay">4月1日 星期一</div>
                        <div class="time-display" id="timeDisplay">08:00</div>
                        <div class="period-display" id="periodDisplay">早晨</div>
                    </div>
                    
                    <!-- 属性快捷条 -->
                    <div class="stats-quick-bar" onclick="toggleStatsPanel()">
                        <div class="stat-quick-item">
                            <span class="stat-quick-icon">📚</span>
                            <span class="stat-quick-value" id="quickKnowledge">45</span>
                        </div>
                        <div class="stat-quick-item">
                            <span class="stat-quick-icon">✨</span>
                            <span class="stat-quick-value" id="quickCharm">32</span>
                        </div>
                        <div class="stat-quick-item">
                            <span class="stat-quick-icon">💪</span>
                            <span class="stat-quick-value" id="quickStamina">80</span>
                        </div>
                        <div class="stat-quick-item">
                            <span class="stat-quick-icon">💰</span>
                            <span class="stat-quick-value" id="quickMoney">5000</span>
                        </div>
                    </div>
                </div>
                
                <div class="hud-right">
                    <button class="hud-btn" onclick="showActionPanel()">
                        <span class="icon">📋</span>
                        <span>行动</span>
                    </button>
                    <button class="hud-btn" onclick="showAffectionPanel()">
                        <span class="icon">💕</span>
                        <span>好感</span>
                    </button>
                    <button class="hud-btn" onclick="showSystemMenu()">
                        <span class="icon">⚙️</span>
                        <span>菜单</span>
                    </button>
                </div>
            </div>

            <!-- 详细属性面板 -->
            <div class="stats-panel" id="statsPanel">
                <div class="stats-panel-header">
                    <span class="stats-panel-title">角色属性</span>
                    <button class="close-btn" onclick="toggleStatsPanel()">×</button>
                </div>
                <div id="statsPanelContent"></div>
            </div>

            <!-- 好感度面板 -->
            <div class="affection-panel" id="affectionPanel">
                <div class="affection-panel-title">好感度</div>
                <div id="affectionPanelContent"></div>
            </div>

            <!-- 对话框 -->
            <div class="dialogue-container" id="dialogueContainer" style="display: none;">
                <div class="dialogue-box">
                    <div class="dialogue-speaker">
                        <div class="speaker-avatar" id="speakerAvatar">🌸</div>
                        <span class="speaker-name" id="speakerName">小樱</span>
                    </div>
                    <div class="dialogue-text" id="dialogueText">
                        <span id="dialogueContent"></span>
                        <span class="typing-cursor"></span>
                    </div>
                    <div class="dialogue-continue">
                        <span>点击继续</span>
                        <span>▼</span>
                    </div>
                </div>
            </div>

            <!-- 选项容器 -->
            <div class="choices-container" id="choicesContainer"></div>

            <!-- 行动选择面板 -->
            <div class="action-panel" id="actionPanel">
                <div class="action-panel-header">
                    <span class="action-panel-title">选择行动</span>
                    <button class="close-btn" onclick="hideActionPanel()">×</button>
                </div>
                <div class="action-tabs" id="actionTabs">
                    <button class="action-tab active" data-category="study">学习</button>
                    <button class="action-tab" data-category="life">生活</button>
                    <button class="action-tab" data-category="social">社交</button>
                </div>
                <div class="action-grid" id="actionGrid"></div>
            </div>

            <!-- 系统菜单 -->
            <div class="system-menu" id="systemMenu">
                <div class="system-panel">
                    <div class="system-panel-header">
                        <span class="system-panel-title" id="systemPanelTitle">系统菜单</span>
                        <button class="close-btn" onclick="hideSystemMenu()">×</button>
                    </div>
                    <div class="system-tabs" id="systemTabs">
                        <button class="system-tab active" data-tab="save">保存</button>
                        <button class="system-tab" data-tab="load">读取</button>
                        <button class="system-tab" data-tab="settings">设置</button>
                    </div>
                    <div class="system-content" id="systemContent"></div>
                </div>
            </div>

            <!-- Bloom泛光层 -->
            <div class="bloom-overlay" id="bloomOverlay"></div>
            
            <!-- 场景转场层 -->
            <div class="transition-overlay" id="transitionOverlay">
                <div class="soft-light"></div>
            </div>
            
            <!-- 心跳脉冲容器 -->
            <div class="heartbeat-container" id="heartbeatContainer">
                <div class="heartbeat-ring"></div>
                <div class="heartbeat-ring"></div>
                <div class="heartbeat-ring"></div>
            </div>
        </div>
    </div>

    <!-- 通知气泡 -->
    <div class="notification" id="notification">
        <span class="notification-icon" id="notificationIcon">✨</span>
        <div class="notification-content">
            <span class="notification-title" id="notificationTitle">提示</span>
            <span class="notification-text" id="notificationText">内容</span>
        </div>
    </div>

    <!-- 提示气泡 -->
    <div class="tooltip" id="tooltip">
        <div class="tooltip-title"></div>
        <div class="tooltip-content"></div>
        <div class="tooltip-arrow"></div>
    </div>

    <!-- 缩放指示器 -->
    <div class="scale-indicator" id="scaleIndicator">100%</div>

    <script>
        // ============================================
        // 游戏配置
        // ============================================
        const CONFIG = {
            CANVAS_WIDTH: 1200,
            CANVAS_HEIGHT: 700,
            TIME_SPEED: 0.0001,
            DAY_LENGTH: 24 * 60 * 60 * 1000,
            PARTICLE_COUNT: 60,
            STAR_COUNT: 100,
            TYPE_SPEED: 30,
            TYPE_SPEED_FAST: 10
        };

        // ============================================
        // 表情状态枚举
        // ============================================
        const ExpressionState = {
            NORMAL: 'normal',
            HAPPY: 'happy',
            SHY: 'shy',
            SAD: 'sad',
            ANGRY: 'angry',
            SURPRISED: 'surprised',
            LOVE: 'love'
        };

        // ============================================
        // 角色数据配置
        // ============================================
        const CharacterData = {
            sakura: {
                name: '小樱',
                avatar: '🌸',
                hairColor: '#ffb7c5',
                hairHighlight: '#ffd4de',
                eyeColor: '#d4738a',
                skinColor: '#fef0e8',
                outfitColor: '#f5f5f5',
                outfitAccent: '#ffb7c5',
                accessoryColor: '#ff69b4',
                personality: '开朗活泼',
                likes: ['甜点', '可爱事物', '聊天'],
                dialogues: {
                    normal: '你好呀！今天天气真好呢~',
                    happy: '哇！真的吗？太开心了！',
                    shy: '那个...人家有点不好意思...',
                    surprised: '诶？！怎么会这样！',
                    sad: '呜...人家有点难过...',
                    love: '和你在一起，感觉心跳好快...'
                }
            },
            yuki: {
                name: '雪乃',
                avatar: '❄️',
                hairColor: '#e8e8f0',
                hairHighlight: '#ffffff',
                eyeColor: '#6b8cce',
                skinColor: '#fef8f5',
                outfitColor: '#2c3e50',
                outfitAccent: '#3498db',
                accessoryColor: '#5dade2',
                personality: '冷静知性',
                likes: ['读书', '安静', '文学'],
                dialogues: {
                    normal: '有什么事吗？',
                    happy: '哼...还不赖吧。',
                    shy: '别...别突然说这种话...',
                    surprised: '这是什么情况...',
                    sad: '我没事...真的...',
                    love: '如果是你的话...也许可以...'
                }
            },
            haru: {
                name: '春菜',
                avatar: '🌿',
                hairColor: '#8b5a2b',
                hairHighlight: '#c9a66b',
                eyeColor: '#228b22',
                skinColor: '#fce4d6',
                outfitColor: '#ff9800',
                outfitAccent: '#ffeb3b',
                accessoryColor: '#4caf50',
                personality: '元气运动',
                likes: ['运动', '冒险', '美食'],
                dialogues: {
                    normal: '哟！今天也一起加油吧！',
                    happy: '太棒了！这就是青春啊！',
                    shy: '等...等一下啦！',
                    surprised: '真的假的？！太厉害了！',
                    sad: '下次一定能做得更好的！',
                    love: '其实...我一直都很在意你哦'
                }
            }
        };

        // ============================================
        // 主角属性定义
        // ============================================
        const PlayerStats = {
            knowledge: { name: '学识', icon: '📚', color: '#6b8cce', max: 100 },
            charm: { name: '魅力', icon: '✨', color: '#ff6b8a', max: 100 },
            stamina: { name: '体力', icon: '💪', color: '#4ecdc4', max: 100 },
            social: { name: '社交', icon: '💬', color: '#ffd700', max: 100 },
            art: { name: '艺术', icon: '🎨', color: '#9b59b6', max: 100 },
            fitness: { name: '运动', icon: '⚽', color: '#e67e22', max: 100 },
            money: { name: '金钱', icon: '💰', color: '#f1c40f', max: 99999 }
        };

        // ============================================
        // 行动定义
        // ============================================
        const ActionsData = {
            study: [
                { id: 'study_class', name: '认真上课', icon: '📖', effects: { knowledge: 5, stamina: -10 }, timeCost: 2, description: '专心听讲，增长知识' },
                { id: 'study_library', name: '图书馆自习', icon: '📕', effects: { knowledge: 8, social: -2, stamina: -15 }, timeCost: 3, description: '沉浸书海，大幅提升学识' },
                { id: 'study_cram', name: '补习班', icon: '✏️', effects: { knowledge: 10, stamina: -20, money: -500 }, timeCost: 3, description: '付费补习，效果显著' },
                { id: 'study_exam', name: '考前冲刺', icon: '📝', effects: { knowledge: 15, stamina: -30 }, timeCost: 4, description: '临阵磨枪，不快也光' },
                { id: 'study_research', name: '课题研究', icon: '🔬', effects: { knowledge: 6, art: 2, stamina: -12 }, timeCost: 2, description: '培养研究能力' },
                { id: 'study_language', name: '外语学习', icon: '🌍', effects: { knowledge: 4, social: 3, stamina: -10 }, timeCost: 2, description: '掌握新语言' }
            ],
            life: [
                { id: 'life_rest', name: '好好休息', icon: '😴', effects: { stamina: 30, knowledge: -2 }, timeCost: 2, description: '恢复体力' },
                { id: 'life_exercise', name: '锻炼身体', icon: '🏃', effects: { fitness: 5, stamina: -5, charm: 2 }, timeCost: 2, description: '强健体魄' },
                { id: 'life_gaming', name: '玩游戏', icon: '🎮', effects: { stamina: 10, social: 2, knowledge: -3 }, timeCost: 2, description: '放松心情' },
                { id: 'life_shopping', name: '逛街购物', icon: '🛍️', effects: { charm: 3, stamina: -10, money: -1000 }, timeCost: 3, description: '提升品味' },
                { id: 'life_hobby', name: '发展爱好', icon: '🎯', effects: { art: 4, stamina: -8, charm: 2 }, timeCost: 2, description: '培养才艺' },
                { id: 'life_sleep', name: '早睡早起', icon: '🛏️', effects: { stamina: 40, fitness: 1 }, timeCost: 4, description: '充分休息' }
            ],
            social: [
                { id: 'social_club', name: '社团活动', icon: '🎪', effects: { social: 5, art: 3, stamina: -10 }, timeCost: 2, description: '参与社团' },
                { id: 'social_volunteer', name: '志愿者活动', icon: '🤝', effects: { social: 6, charm: 3, stamina: -15 }, timeCost: 3, description: '帮助他人' },
                { id: 'social_party', name: '参加聚会', icon: '🎉', effects: { social: 8, charm: 4, stamina: -20 }, timeCost: 3, description: '扩展人脉' },
                { id: 'social_chat', name: '和朋友聊天', icon: '☕', effects: { social: 4, stamina: -5 }, timeCost: 1, description: '增进友谊' },
                { id: 'social_parttime', name: '打工赚钱', icon: '💼', effects: { money: 1500, stamina: -25, social: 2 }, timeCost: 4, description: '赚取生活费' },
                { id: 'social_date', name: '邀约约会', icon: '💑', effects: { charm: 3, social: 5, stamina: -15 }, timeCost: 3, description: '培养感情', needCharacter: true }
            ]
        };

        // ============================================
        // 游戏状态
        // ============================================
        const GameState = {
            currentScreen: 'menu', // menu, game, dialogue
            player: {
                name: '玩家',
                stats: {
                    knowledge: 45,
                    charm: 32,
                    stamina: 80,
                    social: 50,
                    art: 25,
                    fitness: 40,
                    money: 5000
                }
            },
            time: {
                year: 2024,
                month: 4,
                day: 1,
                hour: 8,
                minute: 0,
                dayOfWeek: 1
            },
            affections: {
                sakura: { level: 2, exp: 150, max: 500 },
                yuki: { level: 1, exp: 50, max: 500 },
                haru: { level: 1, exp: 80, max: 500 }
            },
            flags: {},
            dialogue: {
                current: null,
                currentIndex: 0,
                isTyping: false,
                textQueue: []
            },
            settings: {
                bgmVolume: 80,
                sfxVolume: 100,
                textSpeed: 30,
                autoPlay: false
            },
            saves: []
        };

        // ============================================
        // 粒子系统
        // ============================================
        class ParticleSystem {
            constructor(canvas) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.particles = [];
                this.lightSpots = [];
                this.init();
            }

            init() {
                for (let i = 0; i < CONFIG.PARTICLE_COUNT; i++) {
                    this.particles.push(this.createSakuraParticle());
                }
                for (let i = 0; i < 20; i++) {
                    this.lightSpots.push(this.createLightSpot());
                }
            }

            createSakuraParticle() {
                const colors = ['#ffb7c5', '#ffd4de', '#ffffff', '#ffe4e8'];
                return {
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height - this.canvas.height,
                    size: Math.random() * 8 + 4,
                    speedX: Math.random() * 2 - 1,
                    speedY: Math.random() * 1.5 + 0.5,
                    rotation: Math.random() * Math.PI * 2,
                    rotationSpeed: (Math.random() - 0.5) * 0.05,
                    opacity: Math.random() * 0.6 + 0.4,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    swing: Math.random() * Math.PI * 2,
                    swingSpeed: Math.random() * 0.02 + 0.01
                };
            }

            createLightSpot() {
                return {
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    size: Math.random() * 100 + 50,
                    opacity: Math.random() * 0.15 + 0.05,
                    speedX: (Math.random() - 0.5) * 0.3,
                    speedY: (Math.random() - 0.5) * 0.3,
                    hue: Math.random() * 30 + 330
                };
            }

            update() {
                this.particles.forEach(p => {
                    p.swing += p.swingSpeed;
                    p.x += p.speedX + Math.sin(p.swing) * 0.5;
                    p.y += p.speedY;
                    p.rotation += p.rotationSpeed;

                    if (p.y > this.canvas.height + 20) {
                        p.y = -20;
                        p.x = Math.random() * this.canvas.width;
                    }
                    if (p.x < -20) p.x = this.canvas.width + 20;
                    if (p.x > this.canvas.width + 20) p.x = -20;
                });

                this.lightSpots.forEach(spot => {
                    spot.x += spot.speedX;
                    spot.y += spot.speedY;
                    
                    if (spot.x < -spot.size) spot.x = this.canvas.width + spot.size;
                    if (spot.x > this.canvas.width + spot.size) spot.x = -spot.size;
                    if (spot.y < -spot.size) spot.y = this.canvas.height + spot.size;
                    if (spot.y > this.canvas.height + spot.size) spot.y = -spot.size;
                });
            }

            draw(ctx) {
                // 绘制光斑
                this.lightSpots.forEach(spot => {
                    const gradient = ctx.createRadialGradient(spot.x, spot.y, 0, spot.x, spot.y, spot.size);
                    gradient.addColorStop(0, `hsla(${spot.hue}, 80%, 90%, ${spot.opacity})`);
                    gradient.addColorStop(1, 'transparent');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(spot.x, spot.y, spot.size, 0, Math.PI * 2);
                    ctx.fill();
                });

                // 绘制樱花粒子
                this.particles.forEach(p => {
                    ctx.save();
                    ctx.translate(p.x, p.y);
                    ctx.rotate(p.rotation);
                    ctx.globalAlpha = p.opacity;
                    
                    ctx.beginPath();
                    ctx.fillStyle = p.color;
                    
                    for (let i = 0; i < 5; i++) {
                        const angle = (i / 5) * Math.PI * 2;
                        const x = Math.cos(angle) * p.size * 0.5;
                        const y = Math.sin(angle) * p.size * 0.3;
                        if (i === 0) {
                            ctx.moveTo(x, y);
                        } else {
                            ctx.quadraticCurveTo(
                                Math.cos(angle - 0.3) * p.size * 0.7,
                                Math.sin(angle - 0.3) * p.size * 0.5,
                                x, y
                            );
                        }
                    }
                    ctx.closePath();
                    ctx.fill();
                    
                    ctx.restore();
                });
            }
        }

        // ============================================
        // 场景渲染系统
        // ============================================
        class SceneRenderer {
            constructor(canvas) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.currentScene = 'classroom';
            }

            getSceneColors(scene) {
                const scenes = {
                    classroom: {
                        sky: ['#87ceeb', '#b0e0e6'],
                        ground: '#8b7355',
                        building: '#f5f5dc'
                    },
                    rooftop: {
                        sky: ['#ff9a9e', '#fecfef'],
                        ground: '#808080',
                        building: '#a0a0a0'
                    },
                    park: {
                        sky: ['#a8edea', '#fed6e3'],
                        ground: '#90ee90',
                        building: '#deb887'
                    },
                    library: {
                        sky: ['#4a4a6a', '#3a3a5a'],
                        ground: '#8b4513',
                        building: '#d2691e'
                    }
                };
                return scenes[scene] || scenes.classroom;
            }

            getTimeOfDay() {
                const hour = GameState.time.hour;
                if (hour >= 5 && hour < 8) return 'dawn';
                if (hour >= 8 && hour < 12) return 'morning';
                if (hour >= 12 && hour < 14) return 'noon';
                if (hour >= 14 && hour < 17) return 'afternoon';
                if (hour >= 17 && hour < 20) return 'evening';
                return 'night';
            }

            drawGradientRect(x, y, w, h, colors) {
                const gradient = this.ctx.createLinearGradient(x, y, x, y + h);
                colors.forEach((color, i) => {
                    gradient.addColorStop(i / (colors.length - 1), color);
                });
                this.ctx.fillStyle = gradient;
                this.ctx.fillRect(x, y, w, h);
            }

            render(timeOfDay) {
                const ctx = this.ctx;
                const w = this.canvas.width;
                const h = this.canvas.height;
                const colors = this.getSceneColors(this.currentScene);
                
                // 绘制天空
                this.drawGradientRect(0, 0, w, h * 0.6, colors.sky);
                
                // 绘制地面
                ctx.fillStyle = colors.ground;
                ctx.fillRect(0, h * 0.6, w, h * 0.4);
                
                // 绘制远山
                this.drawMountains(ctx, w, h);
                
                // 绘制樱花树
                this.drawSakuraTree(ctx, 100, h * 0.5, 120);
                this.drawSakuraTree(ctx, w - 150, h * 0.55, 100);
                
                // 绘制建筑
                this.drawBuilding(ctx, w * 0.3, h * 0.3, 200, h * 0.35, colors.building);
                
                // 绘制时间效果
                this.drawTimeEffects(ctx, w, h, timeOfDay);
            }

            drawMountains(ctx, w, h) {
                ctx.fillStyle = 'rgba(100, 120, 150, 0.3)';
                ctx.beginPath();
                ctx.moveTo(0, h * 0.6);
                ctx.lineTo(w * 0.2, h * 0.4);
                ctx.lineTo(w * 0.4, h * 0.55);
                ctx.lineTo(w * 0.6, h * 0.35);
                ctx.lineTo(w * 0.8, h * 0.5);
                ctx.lineTo(w, h * 0.45);
                ctx.lineTo(w, h * 0.6);
                ctx.closePath();
                ctx.fill();
            }

            drawSakuraTree(ctx, x, y, size) {
                // 树干
                ctx.fillStyle = '#5d4037';
                ctx.fillRect(x - size * 0.1, y, size * 0.2, size * 0.8);
                
                // 树冠
                const gradient = ctx.createRadialGradient(x, y - size * 0.3, 0, x, y - size * 0.3, size * 0.8);
                gradient.addColorStop(0, 'rgba(255, 183, 197, 0.9)');
                gradient.addColorStop(0.5, 'rgba(255, 183, 197, 0.6)');
                gradient.addColorStop(1, 'rgba(255, 183, 197, 0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(x, y - size * 0.3, size * 0.8, 0, Math.PI * 2);
                ctx.fill();
            }

            drawBuilding(ctx, x, y, w, h, color) {
                ctx.fillStyle = color;
                ctx.fillRect(x, y, w, h);
                
                // 窗户
                ctx.fillStyle = 'rgba(135, 206, 235, 0.5)';
                for (let row = 0; row < 4; row++) {
                    for (let col = 0; col < 3; col++) {
                        ctx.fillRect(x + 20 + col * 60, y + 20 + row * (h / 5), 40, h / 6);
                    }
                }
            }

            drawTimeEffects(ctx, w, h, timeOfDay) {
                // 简单的时间效果
                if (timeOfDay === 'evening') {
                    ctx.fillStyle = 'rgba(255, 150, 100, 0.2)';
                    ctx.fillRect(0, 0, w, h);
                } else if (timeOfDay === 'night') {
                    ctx.fillStyle = 'rgba(0, 0, 50, 0.4)';
                    ctx.fillRect(0, 0, w, h);
                }
            }
        }

        // ============================================
        // UI管理器
        // ============================================
        class UIManager {
            constructor() {
                this.mainMenu = document.getElementById('mainMenu');
                this.gameHud = document.getElementById('gameHud');
                this.systemMenu = document.getElementById('systemMenu');
                this.dialogueContainer = document.getElementById('dialogueContainer');
                this.choicesContainer = document.getElementById('choicesContainer');
                this.statsPanel = document.getElementById('statsPanel');
                this.affectionPanel = document.getElementById('affectionPanel');
                this.actionPanel = document.getElementById('actionPanel');
                this.notification = document.getElementById('notification');
                this.tooltip = document.getElementById('tooltip');
                
                this.typingInterval = null;
                this.currentCategory = 'study';
                
                this.init();
            }

            init() {
                this.initActionTabs();
                this.initSystemTabs();
                this.updateScaleIndicator();
                window.addEventListener('resize', () => this.updateScaleIndicator());
            }

            initActionTabs() {
                const tabs = document.querySelectorAll('#actionTabs .action-tab');
                tabs.forEach(tab => {
                    tab.addEventListener('click', () => {
                        tabs.forEach(t => t.classList.remove('active'));
                        tab.classList.add('active');
                        this.currentCategory = tab.dataset.category;
                        this.renderActionGrid(this.currentCategory);
                    });
                });
            }

            initSystemTabs() {
                const tabs = document.querySelectorAll('#systemTabs .system-tab');
                tabs.forEach(tab => {
                    tab.addEventListener('click', () => {
                        tabs.forEach(t => t.classList.remove('active'));
                        tab.classList.add('active');
                        this.renderSystemContent(tab.dataset.tab);
                    });
                });
            }

            showMainMenu() {
                this.mainMenu.classList.remove('hidden');
                this.gameHud.style.display = 'none';
                GameState.currentScreen = 'menu';
            }

            hideMainMenu() {
                this.mainMenu.classList.add('hidden');
            }

            showGameHUD() {
                this.gameHud.style.display = 'flex';
                GameState.currentScreen = 'game';
            }

            showSystemMenu() {
                this.systemMenu.classList.add('active');
                this.renderSystemContent('save');
            }

            hideSystemMenu() {
                this.systemMenu.classList.remove('active');
            }

            showDialogue(speaker, text, expression = 'normal') {
                this.dialogueContainer.style.display = 'block';
                
                const charData = CharacterData[speaker];
                if (charData) {
                    document.getElementById('speakerAvatar').textContent = charData.avatar;
                    document.getElementById('speakerName').textContent = charData.name;
                }
                
                this.typeText(text);
            }

            hideDialogue() {
                this.dialogueContainer.style.display = 'none';
            }

            typeText(text) {
                const contentEl = document.getElementById('dialogueContent');
                contentEl.textContent = '';
                
                if (this.typingInterval) {
                    clearInterval(this.typingInterval);
                }
                
                let index = 0;
                GameState.dialogue.isTyping = true;
                
                this.typingInterval = setInterval(() => {
                    if (index < text.length) {
                        contentEl.textContent += text[index];
                        index++;
                    } else {
                        clearInterval(this.typingInterval);
                        GameState.dialogue.isTyping = false;
                    }
                }, GameState.settings.textSpeed);
            }

            skipTyping() {
                if (GameState.dialogue.isTyping) {
                    clearInterval(this.typingInterval);
                    // 完成当前文本
                    GameState.dialogue.isTyping = false;
                }
            }

            showChoices(choices, callback) {
                this.choicesContainer.innerHTML = '';
                this.choicesContainer.classList.add('active');
                
                choices.forEach((choice, index) => {
                    const btn = document.createElement('button');
                    btn.className = 'choice-btn';
                    btn.innerHTML = `<span class="choice-icon">${choice.icon || ''}</span>${choice.text}`;
                    btn.addEventListener('click', () => {
                        this.choicesContainer.classList.remove('active');
                        if (callback) callback(index, choice);
                    });
                    this.choicesContainer.appendChild(btn);
                });
            }

            showActionPanel() {
                this.actionPanel.classList.add('active');
                this.renderActionGrid(this.currentCategory);
            }

            hideActionPanel() {
                this.actionPanel.classList.remove('active');
            }

            renderActionGrid(category) {
                const grid = document.getElementById('actionGrid');
                const actions = ActionsData[category] || [];
                
                grid.innerHTML = actions.map(action => `
                    <div class="action-card" data-action="${action.id}">
                        <div class="action-card-header">
                            <span class="action-card-icon">${action.icon}</span>
                            <span class="action-card-name">${action.name}</span>
                        </div>
                        <div class="action-card-desc">${action.description}</div>
                        <div class="action-card-effects">
                            ${Object.entries(action.effects).map(([stat, value]) => `
                                <span class="effect-tag ${value > 0 ? 'positive' : 'negative'}">
                                    ${PlayerStats[stat]?.icon || '💰'} ${value > 0 ? '+' : ''}${value}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                `).join('');
                
                // 添加点击事件
                grid.querySelectorAll('.action-card').forEach(card => {
                    card.addEventListener('click', () => {
                        const actionId = card.dataset.action;
                        this.executeAction(actionId, category);
                    });
                });
            }

            executeAction(actionId, category) {
                const action = ActionsData[category].find(a => a.id === actionId);
                if (!action) return;
                
                // 检查体力
                if (action.effects.stamina && GameState.player.stats.stamina + action.effects.stamina < 0) {
                    this.showNotification('⚠️', '体力不足', '请先休息恢复体力');
                    return;
                }
                
                // 应用效果
                Object.entries(action.effects).forEach(([stat, value]) => {
                    if (GameState.player.stats[stat] !== undefined) {
                        GameState.player.stats[stat] = Math.max(0, Math.min(
                            PlayerStats[stat]?.max || 99999,
                            GameState.player.stats[stat] + value
                        ));
                    }
                });
                
                // 推进时间
                this.advanceTime(action.timeCost);
                
                // 更新UI
                this.updateQuickStats();
                
                // 显示反馈
                this.showNotification(
                    action.icon,
                    action.name,
                    Object.entries(action.effects)
                        .filter(([_, v]) => v !== 0)
                        .map(([k, v]) => `${PlayerStats[k]?.name || k} ${v > 0 ? '+' : ''}${v}`)
                        .join(', ')
                );
                
                // 隐藏面板
                this.hideActionPanel();
                
                // 播放心跳效果
                this.triggerHeartbeat();
            }

            advanceTime(hours) {
                GameState.time.hour += hours;
                while (GameState.time.hour >= 24) {
                    GameState.time.hour -= 24;
                    GameState.time.day++;
                    GameState.time.dayOfWeek = (GameState.time.dayOfWeek + 1) % 7;
                    
                    // 月份处理
                    const daysInMonth = new Date(GameState.time.year, GameState.time.month, 0).getDate();
                    if (GameState.time.day > daysInMonth) {
                        GameState.time.day = 1;
                        GameState.time.month++;
                        if (GameState.time.month > 12) {
                            GameState.time.month = 1;
                            GameState.time.year++;
                        }
                    }
                }
                this.updateTimeDisplay();
            }

            updateTimeDisplay() {
                const days = ['日', '一', '二', '三', '四', '五', '六'];
                const periods = ['深夜', '凌晨', '早晨', '上午', '中午', '下午', '傍晚', '夜晚'];
                
                document.getElementById('dateDisplay').textContent = 
                    `${GameState.time.month}月${GameState.time.day}日 星期${days[GameState.time.dayOfWeek]}`;
                document.getElementById('timeDisplay').textContent = 
                    `${String(GameState.time.hour).padStart(2, '0')}:00`;
                
                const periodIndex = Math.floor(GameState.time.hour / 3);
                document.getElementById('periodDisplay').textContent = periods[periodIndex];
            }

            updateQuickStats() {
                document.getElementById('quickKnowledge').textContent = GameState.player.stats.knowledge;
                document.getElementById('quickCharm').textContent = GameState.player.stats.charm;
                document.getElementById('quickStamina').textContent = GameState.player.stats.stamina;
                document.getElementById('quickMoney').textContent = GameState.player.stats.money;
            }

            toggleStatsPanel() {
                this.statsPanel.classList.toggle('active');
                if (this.statsPanel.classList.contains('active')) {
                    this.renderStatsPanel();
                }
            }

            renderStatsPanel() {
                const content = document.getElementById('statsPanelContent');
                content.innerHTML = Object.entries(PlayerStats).map(([key, stat]) => {
                    const value = GameState.player.stats[key];
                    const percentage = (value / stat.max) * 100;
                    return `
                        <div class="stat-item">
                            <span class="stat-icon">${stat.icon}</span>
                            <div class="stat-info">
                                <div class="stat-header">
                                    <span class="stat-name">${stat.name}</span>
                                    <span class="stat-value" style="color: ${stat.color}">${value}</span>
                                </div>
                                <div class="stat-bar-bg">
                                    <div class="stat-bar-fill" style="width: ${percentage}%; background: ${stat.color}"></div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
            }

            showAffectionPanel() {
                this.affectionPanel.classList.toggle('active');
                if (this.affectionPanel.classList.contains('active')) {
                    this.renderAffectionPanel();
                }
            }

            renderAffectionPanel() {
                const content = document.getElementById('affectionPanelContent');
                content.innerHTML = Object.entries(CharacterData).map(([key, char]) => {
                    const aff = GameState.affections[key];
                    const percentage = (aff.exp / aff.max) * 100;
                    const hearts = Math.min(5, Math.floor(aff.level));
                    
                    return `
                        <div class="affection-item">
                            <div class="affection-avatar" style="background: linear-gradient(135deg, ${char.hairColor}, ${char.outfitAccent})">
                                ${char.avatar}
                            </div>
                            <div class="affection-info">
                                <div class="affection-name">${char.name}</div>
                                <div class="affection-bar">
                                    <div class="affection-fill" style="width: ${percentage}%"></div>
                                </div>
                            </div>
                            <div class="affection-hearts">
                                ${[1,2,3,4,5].map(i => `<span class="heart-icon ${i <= hearts ? 'filled' : ''}">♥</span>`).join('')}
                            </div>
                        </div>
                    `;
                }).join('');
            }

            showNotification(icon, title, text) {
                document.getElementById('notificationIcon').textContent = icon;
                document.getElementById('notificationTitle').textContent = title;
                document.getElementById('notificationText').textContent = text;
                
                this.notification.classList.add('show');
                
                setTimeout(() => {
                    this.notification.classList.remove('show');
                }, 3000);
            }

            showTooltip(element, title, content, position = 'top') {
                const rect = element.getBoundingClientRect();
                const container = document.getElementById('gameContainer').getBoundingClientRect();
                
                this.tooltip.querySelector('.tooltip-title').textContent = title;
                this.tooltip.querySelector('.tooltip-content').textContent = content;
                this.tooltip.dataset.position = position;
                
                let x = rect.left - container.left + rect.width / 2;
                let y = rect.top - container.top - 10;
                
                this.tooltip.style.left = `${x}px`;
                this.tooltip.style.top = `${y}px`;
                this.tooltip.style.transform = 'translate(-50%, -100%)';
                this.tooltip.classList.add('active');
            }

            hideTooltip() {
                this.tooltip.classList.remove('active');
            }

            renderSystemContent(tab) {
                const content = document.getElementById('systemContent');
                const title = document.getElementById('systemPanelTitle');
                
                switch(tab) {
                    case 'save':
                        title.textContent = '保存游戏';
                        content.innerHTML = this.renderSaveSlots('save');
                        break;
                    case 'load':
                        title.textContent = '读取存档';
                        content.innerHTML = this.renderSaveSlots('load');
                        break;
                    case 'settings':
                        title.textContent = '游戏设置';
                        content.innerHTML = this.renderSettings();
                        break;
                }
            }

            renderSaveSlots(mode) {
                const slots = [];
                for (let i = 1; i <= 6; i++) {
                    const save = GameState.saves[i - 1];
                    if (save) {
                        slots.push(`
                            <div class="save-slot" data-slot="${i}" data-mode="${mode}">
                                <div class="save-slot-header">
                                    <span class="save-slot-name">存档 ${i}</span>
                                    <span class="save-slot-date">${save.date}</span>
                                </div>
                                <div class="save-slot-info">
                                    ${save.month}月${save.day}日 | ${save.location || '学校'}
                                </div>
                            </div>
                        `);
                    } else {
                        slots.push(`
                            <div class="save-slot empty" data-slot="${i}" data-mode="${mode}">
                                <div class="save-slot-header">
                                    <span class="save-slot-name">存档 ${i}</span>
                                </div>
                                <div class="save-slot-info">空</div>
                            </div>
                        `);
                    }
                }
                
                setTimeout(() => {
                    document.querySelectorAll('.save-slot').forEach(slot => {
                        slot.addEventListener('click', () => {
                            const slotIndex = parseInt(slot.dataset.slot) - 1;
                            const mode = slot.dataset.mode;
                            
                            if (mode === 'save') {
                                this.saveGame(slotIndex);
                            } else {
                                this.loadGame(slotIndex);
                            }
                        });
                    });
                }, 0);
                
                return `<div class="save-slots">${slots.join('')}</div>`;
            }

            renderSettings() {
                return `
                    <div class="settings-group">
                        <div class="settings-label">
                            <span>背景音乐</span>
                            <span>${GameState.settings.bgmVolume}%</span>
                        </div>
                        <input type="range" class="settings-slider" id="bgmSlider" 
                            value="${GameState.settings.bgmVolume}" min="0" max="100">
                    </div>
                    <div class="settings-group">
                        <div class="settings-label">
                            <span>音效音量</span>
                            <span>${GameState.settings.sfxVolume}%</span>
                        </div>
                        <input type="range" class="settings-slider" id="sfxSlider" 
                            value="${GameState.settings.sfxVolume}" min="0" max="100">
                    </div>
                    <div class="settings-group">
                        <div class="settings-label">
                            <span>文字速度</span>
                            <span>${101 - GameState.settings.textSpeed}</span>
                        </div>
                        <input type="range" class="settings-slider" id="textSpeedSlider" 
                            value="${101 - GameState.settings.textSpeed}" min="10" max="100">
                    </div>
                    <div class="settings-toggle">
                        <span>自动播放对话</span>
                        <div class="toggle-switch ${GameState.settings.autoPlay ? 'active' : ''}" 
                            id="autoPlayToggle"></div>
                    </div>
                `;
            }

            saveGame(slotIndex) {
                const save = {
                    date: new Date().toLocaleDateString('zh-CN'),
                    month: GameState.time.month,
                    day: GameState.time.day,
                    player: JSON.parse(JSON.stringify(GameState.player)),
                    time: JSON.parse(JSON.stringify(GameState.time)),
                    affections: JSON.parse(JSON.stringify(GameState.affections))
                };
                
                GameState.saves[slotIndex] = save;
                localStorage.setItem('tokimeki_saves', JSON.stringify(GameState.saves));
                
                this.showNotification('💾', '保存成功', `已保存到存档 ${slotIndex + 1}`);
            }

            loadGame(slotIndex) {
                const save = GameState.saves[slotIndex];
                if (!save) {
                    this.showNotification('⚠️', '无法读取', '该存档为空');
                    return;
                }
                
                GameState.player = JSON.parse(JSON.stringify(save.player));
                GameState.time = JSON.parse(JSON.stringify(save.time));
                GameState.affections = JSON.parse(JSON.stringify(save.affections));
                
                this.updateTimeDisplay();
                this.updateQuickStats();
                this.hideSystemMenu();
                
                this.showNotification('📂', '读取成功', '游戏已恢复');
            }

            triggerHeartbeat() {
                const container = document.getElementById('heartbeatContainer');
                container.classList.remove('pulsing');
                void container.offsetWidth; // 强制重排
                container.classList.add('pulsing');
                
                setTimeout(() => {
                    container.classList.remove('pulsing');
                }, 1500);
            }

            triggerBloom() {
                const overlay = document.getElementById('bloomOverlay');
                overlay.classList.add('active');
                setTimeout(() => {
                    overlay.classList.remove('active');
                }, 3000);
            }

            updateScaleIndicator() {
                const container = document.getElementById('gameContainer');
                const scale = container.getBoundingClientRect().width / CONFIG.CANVAS_WIDTH;
                document.getElementById('scaleIndicator').textContent = `${Math.round(scale * 100)}%`;
            }
        }

        // ============================================
        // 游戏主类
        // ============================================
        class Game {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.menuCanvas = document.getElementById('menuCanvas');
                this.menuCtx = this.menuCanvas.getContext('2d');
                
                this.particleSystem = new ParticleSystem(this.canvas);
                this.menuParticles = new ParticleSystem(this.menuCanvas);
                this.sceneRenderer = new SceneRenderer(this.canvas);
                this.ui = new UIManager();
                
                this.lastTime = 0;
                this.isRunning = true;
                
                this.init();
            }

            init() {
                // 加载存档
                const savedData = localStorage.getItem('tokimeki_saves');
                if (savedData) {
                    GameState.saves = JSON.parse(savedData);
                }
                
                // 绑定事件
                this.canvas.addEventListener('click', () => this.handleCanvasClick());
                
                // 初始化设置滑块
                document.addEventListener('click', (e) => {
                    if (e.target.classList.contains('settings-slider')) {
                        this.handleSettingChange(e.target);
                    }
                    if (e.target.classList.contains('toggle-switch')) {
                        e.target.classList.toggle('active');
                        if (e.target.id === 'autoPlayToggle') {
                            GameState.settings.autoPlay = e.target.classList.contains('active');
                        }
                    }
                });
                
                // 开始游戏循环
                this.gameLoop(0);
            }

            handleCanvasClick() {
                if (GameState.dialogue.isTyping) {
                    this.ui.skipTyping();
                }
            }

            handleSettingChange(slider) {
                const value = parseInt(slider.value);
                const label = slider.parentElement.querySelector('.settings-label span:last-child');
                
                switch(slider.id) {
                    case 'bgmSlider':
                        GameState.settings.bgmVolume = value;
                        label.textContent = `${value}%`;
                        break;
                    case 'sfxSlider':
                        GameState.settings.sfxVolume = value;
                        label.textContent = `${value}%`;
                        break;
                    case 'textSpeedSlider':
                        GameState.settings.textSpeed = 101 - value;
                        label.textContent = value;
                        break;
                }
            }

            gameLoop(timestamp) {
                const deltaTime = timestamp - this.lastTime;
                this.lastTime = timestamp;
                
                // 更新粒子
                this.particleSystem.update();
                this.menuParticles.update();
                
                // 渲染
                this.render();
                
                if (this.isRunning) {
                    requestAnimationFrame((t) => this.gameLoop(t));
                }
            }

            render() {
                // 清空画布
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                this.menuCtx.clearRect(0, 0, this.menuCanvas.width, this.menuCanvas.height);
                
                // 渲染主菜单背景
                this.menuCtx.fillStyle = 'transparent';
                this.menuCtx.fillRect(0, 0, this.menuCanvas.width, this.menuCanvas.height);
                this.menuParticles.draw(this.menuCtx);
                
                // 如果在游戏中，渲染场景
                if (GameState.currentScreen === 'game') {
                    const timeOfDay = this.sceneRenderer.getTimeOfDay();
                    this.sceneRenderer.render(timeOfDay);
                    this.particleSystem.draw(this.ctx);
                }
            }
        }

        // ============================================
        // 全局函数
        // ============================================
        let game;

        function startNewGame() {
            // 重置游戏状态
            GameState.player.stats = {
                knowledge: 45,
                charm: 32,
                stamina: 80,
                social: 50,
                art: 25,
                fitness: 40,
                money: 5000
            };
            GameState.time = {
                year: 2024,
                month: 4,
                day: 1,
                hour: 8,
                minute: 0,
                dayOfWeek: 1
            };
            
            game.ui.hideMainMenu();
            game.ui.showGameHUD();
            game.ui.updateTimeDisplay();
            game.ui.updateQuickStats();
            
            // 显示开场对话
            setTimeout(() => {
                game.ui.showDialogue('sakura', '你好呀！欢迎来到樱花学院！我是小樱，从今天开始我们就是同学了呢~');
            }, 500);
        }

        function continueGame() {
            const saves = GameState.saves.filter(s => s);
            if (saves.length === 0) {
                game.ui.showNotification('⚠️', '无存档', '没有找到可继续的存档');
                return;
            }
            
            // 加载最新的存档
            const lastSave = saves[saves.length - 1];
            const slotIndex = GameState.saves.indexOf(lastSave);
            game.ui.loadGame(slotIndex);
            
            game.ui.hideMainMenu();
            game.ui.showGameHUD();
        }

        function showLoadMenu() {
            game.ui.showSystemMenu();
            document.querySelector('[data-tab="load"]').click();
        }

        function showSettings() {
            game.ui.showSystemMenu();
            document.querySelector('[data-tab="settings"]').click();
        }

        function showSystemMenu() {
            game.ui.showSystemMenu();
        }

        function hideSystemMenu() {
            game.ui.hideSystemMenu();
        }

        function showActionPanel() {
            game.ui.showActionPanel();
        }

        function hideActionPanel() {
            game.ui.hideActionPanel();
        }

        function toggleStatsPanel() {
            game.ui.toggleStatsPanel();
        }

        function showAffectionPanel() {
            game.ui.showAffectionPanel();
        }

        // ============================================
        // 初始化游戏
        // ============================================
        window.addEventListener('DOMContentLoaded', () => {
            game = new Game();
        });
    </script>
</body>
</html>
```

## 完成说明

我为你实现了完整的UI界面系统与交互设计，包含以下功能模块：

### 1. 主菜单界面
- 精美的标题动画效果（呼吸光晕）
- 菜单按钮带有闪光扫过效果
- 支持4个主要功能：新游戏、继续游戏、读取存档、游戏设置

### 2. 游戏HUD系统
- **时间面板**：显示日期、时间、时段
- **属性快捷条**：点击可展开详细属性面板
- **功能按钮**：行动、好感度、系统菜单

### 3. 系统菜单
- **保存/读取**：6个存档位，支持自动保存到localStorage
- **设置面板**：音量滑块、文字速度、自动播放开关

### 4. 对话框系统
- 带角色头像和名字的对话框
- 打字机效果 + 闪烁光标
- 点击跳过打字效果

### 5. 选项按钮
- 优雅的hover动效（左侧边条 + 光线扫过）
- 点击后展开选项分支

### 6. 提示气泡与通知
- 右上角滑入式通知
- 属性变化实时反馈

### 7. 界面缩放适配
- 响应式缩放（1300px-700px多档适配）
- 右下角显示当前缩放比例

### 8. 交互特效
- 心跳脉冲动画
- Bloom泛光效果
- 樱花粒子背景