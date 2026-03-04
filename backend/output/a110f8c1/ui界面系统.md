# UI界面系统

**Agent**: coder

**Time**: 2026-02-24T23:01:07.153853

---

我来为你实现一个完整的国风UI界面系统，整合之前的核心玩法，包含主界面、境界面板、装备背包、灵兽图鉴和设置页面，采用水墨风格设计。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>寻道大千 - 挂机修仙</title>
    <link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Sans+SC:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #080810;
            --bg-secondary: #101020;
            --bg-card: rgba(12, 12, 24, 0.95);
            --fg-primary: #e8e4d9;
            --fg-secondary: #7a7a8a;
            --fg-muted: #4a4a5a;
            --accent-gold: #d4a54a;
            --accent-gold-light: #e8c878;
            --accent-cyan: #3ecdc4;
            --accent-red: #d64545;
            --accent-green: #45b76c;
            --accent-purple: #9c64b5;
            --accent-orange: #e67e22;
            --border-gold: rgba(212, 165, 74, 0.4);
            --border-light: rgba(212, 165, 74, 0.2);
            --shadow-gold: rgba(212, 165, 74, 0.2);
            --quality-common: #8a8a9a;
            --quality-good: #4caf50;
            --quality-rare: #2196f3;
            --quality-epic: #9c27b0;
            --quality-legend: #ff9800;
            --quality-mythic: #f44336;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: var(--bg-primary);
            color: var(--fg-primary);
            font-family: 'Noto Sans SC', sans-serif;
            overflow: hidden;
            min-height: 100vh;
            min-height: 100dvh;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        
        #gameContainer {
            position: relative;
            width: 100vw;
            height: 100vh;
            height: 100dvh;
        }
        
        #gameCanvas {
            display: block;
            position: absolute;
            top: 0;
            left: 0;
        }
        
        #uiLayer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }
        
        #uiLayer > * { pointer-events: auto; }
        
        /* 国风边框组件 */
        .guofeng-frame {
            position: relative;
            border: 1px solid var(--border-gold);
            background: var(--bg-card);
            backdrop-filter: blur(10px);
        }
        
        .guofeng-frame::before,
        .guofeng-frame::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border: 2px solid var(--accent-gold);
            pointer-events: none;
        }
        
        .guofeng-frame::before {
            top: -1px;
            left: -1px;
            border-right: none;
            border-bottom: none;
        }
        
        .guofeng-frame::after {
            bottom: -1px;
            right: -1px;
            border-left: none;
            border-top: none;
        }
        
        .frame-corner-tr,
        .frame-corner-bl {
            position: absolute;
            width: 20px;
            height: 20px;
            border: 2px solid var(--accent-gold);
            pointer-events: none;
        }
        
        .frame-corner-tr {
            top: -1px;
            right: -1px;
            border-left: none;
            border-bottom: none;
        }
        
        .frame-corner-bl {
            bottom: -1px;
            left: -1px;
            border-right: none;
            border-top: none;
        }
        
        /* 水墨按钮 */
        .ink-btn {
            position: relative;
            padding: 10px 24px;
            background: linear-gradient(135deg, rgba(212, 165, 74, 0.15) 0%, rgba(212, 165, 74, 0.05) 100%);
            border: 1px solid var(--border-gold);
            border-radius: 4px;
            color: var(--accent-gold);
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            overflow: hidden;
        }
        
        .ink-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(212, 165, 74, 0.2), transparent);
            transition: left 0.5s ease;
        }
        
        .ink-btn:hover {
            background: linear-gradient(135deg, rgba(212, 165, 74, 0.3) 0%, rgba(212, 165, 74, 0.1) 100%);
            box-shadow: 0 0 20px rgba(212, 165, 74, 0.3), inset 0 0 10px rgba(212, 165, 74, 0.1);
            transform: translateY(-2px);
        }
        
        .ink-btn:hover::before {
            left: 100%;
        }
        
        .ink-btn:active {
            transform: translateY(0);
        }
        
        .ink-btn.primary {
            background: linear-gradient(135deg, rgba(62, 205, 196, 0.2) 0%, rgba(62, 205, 196, 0.05) 100%);
            border-color: rgba(62, 205, 196, 0.5);
            color: var(--accent-cyan);
        }
        
        .ink-btn.primary:hover {
            background: linear-gradient(135deg, rgba(62, 205, 196, 0.35) 0%, rgba(62, 205, 196, 0.15) 100%);
            box-shadow: 0 0 20px rgba(62, 205, 196, 0.3);
        }
        
        .ink-btn.danger {
            background: linear-gradient(135deg, rgba(214, 69, 69, 0.2) 0%, rgba(214, 69, 69, 0.05) 100%);
            border-color: rgba(214, 69, 69, 0.5);
            color: var(--accent-red);
        }
        
        .ink-btn.danger:hover {
            background: linear-gradient(135deg, rgba(214, 69, 69, 0.35) 0%, rgba(214, 69, 69, 0.15) 100%);
            box-shadow: 0 0 20px rgba(214, 69, 69, 0.3);
        }
        
        /* 顶部状态栏 */
        .top-bar {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            padding: 10px 16px;
            background: linear-gradient(180deg, rgba(8,8,16,0.98) 0%, rgba(8,8,16,0.6) 80%, transparent 100%);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 20;
        }
        
        .player-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .player-avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 2px solid var(--accent-gold);
            background: linear-gradient(135deg, #1a1a2e 0%, #0a0a1a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 20px;
            color: var(--accent-gold);
            box-shadow: 0 0 15px rgba(212, 165, 74, 0.3);
            position: relative;
        }
        
        .avatar-frame {
            position: absolute;
            inset: -4px;
            border: 1px solid var(--border-light);
            border-radius: 50%;
            animation: avatarPulse 3s ease-in-out infinite;
        }
        
        @keyframes avatarPulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.05); }
        }
        
        .player-stats { display: flex; flex-direction: column; gap: 2px; }
        .player-name { font-size: 14px; font-weight: 600; }
        .player-realm { font-size: 11px; color: var(--accent-cyan); }
        
        .top-resources {
            display: flex;
            gap: 12px;
        }
        
        .resource-mini {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            background: rgba(20, 20, 35, 0.8);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            font-size: 12px;
        }
        
        .resource-mini .icon {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }
        
        .resource-mini .icon.wood { background: linear-gradient(135deg, #5d4037, #3e2723); }
        .resource-mini .icon.spirit { background: linear-gradient(135deg, #1565c0, #0d47a1); }
        .resource-mini .icon.gold { background: linear-gradient(135deg, #d4a54a, #a67c00); }
        
        /* 主界面内容区 */
        .main-content {
            position: absolute;
            top: 70px;
            left: 0;
            right: 0;
            bottom: 80px;
            padding: 16px;
            overflow: hidden;
        }
        
        /* 页面容器 */
        .page-container {
            position: relative;
            width: 100%;
            height: 100%;
        }
        
        .page {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            visibility: hidden;
            transform: translateX(20px);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .page.active {
            opacity: 1;
            visibility: visible;
            transform: translateX(0);
        }
        
        /* 主页面 */
        .home-page {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        /* 角色卡片 */
        .character-card {
            guofeng-frame: true;
            padding: 16px;
            display: flex;
            gap: 16px;
        }
        
        .char-visual {
            width: 80px;
            height: 80px;
            border-radius: 8px;
            background: linear-gradient(135deg, #1a1a2e 0%, #0a0a1a 100%);
            border: 1px solid var(--border-gold);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        .char-visual::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 50% 30%, rgba(212, 165, 74, 0.1) 0%, transparent 70%);
        }
        
        .char-icon {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 36px;
            color: var(--accent-gold);
        }
        
        .char-details {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .char-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .char-name {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 20px;
            color: var(--accent-gold);
        }
        
        .char-level {
            font-size: 12px;
            color: var(--accent-cyan);
            padding: 2px 8px;
            background: rgba(62, 205, 196, 0.15);
            border-radius: 10px;
        }
        
        .char-realm-bar {
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .char-realm-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-gold));
            border-radius: 3px;
            transition: width 0.5s ease;
        }
        
        .char-stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }
        
        .stat-item {
            text-align: center;
            padding: 6px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
        }
        
        .stat-value {
            font-size: 14px;
            font-weight: 600;
            color: var(--fg-primary);
        }
        
        .stat-label {
            font-size: 10px;
            color: var(--fg-secondary);
        }
        
        /* 关卡信息 */
        .stage-card {
            padding: 16px;
        }
        
        .stage-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .stage-title {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 18px;
            color: var(--accent-gold);
        }
        
        .stage-enemy {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            margin-bottom: 12px;
        }
        
        .enemy-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2a1a1a 0%, #1a0a0a 100%);
            border: 2px solid var(--accent-red);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .enemy-info {
            flex: 1;
        }
        
        .enemy-name {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .enemy-hp-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .enemy-hp-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-red), #ff6b6b);
            transition: width 0.3s ease;
        }
        
        /* 快捷功能 */
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }
        
        .quick-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            padding: 12px 8px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border-light);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .quick-btn:hover {
            background: rgba(212, 165, 74, 0.1);
            border-color: var(--border-gold);
            transform: translateY(-2px);
        }
        
        .quick-btn .icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .quick-btn .label {
            font-size: 11px;
            color: var(--fg-secondary);
        }
        
        .quick-btn .badge {
            position: absolute;
            top: -4px;
            right: -4px;
            min-width: 16px;
            height: 16px;
            padding: 0 4px;
            background: var(--accent-red);
            border-radius: 8px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* 境界面板 */
        .realm-page {
            padding: 8px;
            overflow-y: auto;
        }
        
        .realm-current {
            padding: 20px;
            text-align: center;
            margin-bottom: 16px;
        }
        
        .realm-icon-big {
            width: 80px;
            height: 80px;
            margin: 0 auto 16px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(62, 205, 196, 0.2) 0%, transparent 70%);
            border: 2px solid var(--accent-cyan);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            animation: realmFloat 3s ease-in-out infinite;
        }
        
        @keyframes realmFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .realm-name-big {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 28px;
            color: var(--accent-cyan);
            margin-bottom: 8px;
        }
        
        .realm-desc {
            font-size: 12px;
            color: var(--fg-secondary);
            margin-bottom: 16px;
        }
        
        .realm-progress-ring {
            position: relative;
            width: 120px;
            height: 120px;
            margin: 0 auto 16px;
        }
        
        .realm-progress-ring svg {
            transform: rotate(-90deg);
        }
        
        .realm-progress-ring .bg {
            fill: none;
            stroke: rgba(255,255,255,0.1);
            stroke-width: 8;
        }
        
        .realm-progress-ring .progress {
            fill: none;
            stroke: url(#realmGradient);
            stroke-width: 8;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.5s ease;
        }
        
        .realm-progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        
        .realm-progress-text .percent {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent-gold);
        }
        
        .realm-progress-text .label {
            font-size: 10px;
            color: var(--fg-secondary);
        }
        
        .breakthrough-btn {
            margin-top: 16px;
        }
        
        .realm-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .realm-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border-light);
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .realm-item.current {
            background: rgba(62, 205, 196, 0.1);
            border-color: rgba(62, 205, 196, 0.3);
        }
        
        .realm-item.passed {
            opacity: 0.6;
        }
        
        .realm-item-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255,255,255,0.05);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .realm-item-info {
            flex: 1;
        }
        
        .realm-item-name {
            font-size: 14px;
            font-weight: 600;
        }
        
        .realm-item-bonus {
            font-size: 11px;
            color: var(--fg-secondary);
        }
        
        .realm-item-status {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
        }
        
        .realm-item-status.passed {
            background: rgba(69, 183, 108, 0.2);
            color: var(--accent-green);
        }
        
        .realm-item-status.current {
            background: rgba(62, 205, 196, 0.2);
            color: var(--accent-cyan);
        }
        
        /* 装备背包 */
        .equipment-page {
            display: flex;
            flex-direction: column;
            gap: 12px;
            height: 100%;
        }
        
        .equipped-section {
            padding: 16px;
        }
        
        .section-title {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 16px;
            color: var(--accent-gold);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-title::before {
            content: '';
            width: 3px;
            height: 14px;
            background: var(--accent-gold);
            border-radius: 2px;
        }
        
        .equipped-slots {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 8px;
        }
        
        .equip-slot {
            aspect-ratio: 1;
            background: rgba(255,255,255,0.03);
            border: 1px dashed var(--border-light);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .equip-slot:hover {
            border-style: solid;
            border-color: var(--border-gold);
            background: rgba(212, 165, 74, 0.1);
        }
        
        .equip-slot.filled {
            border-style: solid;
        }
        
        .equip-slot .slot-icon {
            font-size: 24px;
            opacity: 0.3;
        }
        
        .equip-slot .item-icon {
            width: 100%;
            height: 100%;
            border-radius: 7px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .equip-slot .slot-label {
            position: absolute;
            bottom: 2px;
            font-size: 8px;
            color: var(--fg-muted);
        }
        
        .bag-section {
            flex: 1;
            padding: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .bag-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .bag-tabs {
            display: flex;
            gap: 4px;
        }
        
        .bag-tab {
            padding: 4px 12px;
            font-size: 12px;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 12px;
            color: var(--fg-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .bag-tab:hover {
            color: var(--fg-primary);
        }
        
        .bag-tab.active {
            background: rgba(212, 165, 74, 0.15);
            border-color: var(--border-gold);
            color: var(--accent-gold);
        }
        
        .bag-grid {
            flex: 1;
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            overflow-y: auto;
            padding-right: 4px;
        }
        
        .bag-item {
            aspect-ratio: 1;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border-light);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .bag-item:hover {
            transform: scale(1.05);
            z-index: 5;
        }
        
        .bag-item .item-icon {
            width: 100%;
            height: 100%;
            border-radius: 7px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }
        
        .bag-item .item-level {
            position: absolute;
            top: 2px;
            right: 2px;
            font-size: 9px;
            padding: 0 4px;
            background: rgba(0,0,0,0.6);
            border-radius: 4px;
        }
        
        .bag-item.empty {
            opacity: 0.3;
        }
        
        /* 品质颜色 */
        .quality-common { background: linear-gradient(135deg, rgba(138, 138, 154, 0.3), rgba(138, 138, 154, 0.1)); border-color: var(--quality-common); }
        .quality-good { background: linear-gradient(135deg, rgba(76, 175, 80, 0.3), rgba(76, 175, 80, 0.1)); border-color: var(--quality-good); }
        .quality-rare { background: linear-gradient(135deg, rgba(33, 150, 243, 0.3), rgba(33, 150, 243, 0.1)); border-color: var(--quality-rare); }
        .quality-epic { background: linear-gradient(135deg, rgba(156, 39, 176, 0.3), rgba(156, 39, 176, 0.1)); border-color: var(--quality-epic); }
        .quality-legend { background: linear-gradient(135deg, rgba(255, 152, 0, 0.3), rgba(255, 152, 0, 0.1)); border-color: var(--quality-legend); }
        .quality-mythic { background: linear-gradient(135deg, rgba(244, 67, 54, 0.3), rgba(244, 67, 54, 0.1)); border-color: var(--quality-mythic); }
        
        /* 灵兽图鉴 */
        .beast-page {
            padding: 8px;
            overflow-y: auto;
        }
        
        .beast-showcase {
            padding: 20px;
            text-align: center;
            margin-bottom: 16px;
        }
        
        .beast-avatar-big {
            width: 100px;
            height: 100px;
            margin: 0 auto 16px;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(156, 100, 181, 0.3) 0%, rgba(156, 100, 181, 0.1) 100%);
            border: 2px solid var(--accent-purple);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            position: relative;
            overflow: hidden;
        }
        
        .beast-avatar-big::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.3) 100%);
        }
        
        .beast-name-big {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 24px;
            color: var(--accent-purple);
            margin-bottom: 4px;
        }
        
        .beast-level {
            font-size: 12px;
            color: var(--fg-secondary);
            margin-bottom: 12px;
        }
        
        .beast-stars {
            display: flex;
            justify-content: center;
            gap: 4px;
            margin-bottom: 16px;
        }
        
        .beast-stars .star {
            font-size: 16px;
            color: var(--accent-gold);
        }
        
        .beast-stats {
            display: flex;
            justify-content: center;
            gap: 24px;
        }
        
        .beast-stat {
            text-align: center;
        }
        
        .beast-stat .value {
            font-size: 18px;
            font-weight: 600;
            color: var(--accent-gold);
        }
        
        .beast-stat .label {
            font-size: 10px;
            color: var(--fg-secondary);
        }
        
        .beast-list {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }
        
        .beast-card {
            padding: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .beast-card:hover {
            transform: translateY(-4px);
        }
        
        .beast-card.selected {
            background: rgba(156, 100, 181, 0.15);
        }
        
        .beast-card .avatar {
            width: 56px;
            height: 56px;
            margin: 0 auto 8px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }
        
        .beast-card .name {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .beast-card .type {
            font-size: 10px;
            color: var(--fg-secondary);
        }
        
        /* 设置页面 */
        .settings-page {
            padding: 8px;
            overflow-y: auto;
        }
        
        .settings-group {
            margin-bottom: 16px;
            padding: 16px;
        }
        
        .settings-group-title {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 16px;
            color: var(--accent-gold);
            margin-bottom: 12px;
        }
        
        .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .setting-item:last-child {
            border-bottom: none;
        }
        
        .setting-label {
            font-size: 14px;
        }
        
        .setting-desc {
            font-size: 11px;
            color: var(--fg-secondary);
            margin-top: 2px;
        }
        
        /* 开关 */
        .toggle-switch {
            width: 48px;
            height: 26px;
            background: rgba(255,255,255,0.1);
            border-radius: 13px;
            position: relative;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .toggle-switch.on {
            background: var(--accent-cyan);
        }
        
        .toggle-switch::after {
            content: '';
            position: absolute;
            top: 3px;
            left: 3px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s ease;
        }
        
        .toggle-switch.on::after {
            transform: translateX(22px);
        }
        
        /* 滑块 */
        .slider-control {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .slider {
            width: 120px;
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            position: relative;
            cursor: pointer;
        }
        
        .slider-fill {
            height: 100%;
            background: var(--accent-gold);
            border-radius: 2px;
        }
        
        .slider-thumb {
            position: absolute;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 16px;
            height: 16px;
            background: var(--accent-gold);
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(212, 165, 74, 0.5);
        }
        
        .slider-value {
            font-size: 12px;
            color: var(--fg-secondary);
            min-width: 36px;
            text-align: right;
        }
        
        .about-section {
            text-align: center;
            padding: 24px 16px;
        }
        
        .game-logo {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 32px;
            color: var(--accent-gold);
            margin-bottom: 8px;
        }
        
        .game-version {
            font-size: 12px;
            color: var(--fg-secondary);
            margin-bottom: 16px;
        }
        
        /* 底部导航 */
        .bottom-nav {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 76px;
            padding-bottom: env(safe-area-inset-bottom);
            background: linear-gradient(0deg, rgba(8,8,16,0.98) 0%, rgba(8,8,16,0.9) 80%, transparent 100%);
            display: flex;
            justify-content: space-around;
            align-items: flex-start;
            padding-top: 8px;
            z-index: 30;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 8px 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .nav-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 32px;
            height: 3px;
            background: var(--accent-gold);
            border-radius: 2px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .nav-item.active::before {
            opacity: 1;
        }
        
        .nav-icon {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: transform 0.3s ease;
        }
        
        .nav-item.active .nav-icon {
            color: var(--accent-gold);
            transform: scale(1.1);
        }
        
        .nav-item:not(.active) .nav-icon {
            color: var(--fg-secondary);
        }
        
        .nav-label {
            font-size: 10px;
            transition: color 0.3s ease;
        }
        
        .nav-item.active .nav-label {
            color: var(--accent-gold);
        }
        
        .nav-item:not(.active) .nav-label {
            color: var(--fg-secondary);
        }
        
        /* 物品详情弹窗 */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .modal-overlay.show {
            opacity: 1;
            visibility: visible;
        }
        
        .modal-content {
            width: 90%;
            max-width: 340px;
            padding: 24px;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        
        .modal-overlay.show .modal-content {
            transform: scale(1);
        }
        
        .modal-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .modal-item-icon {
            width: 64px;
            height: 64px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
        }
        
        .modal-item-info {
            flex: 1;
        }
        
        .modal-item-name {
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 20px;
            margin-bottom: 4px;
        }
        
        .modal-item-type {
            font-size: 12px;
            color: var(--fg-secondary);
        }
        
        .modal-stats {
            padding: 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            margin-bottom: 16px;
        }
        
        .modal-stat-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 13px;
        }
        
        .modal-stat-row .label {
            color: var(--fg-secondary);
        }
        
        .modal-stat-row .value {
            color: var(--accent-green);
        }
        
        .modal-actions {
            display: flex;
            gap: 12px;
        }
        
        .modal-actions .ink-btn {
            flex: 1;
        }
        
        .modal-close {
            position: absolute;
            top: 12px;
            right: 12px;
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 50%;
            color: var(--fg-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .modal-close:hover {
            background: rgba(255,255,255,0.2);
            color: var(--fg-primary);
        }
        
        /* 滚动条美化 */
        ::-webkit-scrollbar {
            width: 4px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-gold);
            border-radius: 2px;
        }
        
        /* 动画 */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-in {
            animation: fadeInUp 0.5s ease forwards;
        }
        
        /* 响应式 */
        @media (max-width: 360px) {
            .top-resources {
                gap: 8px;
            }
            
            .resource-mini {
                padding: 4px 8px;
                font-size: 11px;
            }
            
            .equipped-slots {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .bag-grid {
                grid-template-columns: repeat(4, 1fr);
            }
            
            .beast-list {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        
        <div id="uiLayer">
            <!-- 顶部状态栏 -->
            <div class="top-bar">
                <div class="player-info">
                    <div class="player-avatar">
                        <div class="avatar-frame"></div>
                        <span>妖</span>
                    </div>
                    <div class="player-stats">
                        <div class="player-name">青云小妖</div>
                        <div class="player-realm">筑基初期</div>
                    </div>
                </div>
                <div class="top-resources">
                    <div class="resource-mini">
                        <div class="icon wood">木</div>
                        <span id="woodCount">12,580</span>
                    </div>
                    <div class="resource-mini">
                        <div class="icon spirit">灵</div>
                        <span id="spiritCount">3,240</span>
                    </div>
                    <div class="resource-mini">
                        <div class="icon gold">金</div>
                        <span id="goldCount">856</span>
                    </div>
                </div>
            </div>
            
            <!-- 主内容区 -->
            <div class="main-content">
                <div class="page-container">
                    <!-- 主页面 -->
                    <div class="page home-page active" id="page-home">
                        <div class="guofeng-frame character-card">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="char-visual">
                                <span class="char-icon">妖</span>
                            </div>
                            <div class="char-details">
                                <div class="char-header">
                                    <span class="char-name">青云小妖</span>
                                    <span class="char-level">Lv.36</span>
                                </div>
                                <div class="char-realm-bar">
                                    <div class="char-realm-fill" style="width: 65%"></div>
                                </div>
                                <div class="char-stats-grid">
                                    <div class="stat-item">
                                        <div class="stat-value" id="statAtk">2,458</div>
                                        <div class="stat-label">攻击</div>
                                    </div>
                                    <div class="stat-item">
                                        <div class="stat-value" id="statDef">1,892</div>
                                        <div class="stat-label">防御</div>
                                    </div>
                                    <div class="stat-item">
                                        <div class="stat-value" id="statHp">28.5K</div>
                                        <div class="stat-label">生命</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="guofeng-frame stage-card">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="stage-header">
                                <span class="stage-title">万妖森林</span>
                                <span style="font-size:12px;color:var(--fg-secondary)">第 36 关</span>
                            </div>
                            <div class="stage-enemy">
                                <div class="enemy-avatar">虎</div>
                                <div class="enemy-info">
                                    <div class="enemy-name">千年虎妖</div>
                                    <div class="enemy-hp-bar">
                                        <div class="enemy-hp-fill" id="enemyHpFill" style="width: 78%"></div>
                                    </div>
                                </div>
                            </div>
                            <div style="display:flex;gap:12px;">
                                <button class="ink-btn" style="flex:1" onclick="simulateBattle()">挑战</button>
                                <button class="ink-btn primary" style="flex:1">扫荡 x5</button>
                            </div>
                        </div>
                        
                        <div class="quick-actions">
                            <div class="quick-btn" onclick="switchPage('realm')">
                                <div class="icon" style="background:linear-gradient(135deg,rgba(62,205,196,0.3),rgba(62,205,196,0.1))">境</div>
                                <span class="label">境界</span>
                            </div>
                            <div class="quick-btn" onclick="switchPage('equipment')">
                                <div class="icon" style="background:linear-gradient(135deg,rgba(212,165,74,0.3),rgba(212,165,74,0.1))">装</div>
                                <span class="label">装备</span>
                            </div>
                            <div class="quick-btn" onclick="switchPage('beast')">
                                <div class="icon" style="background:linear-gradient(135deg,rgba(156,100,181,0.3),rgba(156,100,181,0.1))">兽</div>
                                <span class="label">灵兽</span>
                            </div>
                            <div class="quick-btn" onclick="switchPage('settings')">
                                <div class="icon" style="background:linear-gradient(135deg,rgba(122,122,138,0.3),rgba(122,122,138,0.1))">设</div>
                                <span class="label">设置</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 境界面板 -->
                    <div class="page realm-page" id="page-realm">
                        <div class="guofeng-frame realm-current">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="realm-icon-big">筑</div>
                            <div class="realm-name-big">筑基期</div>
                            <div class="realm-desc">凝气成基，初窥仙门</div>
                            
                            <div class="realm-progress-ring">
                                <svg width="120" height="120">
                                    <defs>
                                        <linearGradient id="realmGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" style="stop-color:#3ecdc4"/>
                                            <stop offset="100%" style="stop-color:#d4a54a"/>
                                        </linearGradient>
                                    </defs>
                                    <circle class="bg" cx="60" cy="60" r="52"/>
                                    <circle class="progress" cx="60" cy="60" r="52" 
                                        stroke-dasharray="327" 
                                        stroke-dashoffset="115"
                                        id="realmProgressCircle"/>
                                </svg>
                                <div class="realm-progress-text">
                                    <div class="percent">65%</div>
                                    <div class="label">突破进度</div>
                                </div>
                            </div>
                            
                            <button class="ink-btn primary breakthrough-btn" onclick="simulateBreakthrough()">
                                突破境界
                            </button>
                        </div>
                        
                        <div class="guofeng-frame" style="padding:16px">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="section-title">修仙境界</div>
                            <div class="realm-list" id="realmList"></div>
                        </div>
                    </div>
                    
                    <!-- 装备背包 -->
                    <div class="page equipment-page" id="page-equipment">
                        <div class="guofeng-frame equipped-section">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="section-title">已装备</div>
                            <div class="equipped-slots" id="equippedSlots"></div>
                        </div>
                        
                        <div class="guofeng-frame bag-section">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="bag-header">
                                <div class="section-title" style="margin-bottom:0">背包</div>
                                <div class="bag-tabs">
                                    <button class="bag-tab active" data-type="all">全部</button>
                                    <button class="bag-tab" data-type="weapon">武器</button>
                                    <button class="bag-tab" data-type="armor">防具</button>
                                    <button class="bag-tab" data-type="accessory">饰品</button>
                                </div>
                            </div>
                            <div class="bag-grid" id="bagGrid"></div>
                        </div>
                    </div>
                    
                    <!-- 灵兽图鉴 -->
                    <div class="page beast-page" id="page-beast">
                        <div class="guofeng-frame beast-showcase">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="beast-avatar-big" id="showcaseAvatar">狐</div>
                            <div class="beast-name-big" id="showcaseName">九尾灵狐</div>
                            <div class="beast-level" id="showcaseLevel">Lv.42 · 神兽</div>
                            <div class="beast-stars" id="showcaseStars"></div>
                            <div class="beast-stats">
                                <div class="beast-stat">
                                    <div class="value" id="beastAtk">+1,280</div>
                                    <div class="label">攻击加成</div>
                                </div>
                                <div class="beast-stat">
                                    <div class="value" id="beastDef">+860</div>
                                    <div class="label">防御加成</div>
                                </div>
                                <div class="beast-stat">
                                    <div class="value" id="beastHp">+12.5K</div>
                                    <div class="label">生命加成</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="guofeng-frame" style="padding:16px">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="section-title">灵兽列表</div>
                            <div class="beast-list" id="beastList"></div>
                        </div>
                    </div>
                    
                    <!-- 设置页面 -->
                    <div class="page settings-page" id="page-settings">
                        <div class="about-section">
                            <div class="game-logo">寻道大千</div>
                            <div class="game-version">版本 1.0.0</div>
                        </div>
                        
                        <div class="guofeng-frame settings-group">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="settings-group-title">音频设置</div>
                            <div class="setting-item">
                                <div>
                                    <div class="setting-label">背景音乐</div>
                                    <div class="setting-desc">游戏背景音乐开关</div>
                                </div>
                                <div class="toggle-switch on" id="toggleBgm" onclick="toggleSwitch(this)"></div>
                            </div>
                            <div class="setting-item">
                                <div>
                                    <div class="setting-label">音效</div>
                                    <div class="setting-desc">游戏音效开关</div>
                                </div>
                                <div class="toggle-switch on" id="toggleSfx" onclick="toggleSwitch(this)"></div>
                            </div>
                            <div class="setting-item">
                                <div>
                                    <div class="setting-label">音量大小</div>
                                </div>
                                <div class="slider-control">
                                    <div class="slider" id="volumeSlider" onclick="handleSlider(event, this)">
                                        <div class="slider-fill" style="width:70%"></div>
                                        <div class="slider-thumb" style="left:70%"></div>
                                    </div>
                                    <span class="slider-value">70%</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="guofeng-frame settings-group">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="settings-group-title">游戏设置</div>
                            <div class="setting-item">
                                <div>
                                    <div class="setting-label">战斗特效</div>
                                    <div class="setting-desc">战斗时的技能特效显示</div>
                                </div>
                                <div class="toggle-switch on" onclick="toggleSwitch(this)"></div>
                            </div>
                            <div class="setting-item">
                                <div>
                                    <div class="setting-label">自动战斗</div>
                                    <div class="setting-desc">进入关卡自动开始战斗</div>
                                </div>
                                <div class="toggle-switch on" onclick="toggleSwitch(this)"></div>
                            </div>
                            <div class="setting-item">
                                <div>
                                    <div class="setting-label">离线收益提醒</div>
                                </div>
                                <div class="toggle-switch" onclick="toggleSwitch(this)"></div>
                            </div>
                        </div>
                        
                        <div class="guofeng-frame settings-group">
                            <div class="frame-corner-tr"></div>
                            <div class="frame-corner-bl"></div>
                            <div class="settings-group-title">账号信息</div>
                            <div class="setting-item">
                                <div class="setting-label">玩家ID</div>
                                <div style="font-size:12px;color:var(--fg-secondary)">10086520</div>
                            </div>
                            <div class="setting-item">
                                <div class="setting-label">服务器</div>
                                <div style="font-size:12px;color:var(--fg-secondary)">天机阁 · 1区</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 底部导航 -->
            <div class="bottom-nav">
                <div class="nav-item active" data-page="home" onclick="switchPage('home')">
                    <div class="nav-icon">域</div>
                    <span class="nav-label">主界面</span>
                </div>
                <div class="nav-item" data-page="realm" onclick="switchPage('realm')">
                    <div class="nav-icon">境</div>
                    <span class="nav-label">境界</span>
                </div>
                <div class="nav-item" data-page="equipment" onclick="switchPage('equipment')">
                    <div class="nav-icon">囊</div>
                    <span class="nav-label">背包</span>
                </div>
                <div class="nav-item" data-page="beast" onclick="switchPage('beast')">
                    <div class="nav-icon">兽</div>
                    <span class="nav-label">灵兽</span>
                </div>
                <div class="nav-item" data-page="settings" onclick="switchPage('settings')">
                    <div class="nav-icon">设</div>
                    <span class="nav-label">设置</span>
                </div>
            </div>
        </div>
        
        <!-- 物品详情弹窗 -->
        <div class="modal-overlay" id="itemModal">
            <div class="guofeng-frame modal-content">
                <div class="frame-corner-tr"></div>
                <div class="frame-corner-bl"></div>
                <button class="modal-close" onclick="closeModal()">✕</button>
                <div class="modal-header">
                    <div class="modal-item-icon quality-epic" id="modalIcon">剑</div>
                    <div class="modal-item-info">
                        <div class="modal-item-name" style="color:var(--quality-epic)" id="modalName">青云剑</div>
                        <div class="modal-item-type" id="modalType">武器 · 紫色品质</div>
                    </div>
                </div>
                <div class="modal-stats" id="modalStats">
                    <div class="modal-stat-row">
                        <span class="label">攻击力</span>
                        <span class="value">+1,280</span>
                    </div>
                    <div class="modal-stat-row">
                        <span class="label">暴击率</span>
                        <span class="value">+8%</span>
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="ink-btn" onclick="closeModal()">关闭</button>
                    <button class="ink-btn primary" id="modalAction">装备</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ==================== 游戏数据 ====================
        const GameData = {
            player: {
                name: '青云小妖',
                level: 36,
                realm: '筑基初期',
                realmProgress: 65,
                stats: { atk: 2458, def: 1892, hp: 28500 }
            },
            resources: { wood: 12580, spirit: 3240, gold: 856 },
            currentStage: 36
        };
        
        // 境界数据
        const realmData = [
            { name: '练气期', icon: '气', desc: '初入修仙', bonus: '基础属性+5%', status: 'passed' },
            { name: '筑基期', icon: '筑', desc: '凝气成基', bonus: '基础属性+15%', status: 'current' },
            { name: '金丹期', icon: '丹', desc: '结丹化形', bonus: '基础属性+30%', status: 'locked' },
            { name: '元婴期', icon: '婴', desc: '元婴出窍', bonus: '基础属性+50%', status: 'locked' },
            { name: '化神期', icon: '神', desc: '化神通玄', bonus: '基础属性+80%', status: 'locked' },
            { name: '渡劫期', icon: '劫', desc: '渡劫飞升', bonus: '基础属性+120%', status: 'locked' }
        ];
        
        // 装备槽位配置
        const equipSlots = [
            { id: 'weapon', label: '武器', icon: '剑' },
            { id: 'helmet', label: '头盔', icon: '盔' },
            { id: 'armor', label: '护甲', icon: '甲' },
            { id: 'belt', label: '腰带', icon: '带' },
            { id: 'boots', label: '鞋子', icon: '靴' },
            { id: 'accessory', label: '饰品', icon: '佩' }
        ];
        
        // 背包装备数据
        const bagItems = [
            { id: 1, name: '青云剑', icon: '剑', type: 'weapon', quality: 'epic', level: 35, stats: { atk: 1280, crit: 8 } },
            { id: 2, name: '玄铁甲', icon: '甲', type: 'armor', quality: 'rare', level: 32, stats: { def: 860, hp: 1200 } },
            { id: 3, name: '灵玉佩', icon: '佩', type: 'accessory', quality: 'legend', level: 38, stats: { atk: 520, def: 380, hp: 2500 } },
            { id: 4, name: '疾风靴', icon: '靴', type: 'boots', quality: 'good', level: 28, stats: { def: 320, dodge: 5 } },
            { id: 5, name: '龙纹带', icon: '带', type: 'belt', quality: 'rare', level: 33, stats: { hp: 2800, def: 280 } },
            { id: 6, name: '星陨剑', icon: '剑', type: 'weapon', quality: 'mythic', level: 42, stats: { atk: 2680, crit: 15 } },
            { id: 7, name: '凤羽盔', icon: '盔', type: 'helmet', quality: 'legend', level: 36, stats: { def: 680, hp: 1800 } },
            { id: 8, name: '灵木杖', icon: '剑', type: 'weapon', quality: 'common', level: 20, stats: { atk: 380 } },
            { id: 9, name: '青竹甲', icon: '甲', type: 'armor', quality: 'common', level: 22, stats: { def: 420 } },
            { id: 10, name: '碧波佩', icon: '佩', type: 'accessory', quality: 'good', level: 30, stats: { atk: 280, hp: 800 } },
            { id: 11, name: '玄铁盔', icon: '盔', type: 'helmet', quality: 'rare', level: 31, stats: { def: 520, hp: 600 } },
            { id: 12, name: '金丝甲', icon: '甲', type: 'armor', quality: 'epic', level: 37, stats: { def: 1120, hp: 2000 } },
            null, null, null, null, null, null, null, null
        ];
        
        // 已装备数据
        const equippedData = {
            weapon: { name: '青云剑', icon: '剑', quality: 'epic' },
            helmet: null,
            armor: { name: '玄铁甲', icon: '甲', quality: 'rare' },
            belt: { name: '龙纹带', icon: '带', quality: 'rare' },
            boots: null,
            accessory: { name: '灵玉佩', icon: '佩', quality: 'legend' }
        };
        
        // 灵兽数据
        const beastData = [
            { id: 1, name: '九尾灵狐', icon: '狐', type: '神兽', stars: 5, atk: 1280, def: 860, hp: 12500, selected: true },
            { id: 2, name: '玄武神龟', icon: '龟', type: '神兽', stars: 5, atk: 680, def: 1860, hp: 25000 },
            { id: 3, name: '朱雀', icon: '雀', type: '仙兽', stars: 4, atk: 1580, def: 520, hp: 8600 },
            { id: 4, name: '白虎', icon: '虎', type: '仙兽', stars: 4, atk: 1380, def: 780, hp: 9200 },
            { id: 5, name: '青龙', icon: '龙', type: '仙兽', stars: 4, atk: 1120, def: 980, hp: 11000 },
            { id: 6, name: '灵鹿', icon: '鹿', type: '灵兽', stars: 3, atk: 580, def: 420, hp: 5200 },
            { id: 7, name: '玄豹', icon: '豹', type: '灵兽', stars: 3, atk: 720, def: 380, hp: 4200 },
            { id: 8, name: '灵鹤', icon: '鹤', type: '灵兽', stars: 3, atk: 480, def: 480, hp: 5800 },
            { id: 9, name: '山狼', icon: '狼', type: '凡兽', stars: 2, atk: 320, def: 280, hp: 3200 }
        ];
        
        // ==================== Canvas 背景 ====================
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        let animationId = null;
        let particles = [];
        let time = 0;
        
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        
        function initParticles() {
            particles = [];
            const count = Math.min(50, Math.floor(canvas.width * canvas.height / 15000));
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 3 + 1,
                    speedX: (Math.random() - 0.5) * 0.3,
                    speedY: -Math.random() * 0.5 - 0.2,
                    opacity: Math.random() * 0.5 + 0.2,
                    hue: Math.random() * 40 + 30
                });
            }
        }
        
        function drawBackground() {
            // 渐变背景
            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            gradient.addColorStop(0, '#0a0a14');
            gradient.addColorStop(0.5, '#0f0f1f');
            gradient.addColorStop(1, '#080810');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 水墨山峦
            drawInkMountains();
            
            // 云雾
            drawMist();
            
            // 粒子
            drawParticles();
        }
        
        function drawInkMountains() {
            const baseY = canvas.height * 0.6;
            
            // 远山
            ctx.fillStyle = 'rgba(20, 20, 40, 0.6)';
            ctx.beginPath();
            ctx.moveTo(0, canvas.height);
            
            for (let x = 0; x <= canvas.width; x += 20) {
                const y = baseY + Math.sin(x * 0.005 + time * 0.0003) * 30 
                        + Math.sin(x * 0.01) * 20;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(canvas.width, canvas.height);
            ctx.closePath();
            ctx.fill();
            
            // 近山
            ctx.fillStyle = 'rgba(15, 15, 30, 0.8)';
            ctx.beginPath();
            ctx.moveTo(0, canvas.height);
            
            for (let x = 0; x <= canvas.width; x += 15) {
                const y = baseY + 60 + Math.sin(x * 0.008 + 1) * 40 
                        + Math.sin(x * 0.003 + time * 0.0002) * 25;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(canvas.width, canvas.height);
            ctx.closePath();
            ctx.fill();
        }
        
        function drawMist() {
            const mistY = canvas.height * 0.7;
            
            for (let i = 0; i < 3; i++) {
                const gradient = ctx.createRadialGradient(
                    canvas.width * (0.2 + i * 0.3), mistY,
                    0,
                    canvas.width * (0.2 + i * 0.3), mistY,
                    Math.max(1, canvas.width * 0.25)
                );
                gradient.addColorStop(0, 'rgba(60, 60, 80, 0.15)');
                gradient.addColorStop(0.5, 'rgba(40, 40, 60, 0.08)');
                gradient.addColorStop(1, 'rgba(30, 30, 50, 0)');
                
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
        }
        
        function drawParticles() {
            particles.forEach(p => {
                p.x += p.speedX;
                p.y += p.speedY;
                
                if (p.y < -10) {
                    p.y = canvas.height + 10;
                    p.x = Math.random() * canvas.width;
                }
                if (p.x < -10) p.x = canvas.width + 10;
                if (p.x > canvas.width + 10) p.x = -10;
                
                const glowGradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, Math.max(1, p.size * 3));
                glowGradient.addColorStop(0, `hsla(${p.hue}, 50%, 70%, ${p.opacity})`);
                glowGradient.addColorStop(0.5, `hsla(${p.hue}, 40%, 50%, ${p.opacity * 0.5})`);
                glowGradient.addColorStop(1, 'transparent');
                
                ctx.fillStyle = glowGradient;
                ctx.beginPath();
                ctx.arc(p.x, p.y, Math.max(1, p.size * 3), 0, Math.PI * 2);
                ctx.fill();
            });
        }
        
        function gameLoop() {
            time++;
            drawBackground();
            animationId = requestAnimationFrame(gameLoop);
        }
        
        // ==================== UI 功能 ====================
        let currentPage = 'home';
        
        function switchPage(pageId) {
            if (currentPage === pageId) return;
            
            // 切换页面
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            const targetPage = document.getElementById(`page-${pageId}`);
            if (targetPage) {
                targetPage.classList.add('active');
            }
            
            // 切换导航
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            const targetNav = document.querySelector(`.nav-item[data-page="${pageId}"]`);
            if (targetNav) {
                targetNav.classList.add('active');
            }
            
            currentPage = pageId;
        }
        
        // 渲染境界列表
        function renderRealmList() {
            const container = document.getElementById('realmList');
            if (!container) return;
            
            container.innerHTML = realmData.map(realm => `
                <div class="realm-item ${realm.status}">
                    <div class="realm-item-icon">${realm.icon}</div>
                    <div class="realm-item-info">
                        <div class="realm-item-name">${realm.name}</div>
                        <div class="realm-item-bonus">${realm.bonus}</div>
                    </div>
                    <span class="realm-item-status ${realm.status}">
                        ${realm.status === 'passed' ? '已突破' : realm.status === 'current' ? '修炼中' : '未解锁'}
                    </span>
                </div>
            `).join('');
        }
        
        // 渲染装备槽
        function renderEquippedSlots() {
            const container = document.getElementById('equippedSlots');
            if (!container) return;
            
            container.innerHTML = equipSlots.map(slot => {
                const equipped = equippedData[slot.id];
                return `
                    <div class="equip-slot ${equipped ? 'filled' : ''}" 
                         onclick="${equipped ? `showEquipDetail('${slot.id}')` : ''}">
                        ${equipped 
                            ? `<div class="item-icon quality-${equipped.quality}">${equipped.icon}</div>`
                            : `<span class="slot-icon">${slot.icon}</span><span class="slot-label">${slot.label}</span>`
                        }
                    </div>
                `;
            }).join('');
        }
        
        // 渲染背包
        let currentBagFilter = 'all';
        
        function renderBagGrid() {
            const container = document.getElementById('bagGrid');
            if (!container) return;
            
            const filteredItems = currentBagFilter === 'all' 
                ? bagItems 
                : bagItems.filter(item => item && item.type === currentBagFilter);
            
            container.innerHTML = filteredItems.map((item, index) => {
                if (!item) {
                    return `<div class="bag-item empty"></div>`;
                }
                return `
                    <div class="bag-item" onclick="showItemModal(${item.id})">
                        <div class="item-icon quality-${item.quality}">${item.icon}</div>
                        <span class="item-level">+${item.level}</span>
                    </div>
                `;
            }).join('');
        }
        
        // 背包筛选
        function initBagTabs() {
            document.querySelectorAll('.bag-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.bag-tab').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    currentBagFilter = this.dataset.type;
                    renderBagGrid();
                });
            });
        }
        
        // 渲染灵兽列表
        function renderBeastList() {
            const container = document.getElementById('beastList');
            if (!container) return;
            
            container.innerHTML = beastData.map(beast => `
                <div class="guofeng-frame beast-card ${beast.selected ? 'selected' : ''}" 
                     onclick="selectBeast(${beast.id})">
                    <div class="frame-corner-tr"></div>
                    <div class="frame-corner-bl"></div>
                    <div class="avatar quality-${beast.stars >= 5 ? 'mythic' : beast.stars >= 4 ? 'legend' : 'epic'}">
                        ${beast.icon}
                    </div>
                    <div class="name">${beast.name}</div>
                    <div class="type">${beast.type}</div>
                </div>
            `).join('');
        }
        
        // 选择灵兽
        function selectBeast(id) {
            const beast = beastData.find(b => b.id === id);
            if (!beast) return;
            
            // 更新选中状态
            beastData.forEach(b => b.selected = b.id === id);
            renderBeastList();
            
            // 更新展示
            document.getElementById('showcaseAvatar').textContent = beast.icon;
            document.getElementById('showcaseName').textContent = beast.name;
            document.getElementById('showcaseLevel').textContent = `Lv.${30 + beast.stars * 5} · ${beast.type}`;
            
            // 星星
            const starsContainer = document.getElementById('showcaseStars');
            starsContainer.innerHTML = Array(5).fill(0).map((_, i) => 
                `<span class="star" style="opacity:${i < beast.stars ? 1 : 0.3}">★</span>`
            ).join('');
            
            // 属性
            document.getElementById('beastAtk').textContent = `+${beast.atk.toLocaleString()}`;
            document.getElementById('beastDef').textContent = `+${beast.def.toLocaleString()}`;
            document.getElementById('beastHp').textContent = `+${(beast.hp / 1000).toFixed(1)}K`;
        }
        
        // 显示物品弹窗
        function showItemModal(id) {
            const item = bagItems.find(i => i && i.id === id);
            if (!item) return;
            
            const qualityNames = {
                common: '白色', good: '绿色', rare: '蓝色', 
                epic: '紫色', legend: '橙色', mythic: '红色'
            };
            
            document.getElementById('modalIcon').className = `modal-item-icon quality-${item.quality}`;
            document.getElementById('modalIcon').textContent = item.icon;
            document.getElementById('modalName').textContent = item.name;
            document.getElementById('modalName').style.color = `var(--quality-${item.quality})`;
            document.getElementById('modalType').textContent = `装备 · ${qualityNames[item.quality]}品质`;
            
            // 属性
            const statsContainer = document.getElementById('modalStats');
            let statsHtml = '';
            if (item.stats.atk) statsHtml += `<div class="modal-stat-row"><span class="label">攻击力</span><span class="value">+${item.stats.atk.toLocaleString()}</span></div>`;
            if (item.stats.def) statsHtml += `<div class="modal-stat-row"><span class="label">防御力</span><span class="value">+${item.stats.def.toLocaleString()}</span></div>`;
            if (item.stats.hp) statsHtml += `<div class="modal-stat-row"><span class="label">生命值</span><span class="value">+${item.stats.hp.toLocaleString()}</span></div>`;
            if (item.stats.crit) statsHtml += `<div class="modal-stat-row"><span class="label">暴击率</span><span class="value">+${item.stats.crit}%</span></div>`;
            if (item.stats.dodge) statsHtml += `<div class="modal-stat-row"><span class="label">闪避率</span><span class="value">+${item.stats.dodge}%</span></div>`;
            statsContainer.innerHTML = statsHtml;
            
            document.getElementById('itemModal').classList.add('show');
        }
        
        function closeModal() {
            document.getElementById('itemModal').classList.remove('show');
        }
        
        // 开关切换
        function toggleSwitch(el) {
            el.classList.toggle('on');
        }
        
        // 滑块处理
        function handleSlider(event, slider) {
            const rect = slider.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
            
            slider.querySelector('.slider-fill').style.width = percent + '%';
            slider.querySelector('.slider-thumb').style.left = percent + '%';
            slider.parentElement.querySelector('.slider-value').textContent = Math.round(percent) + '%';
        }
        
        // 模拟战斗
        function simulateBattle() {
            const hpFill = document.getElementById('enemyHpFill');
            let hp = 78;
            
            const battleInterval = setInterval(() => {
                hp -= Math.random() * 8 + 3;
                if (hp <= 0) {
                    hp = 100;
                    hpFill.style.width = '100%';
                    clearInterval(battleInterval);
                    
                    // 增加资源
                    GameData.resources.wood += Math.floor(Math.random() * 500 + 200);
                    GameData.resources.spirit += Math.floor(Math.random() * 100 + 50);
                    updateResourceDisplay();
                } else {
                    hpFill.style.width = hp + '%';
                }
            }, 200);
        }
        
        // 模拟突破
        function simulateBreakthrough() {
            const progress = document.getElementById('realmProgressCircle');
            let current = 65;
            
            const breakInterval = setInterval(() => {
                current += Math.random() * 3;
                if (current >= 100) {
                    current = 0;
                    clearInterval(breakInterval);
                    alert('恭喜突破成功！进入下一境界！');
                }
                
                const offset = 327 - (327 * current / 100);
                progress.setAttribute('stroke-dashoffset', offset);
                GameData.player.realmProgress = current;
            }, 100);
        }
        
        // 更新资源显示
        function updateResourceDisplay() {
            document.getElementById('woodCount').textContent = GameData.resources.wood.toLocaleString();
            document.getElementById('spiritCount').textContent = GameData.resources.spirit.toLocaleString();
            document.getElementById('goldCount').textContent = GameData.resources.gold.toLocaleString();
        }
        
        // 挂机收益
        function idleGain() {
            GameData.resources.wood += Math.floor(Math.random() * 20 + 10);
            GameData.resources.spirit += Math.floor(Math.random() * 5 + 2);
            updateResourceDisplay();
        }
        
        // ==================== 初始化 ====================
        function init() {
            resizeCanvas();
            initParticles();
            gameLoop();
            
            // 渲染UI组件
            renderRealmList();
            renderEquippedSlots();
            renderBagGrid();
            initBagTabs();
            renderBeastList();
            selectBeast(1);
            
            // 启动挂机收益
            setInterval(idleGain, 3000);
            
            // 点击背景关闭弹窗
            document.getElementById('itemModal').addEventListener('click', function(e) {
                if (e.target === this) closeModal();
            });
        }
        
        window.addEventListener('resize', () => {
            resizeCanvas();
            initParticles();
        });
        
        window.addEventListener('load', init);
    </script>
</body>
</html>
```

## 设计思路说明

### 1. 国风视觉设计
- **边框组件**：使用CSS伪元素实现四角装饰的金色边框，营造古典卷轴感
- **水墨背景**：Canvas绘制分层山峦、云雾和粒子效果，呈现水墨画风格
- **配色方案**：以墨色为底，金色为主调，青色为辅助，红色点缀战斗元素

### 2. 水墨按钮设计
- 渐变背景模拟墨迹深浅
- 悬停时光晕扫过效果
- 三种风格：默认金色、主要操作青色、危险操作红色

### 3. 五个功能页面
- **主界面**：角色卡片、当前关卡信息、快捷功能入口
- **境界面板**：环形进度条、突破按钮、境界列表
- **装备背包**：已装备槽位、背包网格、品质筛选
- **灵兽图鉴**：展示区、星星评级、属性加成
- **设置页面**：音频开关、音量滑块、游戏设置

### 4. 交互特性
- 页面切换动画（淡入滑动）
- 底部Tab导航高亮指示
- 物品详情弹窗
- 开关/滑块控件
- 挂机资源自动增长