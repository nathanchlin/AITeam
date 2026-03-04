# AI对手决策系统

**Time**: 2026-02-28T16:47:51.211437

---

我来为你实现一个完整的AI对手决策系统，包含启发式评估、三档难度、战力差距评估、卡牌价值排序、Pass策略和特殊卡牌使用判断。

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
        
        .game-controls {
            position: absolute;
            top: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
            pointer-events: all;
            flex-wrap: wrap;
            max-width: 400px;
        }
        
        .control-btn {
            padding: 10px 20px;
            background: linear-gradient(180deg, #1a2520 0%, #0a1815 100%);
            border: 1px solid #356a55;
            color: #4ade80;
            font-family: 'Cinzel', serif;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .control-btn:hover {
            background: linear-gradient(180deg, #2a3530 0%, #1a2825 100%);
            border-color: #4ade80;
            box-shadow: 0 0 15px rgba(74, 222, 128, 0.3);
        }
        
        .control-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .control-btn.danger {
            background: linear-gradient(180deg, #2a1520 0%, #1a1015 100%);
            border-color: #6a3535;
            color: #de4a4a;
        }
        
        .control-btn.danger:hover {
            background: linear-gradient(180deg, #3a2530 0%, #2a1825 100%);
            border-color: #de4a4a;
            box-shadow: 0 0 15px rgba(222, 74, 74, 0.3);
        }
        
        .control-btn.leader {
            background: linear-gradient(180deg, #2a2515 0%, #1a180a 100%);
            border-color: #c9a227;
            color: #f0d060;
        }
        
        .control-btn.leader:hover {
            box-shadow: 0 0 20px rgba(201, 162, 39, 0.5);
        }
        
        .control-btn.leader.used {
            opacity: 0.4;
            cursor: not-allowed;
        }
        
        .ai-controls {
            position: absolute;
            top: 70px;
            left: 20px;
            display: flex;
            gap: 10px;
            pointer-events: all;
        }
        
        .difficulty-btn {
            padding: 8px 16px;
            background: linear-gradient(180deg, #201a25 0%, #151018 100%);
            border: 1px solid #4a3555;
            color: #a880c0;
            font-family: 'Cinzel', serif;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .difficulty-btn:hover {
            background: linear-gradient(180deg, #302a35 0%, #252028 100%);
            border-color: #a880c0;
        }
        
        .difficulty-btn.active {
            background: linear-gradient(180deg, #3a2540 0%, #2a1830 100%);
            border-color: #c080d0;
            color: #d0a0e0;
            box-shadow: 0 0 15px rgba(192, 128, 208, 0.3);
        }
        
        .game-info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            font-size: 12px;
            color: #6a5a45;
            pointer-events: all;
        }
        
        .game-log {
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 300px;
            max-height: 150px;
            overflow-y: auto;
            background: rgba(10, 10, 15, 0.9);
            border: 1px solid #2a2a35;
            padding: 10px;
            font-size: 11px;
            color: #8a8a95;
            pointer-events: all;
        }
        
        .game-log::-webkit-scrollbar {
            width: 6px;
        }
        
        .game-log::-webkit-scrollbar-track {
            background: #1a1a20;
        }
        
        .game-log::-webkit-scrollbar-thumb {
            background: #3a3a45;
            border-radius: 3px;
        }
        
        .log-entry {
            padding: 3px 0;
            border-bottom: 1px solid #1a1a20;
        }
        
        .log-entry.ai {
            color: #c080d0;
        }
        
        .log-entry.player {
            color: #4ade80;
        }
        
        .log-entry.system {
            color: #c9a227;
        }
        
        .ai-thinking {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(20, 15, 25, 0.95);
            border: 2px solid #6a4a80;
            padding: 20px 40px;
            border-radius: 8px;
            font-size: 16px;
            color: #c080d0;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 100;
        }
        
        .ai-thinking.visible {
            opacity: 1;
        }
        
        .ai-thinking::after {
            content: '';
            display: inline-block;
            width: 20px;
            text-align: left;
            animation: dots 1.5s infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <div id="uiOverlay">
            <div class="game-controls">
                <button class="control-btn" id="passBtn">放弃回合</button>
                <button class="control-btn leader" id="leaderBtn">领袖技能</button>
                <button class="control-btn danger" id="forfeitBtn">认输</button>
                <button class="control-btn" id="newGameBtn">新游戏</button>
            </div>
            <div class="ai-controls">
                <button class="difficulty-btn active" data-difficulty="EASY">简单</button>
                <button class="difficulty-btn" data-difficulty="NORMAL">普通</button>
                <button class="difficulty-btn" data-difficulty="HARD">困难</button>
            </div>
            <div class="weather-controls">
                <button class="weather-btn active" data-weather="clear">晴天</button>
                <button class="weather-btn" data-weather="frost">霜冻</button>
                <button class="weather-btn" data-weather="fog">迷雾</button>
                <button class="weather-btn" data-weather="rain">暴雨</button>
            </div>
            <div class="game-info">
                <p>鼠标悬停查看卡牌 | 点击选择卡牌 | 拖拽到战场放置 | 右键查看详情</p>
                <p id="turnIndicator" style="margin-top: 5px; color: #c9a227;"></p>
            </div>
            <div class="game-log" id="gameLog"></div>
            <div class="ai-thinking" id="aiThinking">AI思考中</div>
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
            ALLY_ZONE: '#151a20',
            PLAYER_POWER: '#4ade80',
            ENEMY_POWER: '#f87171',
            HIGHLIGHT_VALID: 'rgba(74, 222, 128, 0.3)',
            HIGHLIGHT_INVALID: 'rgba(248, 113, 113, 0.3)',
            CARD_SELECTED: '#4ade80',
            AI_COLOR: '#c080d0'
        },
        CARD_WIDTH: 70,
        CARD_HEIGHT: 100,
        HAND_FAN_ANGLE: 0.25,
        HAND_FAN_RADIUS: 100,
        HOVER_SCALE: 1.4,
        DRAG_ALPHA: 0.7,
        AI_THINK_TIME: 800
    };
    
    // ==================== 卡牌数据库 ====================
    const CardDatabase = {
        monsters: [
            { id: 'm001', name: '狂猎战士', power: 8, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'MELEE', abilities: [], desc: '狂猎军团的精锐战士' },
            { id: 'm002', name: '食尸鬼', power: 4, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'MELEE', abilities: ['MUSTER'], desc: '战场上的食腐者' },
            { id: 'm003', name: '鹰身女妖', power: 6, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'RANGED', abilities: [], desc: '从天空俯冲的凶猛掠食者' },
            { id: 'm004', name: '攻城巨魔', power: 10, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'SIEGE', abilities: [], desc: '体型巨大的巨魔' },
            { id: 'm005', name: '大狮鹫', power: 7, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'MELEE', abilities: [], desc: '极其危险的捕食者' },
            { id: 'm006', name: '古老树精', power: 5, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'RANGED', abilities: ['BOND'], desc: '森林的守护者' },
            { id: 'm007', name: '墓穴女巫', power: 3, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'SIEGE', abilities: ['MEDIC'], desc: '能够复活阵亡的单位' },
            { id: 'm008', name: '血魔', power: 12, faction: 'MONSTERS', color: 'GOLD', type: 'UNIT', row: 'MELEE', abilities: [], desc: '高等吸血鬼' },
            { id: 'm009', name: '瘟疫妖', power: 6, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'RANGED', abilities: [], desc: '携带致命瘟疫的妖物' },
            { id: 'm010', name: '霜冻巨像', power: 9, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'SIEGE', abilities: [], desc: '由寒冰构成的巨大魔像' },
            { id: 'm011', name: '吸血鬼间谍', power: 5, faction: 'MONSTERS', color: 'BRONZE', type: 'UNIT', row: 'MELEE', abilities: ['SPY'], desc: '潜伏在敌阵中收集情报' },
            { id: 'm012', name: '指挥号角', power: 0, faction: 'NEUTRAL', color: 'SPECIAL', type: 'SPECIAL', abilityType: 'COMMANDERS_HORN', desc: '使一排所有单位战力翻倍' },
            { id: 'm013', name: '灼烧', power: 0, faction: 'NEUTRAL', color: 'SPECIAL', type: 'SPECIAL', abilityType: 'SCORCH', desc: '摧毁场上所有最强单位' },
            { id: 'm014', name: '霜冻天气', power: 0, faction: 'NEUTRAL', color: 'WEATHER', type: 'WEATHER', abilityType: 'BITING_FROST', desc: '将所有近战排单位战力设为1' },
            { id: 'm015', name: '浓雾天气', power: 0, faction: 'NEUTRAL', color: 'WEATHER', type: 'WEATHER', abilityType: 'IMPENETRABLE_FOG', desc: '将所有远程排单位战力设为1' }
        ],
        
        northern: [
            { id: 'n001', name: '泰莫利亚士兵', power: 5, faction: 'NORTHERN', color: 'BRONZE', type: 'UNIT', row: 'MELEE', abilities: ['BOND'], desc: '精锐步兵' },
            { id: 'n002', name: '蓝衣铁卫', power: 6, faction: 'NORTHERN', color: 'BRONZE', type: 'UNIT', row: 'MELEE', abilities: [], desc: '特种作战部队' },
            { id: 'n003', name: '攻城技师', power: 4, faction: 'NORTHERN', color: 'BRONZE', type: 'UNIT', row: 'SIEGE', abilities: ['MORALE_BOOST'], desc: '为攻城单位提供支援' },
            { id: 'n004', name: '弗农·罗奇', power: 8, faction: 'NORTHERN', color: 'GOLD', type: 'UNIT', row: 'MELEE', abilities: [], desc: '蓝衣铁卫的指挥官' },
            { id: 'n005', name: '草药医', power: 3, faction: 'NORTHERN', color: 'BRONZE', type: 'UNIT', row: 'RANGED', abilities: ['MEDIC'], desc: '能够复活单位' },
            { id: 'n006', name: '斥候', power: 5, faction: 'NORTHERN', color: 'BRONZE', type: 'UNIT', row: 'RANGED', abilities: ['SPY'], desc: '深入敌后收集情报' },
            { id: 'n007', name: '投石机', power: 7, faction: 'NORTHERN', color: 'BRONZE', type: 'UNIT', row: 'SIEGE', abilities: [], desc: '威力强大的攻城武器' },
            { id: 'n008', name: '凯拉·梅兹', power: 6, faction: 'NORTHERN', color: 'GOLD', type: 'UNIT', row: 'RANGED', abilities: [], desc: '强大的女术士' }
        ],
        
        leaders: [
            { id: 'l001', name: '艾瑞汀', faction: 'MONSTERS', ability: '回合结束时保留场上最强单位', charges: 1 },
            { id: 'l002', name: '恩希尔·恩瑞斯', faction: 'NILFGAARD', ability: '查看对手一张手牌', charges: 1 },
            { id: 'l003', name: '弗尔泰斯特', faction: 'NORTHERN', ability: '摧毁一张攻城单位的护甲', charges: 1 }
        ]
    };
    
    // ==================== AI决策系统 ====================
    class AIDecisionSystem {
        constructor(difficulty = 'NORMAL') {
            this.difficulty = difficulty;
            this.config = this.getDifficultyConfig(difficulty);
            this.decisionHistory = [];
            this.lastPowerGap = 0;
        }
        
        getDifficultyConfig(difficulty) {
            const configs = {
                EASY: {
                    randomFactor: 0.4,
                    lookAheadRounds: 0,
                    passThreshold: -20,
                    passLeadThreshold: 25,
                    scorchThreshold: 3,
                    mistakeChance: 0.35,
                    cardAdvantageWeight: 0.3,
                    spyValue: 5,
                    thinkTime: 600
                },
                NORMAL: {
                    randomFactor: 0.2,
                    lookAheadRounds: 1,
                    passThreshold: -12,
                    passLeadThreshold: 18,
                    scorchThreshold: 2,
                    mistakeChance: 0.15,
                    cardAdvantageWeight: 0.6,
                    spyValue: 12,
                    thinkTime: 1000
                },
                HARD: {
                    randomFactor: 0.05,
                    lookAheadRounds: 2,
                    passThreshold: -6,
                    passLeadThreshold: 12,
                    scorchThreshold: 1,
                    mistakeChance: 0.02,
                    cardAdvantageWeight: 1.0,
                    spyValue: 18,
                    thinkTime: 1500
                }
            };
            return configs[difficulty] || configs.NORMAL;
        }
        
        setDifficulty(difficulty) {
            this.difficulty = difficulty;
            this.config = this.getDifficultyConfig(difficulty);
        }
        
        // 主决策函数
        makeDecision(gameState) {
            const { aiHand, aiBoard, playerBoard, round, playerPassed, aiPassed,
                    aiRoundWins, playerRoundWins, weather, aiGrave, playerGrave } = gameState;
            
            const aiPower = this.calculateTotalPower(aiBoard, weather);
            const playerPower = this.calculateTotalPower(playerBoard, weather);
            const powerGap = aiPower - playerPower;
            const cardAdvantage = aiHand.length - gameState.playerHand.length;
            
            // 记录决策上下文
            const context = {
                round,
                aiPower,
                playerPower,
                powerGap,
                cardAdvantage,
                aiCards: aiHand.length,
                playerCards: gameState.playerHand.length,
                playerPassed
            };
            
            // 1. 检查是否应该pass
            const passDecision = this.evaluatePassDecision(context, gameState);
            if (passDecision.shouldPass) {
                this.logDecision('PASS', passDecision.reason, context);
                return { action: 'PASS', reason: passDecision.reason };
            }
            
            // 2. 评估手中所有卡牌
            const cardEvaluations = this.evaluateAllCards(aiHand, gameState, context);
            
            // 3. 选择最佳卡牌
            const selectedCard = this.selectBestCard(cardEvaluations, context);
            
            // 4. 确定打出位置
            const playDecision = this.determinePlayLocation(selectedCard, gameState, context);
            
            // 记录决策
            this.logDecision('PLAY', `打出 ${selectedCard.card.name}`, context);
            
            return playDecision;
        }
        
        // Pass决策评估
        evaluatePassDecision(context, gameState) {
            const { round, aiPower, playerPower, powerGap, cardAdvantage, 
                    aiCards, playerCards, playerPassed } = context;
            const { aiRoundWins, playerRoundWins } = gameState;
            
            // 已经pass了不能再pass
            if (gameState.aiPassed) {
                return { shouldPass: false };
            }
            
            // 对手已经pass - 分析是否应该继续打
            if (playerPassed) {
                // 领先就pass
                if (powerGap > 0) {
                    return { shouldPass: true, reason: '领先状态下对手已pass' };
                }
                // 落后但还有牌可打，继续
                if (aiCards > 0 && powerGap >= -30) {
                    return { shouldPass: false };
                }
                // 差距太大，放弃保卡
                return { shouldPass: true, reason: '落后太多，保卡' };
            }
            
            // === 回合特定策略 ===
            
            // 第一回合策略
            if (round === 1) {
                // 大幅领先 + 卡差优势 -> pass换取卡差
                if (powerGap > this.config.passLeadThreshold && cardAdvantage >= 0) {
                    if (Math.random() > this.config.randomFactor) {
                        return { shouldPass: true, reason: `R1领先${powerGap}点，保卡差优势` };
                    }
                }
                
                // 落后太多且卡差不利 -> 放弃保卡
                if (powerGap < this.config.passThreshold && cardAdvantage <= 0) {
                    return { shouldPass: true, reason: `R1落后${-powerGap}点，放弃保卡` };
                }
                
                // 手牌很少且落后 -> 可能需要搏一搏
                if (aiCards <= 2 && powerGap < -10) {
                    // 困难模式会更聪明地判断
                    if (this.difficulty === 'HARD' && this.hasHighValueCards(gameState.aiHand)) {
                        return { shouldPass: false };
                    }
                    return { shouldPass: true, reason: '手牌不足且落后，保卡打后手' };
                }
            }
            
            // 第二回合策略
            if (round === 2) {
                // 赢了第一回合，现在领先 -> 直接pass赢比赛
                if (aiRoundWins === 1 && playerRoundWins === 0) {
                    if (powerGap > 5) {
                        return { shouldPass: true, reason: '赛点领先，直接获胜' };
                    }
                }
                
                // 输了第一回合，必须赢这回合
                if (aiRoundWins === 0 && playerRoundWins === 1) {
                    // 领先且对手可能要追
                    if (powerGap > 15 && playerCards <= aiCards) {
                        return { shouldPass: true, reason: '必须赢的回合，已建立优势' };
                    }
                    // 继续打
                    return { shouldPass: false };
                }
                
                // 平局状态
                if (aiRoundWins === 0 && playerRoundWins === 0) {
                    // 领先较多可以pass
                    if (powerGap > 20 && cardAdvantage >= 0) {
                        return { shouldPass: true, reason: 'R2建立大优势，保卡差' };
                    }
                }
            }
            
            // 第三回合 - 打到底
            if (round === 3) {
                return { shouldPass: false };
            }
            
            // 综合评估：卡差策略
            const cardAdvantageScore = this.evaluateCardAdvantage(context);
            if (cardAdvantageScore.shouldPass) {
                return { shouldPass: true, reason: cardAdvantageScore.reason };
            }
            
            return { shouldPass: false };
        }
        
        // 卡差策略评估
        evaluateCardAdvantage(context) {
            const { round, cardAdvantage, aiCards, playerCards, powerGap } = context;
            
            // 困难模式更注重卡差
            if (this.difficulty === 'HARD') {
                // 如果我们有卡差优势且领先，可以考虑pass
                if (cardAdvantage > 0 && powerGap > 8) {
                    return { shouldPass: true, reason: '卡差优势+领先，巩固优势' };
                }
                
                // 如果我们卡差劣势且落后不多，可能要继续打
                if (cardAdvantage < 0 && powerGap > -15) {
                    return { shouldPass: false };
                }
            }
            
            return { shouldPass: false };
        }
        
        // 评估所有手牌
        evaluateAllCards(hand, gameState, context) {
            return hand.map(card => ({
                card: card,
                score: this.evaluateCard(card, gameState, context),
                preferredRow: this.getPreferredRow(card, gameState),
                priority: this.getCardPriority(card, context)
            })).sort((a, b) => {
                // 先按优先级，再按分数
                if (a.priority !== b.priority) return b.priority - a.priority;
                return b.score - a.score;
            });
        }
        
        // 单卡价值评估
        evaluateCard(card, gameState, context) {
            let score = 0;
            const { weather, aiBoard, playerBoard, round } = gameState;
            const { powerGap, cardAdvantage } = context;
            
            // === 单位卡评估 ===
            if (card.type === 'UNIT') {
                // 基础战力
                score = card.power;
                
                // 天气影响调整
                const weatherPenalty = this.getWeatherPenalty(card, weather);
                if (weatherPenalty) {
                    score = Math.min(score, 2); // 天气下战力极低
                }
                
                // 颜色加成
                if (card.color === 'GOLD') {
                    score *= 1.2; // 金卡更有价值
                }
                
                // 能力评估
                if (card.abilities && card.abilities.length > 0) {
                    card.abilities.forEach(ability => {
                        score += this.evaluateAbility(ability, gameState, card, context);
                    });
                }
                
                // 间谍卡特殊处理
                if (card.abilities && card.abilities.includes('SPY')) {
                    // 落后时不打间谍
                    if (powerGap < 0) {
                        score = -50;
                    } else {
                        // 领先时间谍价值很高
                        score = this.config.spyValue + cardAdvantage * 3;
                        // 手牌少时更珍贵
                        if (context.aiCards <= 3) {
                            score += 10;
                        }
                    }
                }
            }
            
            // === 特殊卡评估 ===
            if (card.type === 'SPECIAL') {
                score = this.evaluateSpecialCard(card, gameState, context);
            }
            
            // === 天气卡评估 ===
            if (card.type === 'WEATHER') {
                score = this.evaluateWeatherCard(card, gameState, context);
            }
            
            // 添加随机性（根据难度）
            if (Math.random() < this.config.randomFactor) {
                score *= (0.6 + Math.random() * 0.8);
            }
            
            return Math.max(0, score);
        }
        
        // 能力价值评估
        evaluateAbility(ability, gameState, card, context) {
            const { aiBoard, aiGrave, playerBoard } = gameState;
            
            switch (ability) {
                case 'BOND':
                    const sameCards = this.countCardsWithId(aiBoard, card.id);
                    if (sameCards > 0) {
                        return sameCards * card.power * 0.8; // 配合收益
                    }
                    return 3; // 潜在配合
                
                case 'MEDIC':
                    const reviveTargets = aiGrave ? aiGrave.filter(c => c.type === 'UNIT') : [];
                    if (reviveTargets.length > 0) {
                        const bestTarget = Math.max(...reviveTargets.map(c => c.power));
                        return Math.min(bestTarget * 0.7, 10);
                    }
                    return 0;
                
                case 'MORALE_BOOST':
                    const rowUnits = this.countRowUnits(aiBoard, card.row);
                    return rowUnits * 2;
                
                case 'MUSTER':
                    return 8; // 召唤价值
                
                default:
                    return 0;
            }
        }
        
        // 特殊卡评估
        evaluateSpecialCard(card, gameState, context) {
            const { aiBoard, playerBoard, weather } = gameState;
            const { powerGap } = context;
            
            // 指挥号角
            if (card.abilityType === 'COMMANDERS_HORN') {
                let maxBoost = 0;
                ['MELEE', 'RANGED', 'SIEGE'].forEach(row => {
                    const rowPower = this.getRowPower(aiBoard, row, weather);
                    if (rowPower > maxBoost) {
                        maxBoost = rowPower;
                    }
                });
                return maxBoost; // 翻倍收益
            }
            
            // 灼烧
            if (card.abilityType === 'SCORCH') {
                return this.evaluateScorch(playerBoard, aiBoard);
            }
            
            return 5;
        }
        
        // 灼烧评估
        evaluateScorch(playerBoard, aiBoard) {
            const playerUnits = playerBoard.filter(c => c.type === 'UNIT');
            const aiUnits = aiBoard.filter(c => c.type === 'UNIT');
            
            if (playerUnits.length === 0) return -10; // 没目标
            
            const maxPower = Math.max(...playerUnits.map(c => c.currentPower || c.power));
            const playerMaxUnits = playerUnits.filter(c => (c.currentPower || c.power) === maxPower);
            const aiMaxUnits = aiUnits.filter(c => (c.currentPower || c.power) === maxPower);
            
            // 会烧到自己
            if (aiMaxUnits.length > 0) {
                if (aiMaxUnits.length >= playerMaxUnits.length) {
                    return -30; // 亏了
                }
            }
            
            // 消灭阈值
            if (playerMaxUnits.length >= this.config.scorchThreshold) {
                return 20 + playerMaxUnits.length * maxPower * 0.5;
            }
            
            return 5;
        }
        
        // 天气卡评估
        evaluateWeatherCard(card, gameState, context) {
            const { playerBoard, aiBoard, weather } = gameState;
            
            // 已经有天气了
            if (weather && weather !== 'clear') {
                return -5;
            }
            
            if (card.abilityType === 'BITING_FROST') {
                const playerMelee = this.getRowPower(playerBoard, 'MELEE', 'clear');
                const aiMelee = this.getRowPower(aiBoard, 'MELEE', 'clear');
                
                if (playerMelee > aiMelee + 8) {
                    return playerMelee - aiMelee;
                }
            }
            
            if (card.abilityType === 'IMPENETRABLE_FOG') {
                const playerRanged = this.getRowPower(playerBoard, 'RANGED', 'clear');
                const aiRanged = this.getRowPower(aiBoard, 'RANGED', 'clear');
                
                if (playerRanged > aiRanged + 8) {
                    return playerRanged - aiRanged;
                }
            }
            
            return -2;
        }
        
        // 获取卡牌优先级
        getCardPriority(card, context) {
            // 间谍卡在特定情况下高优先级
            if (card.abilities && card.abilities.includes('SPY')) {
                if (context.powerGap > 10 && context.aiCards <= 4) {
                    return 10; // 高优先级
                }
            }
            
            // 灼烧在对手有高价值目标时高优先级
            if (card.abilityType === 'SCORCH') {
                return 5;
            }
            
            // 金卡中等优先级
            if (card.color === 'GOLD') {
                return 3;
            }
            
            return 1;
        }
        
        // 选择最佳卡牌
        selectBestCard(evaluations, context) {
            // 过滤负分卡
            const validCards = evaluations.filter(e => e.score > 0);
            
            if (validCards.length === 0) {
                // 没有好选择，选分数最高的
                return evaluations[0];
            }
            
            // 犯错几率
            if (Math.random() < this.config.mistakeChance) {
                const randomIndex = Math.floor(Math.random() * Math.min(3, validCards.length));
                return validCards[randomIndex];
            }
            
            return validCards[0];
        }
        
        // 确定打出位置
        determinePlayLocation(selectedCard, gameState, context) {
            const card = selectedCard.card;
            
            // 天气卡和特殊卡
            if (card.type === 'WEATHER' || card.type === 'SPECIAL') {
                return {
                    action: 'PLAY',
                    card: card,
                    row: 'WEATHER',
                    confidence: selectedCard.score
                };
            }
            
            // 间谍卡打对面
            if (card.abilities && card.abilities.includes('SPY')) {
                return {
                    action: 'PLAY',
                    card: card,
                    row: card.row || 'MELEE',
                    isSpy: true,
                    confidence: selectedCard.score
                };
            }
            
            // 单位卡
            return {
                action: 'PLAY',
                card: card,
                row: selectedCard.preferredRow,
                confidence: selectedCard.score
            };
        }
        
        // 辅助函数
        getPreferredRow(card, gameState) {
            if (card.row) return card.row;
            
            // 选择总战力最低的排
            const rows = ['MELEE', 'RANGED', 'SIEGE'];
            let minRow = 'MELEE';
            let minPower = Infinity;
            
            rows.forEach(row => {
                const power = this.getRowPower(gameState.aiBoard, row, gameState.weather);
                if (power < minPower) {
                    minPower = power;
                    minRow = row;
                }
            });
            
            return minRow;
        }
        
        calculateTotalPower(board, weather) {
            if (!board || board.length === 0) return 0;
            return board.reduce((sum, card) => {
                if (card.type !== 'UNIT') return sum;
                let power = card.currentPower || card.power;
                
                // 天气影响
                if (weather === 'frost' && card.row === 'MELEE') power = 1;
                if (weather === 'fog' && card.row === 'RANGED') power = 1;
                if (weather === 'rain' && card.row === 'SIEGE') power = 1;
                
                return sum + power;
            }, 0);
        }
        
        getRowPower(board, row, weather) {
            if (!board) return 0;
            return board.filter(c => c.row === row && c.type === 'UNIT')
                       .reduce((sum, c) => {
                           let power = c.currentPower || c.power;
                           if (weather === 'frost' && row === 'MELEE') power = 1;
                           if (weather === 'fog' && row === 'RANGED') power = 1;
                           if (weather === 'rain' && row === 'SIEGE') power = 1;
                           return sum + power;
                       }, 0);
        }
        
        getWeatherPenalty(card, weather) {
            if (card.type !== 'UNIT') return false;
            if (weather === 'frost' && card.row === 'MELEE') return true;
            if (weather === 'fog' && card.row === 'RANGED') return true;
            if (weather === 'rain' && card.row === 'SIEGE') return true;
            return false;
        }
        
        countCardsWithId(board, id) {
            if (!board) return 0;
            return board.filter(c => c.id === id).length;
        }
        
        countRowUnits(board, row) {
            if (!board) return 0;
            return board.filter(c => c.row === row && c.type === 'UNIT').length;
        }
        
        hasHighValueCards(hand) {
            if (!hand) return false;
            return hand.some(c => c.power >= 8 || (c.color === 'GOLD'));
        }
        
        logDecision(action, reason, context) {
            this.decisionHistory.push({
                action,
                reason,
                context: { ...context },
                timestamp: Date.now()
            });
            
            // 控制历史长度
            if (this.decisionHistory.length > 50) {
                this.decisionHistory.shift();
            }
        }
        
        getLastDecision() {
            return this.decisionHistory[this.decisionHistory.length - 1];
        }
    }
    
    // ==================== 动画系统 ====================
    class AnimationManager {
        constructor() {
            this.animations = [];
            this.powerPopups = [];
            this.shockwaves = [];
            this.cameraShake = { x: 0, y: 0, intensity: 0 };
        }
        
        playCardFly(card, startX, startY, endX, endY, isGold = false, callback) {
            const animation = {
                type: 'cardFly',
                card: card,
                startX, startY, endX, endY,
                x: startX, y: startY,
                progress: 0,
                duration: 500,
                startTime: Date.now(),
                isGold,
                callback,
                trailPoints: []
            };
            this.animations.push(animation);
            
            if (isGold) {
                this.cameraShake.intensity = 6;
                this.addShockwave(endX, endY, '#c9a227', 100);
            }
        }
        
        addPowerPopup(x, y, value, isPositive = true) {
            this.powerPopups.push({
                x, y, value, isPositive,
                alpha: 1,
                offsetY: 0,
                velocityY: -2,
                startTime: Date.now(),
                duration: 1200
            });
        }
        
        addShockwave(x, y, color = '#c9a227', maxRadius = 100) {
            this.shockwaves.push({
                x, y, color,
                radius: 0,
                maxRadius,
                alpha: 1,
                speed: 5
            });
        }
        
        update() {
            const now = Date.now();
            
            // 更新飞行动画
            this.animations = this.animations.filter(anim => {
                if (anim.type === 'cardFly') {
                    const elapsed = now - anim.startTime;
                    anim.progress = Math.min(elapsed / anim.duration, 1);
                    
                    const ease = 1 - Math.pow(1 - anim.progress, 3);
                    anim.x = anim.startX + (anim.endX - anim.startX) * ease;
                    anim.y = anim.startY + (anim.endY - anim.startY) * ease;
                    
                    // 添加拖尾
                    if (anim.progress < 1) {
                        anim.trailPoints.push({ x: anim.x, y: anim.y, alpha: 1 });
                    }
                    anim.trailPoints = anim.trailPoints.filter(p => {
                        p.alpha *= 0.9;
                        return p.alpha > 0.05;
                    });
                    
                    if (anim.progress >= 1 && anim.callback) {
                        anim.callback();
                    }
                    
                    return anim.progress < 1;
                }
                return false;
            });
            
            // 更新战力弹窗
            this.powerPopups = this.powerPopups.filter(p => {
                const elapsed = now - p.startTime;
                const progress = elapsed / p.duration;
                p.alpha = 1 - progress;
                p.offsetY += p.velocityY;
                p.velocityY *= 0.95;
                return progress < 1;
            });
            
            // 更新冲击波
            this.shockwaves = this.shockwaves.filter(s => {
                s.radius += s.speed;
                s.alpha = 1 - (s.radius / s.maxRadius);
                return s.radius < s.maxRadius;
            });
            
            // 更新相机震动
            if (this.cameraShake.intensity > 0) {
                this.cameraShake.x = (Math.random() - 0.5) * this.cameraShake.intensity;
                this.cameraShake.y = (Math.random() - 0.5) * this.cameraShake.intensity;
                this.cameraShake.intensity *= 0.9;
                if (this.cameraShake.intensity < 0.5) {
                    this.cameraShake.intensity = 0;
                    this.cameraShake.x = 0;
                    this.cameraShake.y = 0;
                }
            }
        }
        
        render(ctx) {
            // 渲染冲击波
            this.shockwaves.forEach(s => {
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
                ctx.strokeStyle = s.color;
                ctx.globalAlpha = s.alpha;
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.globalAlpha = 1;
            });
            
            // 渲染飞行卡牌和拖尾
            this.animations.forEach(anim => {
                if (anim.type === 'cardFly') {
                    // 拖尾
                    anim.trailPoints.forEach((p, i) => {
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, 4 * (i / anim.trailPoints.length), 0, Math.PI * 2);
                        ctx.fillStyle = anim.isGold ? 
                            `rgba(201, 162, 39, ${p.alpha * 0.6})` : 
                            `rgba(100, 120, 200, ${p.alpha * 0.4})`;
                        ctx.fill();
                    });
                    
                    // 卡牌
                    if (anim.card) {
                        this.renderFlyingCard(ctx, anim);
                    }
                }
            });
            
            // 渲染战力弹窗
            this.powerPopups.forEach(p => {
                ctx.font = 'bold 24px Cinzel';
                ctx.textAlign = 'center';
                ctx.fillStyle = p.isPositive ? '#4ade80' : '#f87171';
                ctx.globalAlpha = p.alpha;
                ctx.fillText((p.isPositive ? '+' : '') + p.value, p.x, p.y + p.offsetY);
                ctx.globalAlpha = 1;
            });
        }
        
        renderFlyingCard(ctx, anim) {
            const card = anim.card;
            const w = CONFIG.CARD_WIDTH;
            const h = CONFIG.CARD_HEIGHT;
            
            ctx.save();
            ctx.translate(anim.x, anim.y);
            
            // 卡牌背景
            let bgColor = '#2a2520';
            let borderColor = '#5a4a35';
            
            if (card.color === 'GOLD') {
                bgColor = '#3a3020';
                borderColor = '#c9a227';
            } else if (card.color === 'SPECIAL') {
                bgColor = '#202a30';
                borderColor = '#4a80a0';
            }
            
            // 发光效果
            if (anim.isGold) {
                ctx.shadowColor = '#c9a227';
                ctx.shadowBlur = 20;
            }
            
            // 卡牌框架
            ctx.fillStyle = bgColor;
            ctx.fillRect(-w/2, -h/2, w, h);
            ctx.strokeStyle = borderColor;
            ctx.lineWidth = 2;
            ctx.strokeRect(-w/2, -h/2, w, h);
            
            ctx.shadowBlur = 0;
            
            // 卡牌名称
            ctx.fillStyle = '#d4c4a8';
            ctx.font = '10px Cinzel';
            ctx.textAlign = 'center';
            ctx.fillText(card.name, 0, -h/2 + 20);
            
            // 战力
            if (card.type === 'UNIT') {
                ctx.fillStyle = card.color === 'GOLD' ? '#f0d060' : '#a0a0a0';
                ctx.font = 'bold 18px Cinzel';
                ctx.fillText(card.power, 0, h/2 - 15);
            }
            
            ctx.restore();
        }
    }
    
    // ==================== 游戏状态管理 ====================
    class GameState {
        constructor() {
            this.reset();
        }
        
        reset() {
            this.round = 1;
            this.playerRoundWins = 0;
            this.aiRoundWins = 0;
            this.playerPassed = false;
            this.aiPassed = false;
            this.isPlayerTurn = true;
            this.gamePhase = 'PLAYING';
            this.weather = 'clear';
            
            // 初始化牌组
            this.playerDeck = this.createDeck('northern');
            this.aiDeck = this.createDeck('monsters');
            
            // 洗牌
            this.shuffle(this.playerDeck);
            this.shuffle(this.aiDeck);
            
            // 抽初始手牌
            this.playerHand = this.playerDeck.splice(0, 10);
            this.aiHand = this.aiDeck.splice(0, 10);
            
            // 战场
            this.playerBoard = [];
            this.aiBoard = [];
            
            // 墓地
            this.playerGrave = [];
            this.aiGrave = [];
            
            // 领袖
            this.playerLeaderUsed = false;
            this.aiLeaderUsed = false;
        }
        
        createDeck(faction) {
            const cards = [];
            const factionCards = faction === 'northern' ? CardDatabase.northern : CardDatabase.monsters;
            
            // 每种卡牌加入1-3张
            factionCards.forEach(card => {
                const count = card.color === 'GOLD' ? 1 : (Math.floor(Math.random() * 2) + 1);
                for (let i = 0; i < count; i++) {
                    cards.push({ ...card, currentPower: card.power });
                }
            });
            
            return cards;
        }
        
        shuffle(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
        }
        
        getPlayerPower() {
            return this.calculatePower(this.playerBoard);
        }
        
        getAIPower() {
            return this.calculatePower(this.aiBoard);
        }
        
        calculatePower(board) {
            return board.reduce((sum, card) => {
                if (card.type !== 'UNIT') return sum;
                let power = card.currentPower || card.power;
                
                if (this.weather === 'frost' && card.row === 'MELEE') power = 1;
                if (this.weather === 'fog' && card.row === 'RANGED') power = 1;
                if (this.weather === 'rain' && card.row === 'SIEGE') power = 1;
                
                return sum + power;
            }, 0);
        }
        
        startNewRound() {
            this.round++;
            this.playerPassed = false;
            this.aiPassed = false;
            
            // 将战场卡牌移入墓地
            this.playerGrave.push(...this.playerBoard);
            this.aiGrave.push(...this.aiBoard);
            
            this.playerBoard = [];
            this.aiBoard = [];
            this.weather = 'clear';
            
            // 抽2张牌
            for (let i = 0; i < 2; i++) {
                if (this.playerDeck.length > 0) {
                    this.playerHand.push(this.playerDeck.pop());
                }
                if (this.aiDeck.length > 0) {
                    this.aiHand.push(this.aiDeck.pop());
                }
            }
        }
    }
    
    // ==================== 渲染器 ====================
    class GameRenderer {
        constructor(canvas, ctx) {
            this.canvas = canvas;
            this.ctx = ctx;
            this.hoveredCard = null;
            this.selectedCard = null;
            this.hoveredZone = null;
        }
        
        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
        
        render(gameState, animationManager) {
            const ctx = this.ctx;
            const w = this.canvas.width;
            const h = this.canvas.height;
            
            // 应用相机震动
            ctx.save();
            ctx.translate(animationManager.cameraShake.x, animationManager.cameraShake.y);
            
            // 背景
            this.renderBackground(ctx, w, h);
            
            // 战场区域
            this.renderBattlefield(ctx, w, h, gameState);
            
            // 手牌
            this.renderHands(ctx, w, h, gameState);
            
            // 战力显示
            this.renderPowerDisplay(ctx, w, h, gameState);
            
            // 回合信息
            this.renderRoundInfo(ctx, w, h, gameState);
            
            // 动画
            animationManager.render(ctx);
            
            // 高亮
            this.renderHighlights(ctx, w, h, gameState);
            
            ctx.restore();
        }
        
        renderBackground(ctx, w, h) {
            // 渐变背景
            const gradient = ctx.createLinearGradient(0, 0, 0, h);
            gradient.addColorStop(0, '#0d0d15');
            gradient.addColorStop(0.5, '#12121a');
            gradient.addColorStop(1, '#0d0d12');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, w, h);
            
            // 装饰线条
            ctx.strokeStyle = 'rgba(201, 162, 39, 0.1)';
            ctx.lineWidth = 1;
            
            for (let i = 0; i < 20; i++) {
                const y = (h / 20) * i;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }
        }
        
        renderBattlefield(ctx, w, h, gameState) {
            const centerX = w / 2;
            const centerY = h / 2;
            const rowWidth = 500;
            const rowHeight = 80;
            const rowGap = 20;
            
            const rows = [
                { name: 'SIEGE', y: centerY - rowHeight - rowGap - rowHeight - rowGap, label: '攻城' },
                { name: 'RANGED', y: centerY - rowHeight - rowGap, label: '远程' },
                { name: 'MELEE', y: centerY, label: '近战' },
                { name: 'ENEMY_MELEE', y: centerY + rowGap + rowHeight, label: '敌方近战' },
                { name: 'ENEMY_RANGED', y: centerY + (rowGap + rowHeight) * 2, label: '敌方远程' },
                { name: 'ENEMY_SIEGE', y: centerY + (rowGap + rowHeight) * 3, label: '敌方攻城' }
            ];
            
            rows.forEach(row => {
                const isEnemy = row.name.startsWith('ENEMY_');
                const board = isEnemy ? gameState.aiBoard : gameState.playerBoard;
                const rowType = isEnemy ? row.name.replace('ENEMY_', '') : row.name;
                const cards = board.filter(c => c.row === rowType);
                
                // 行背景
                ctx.fillStyle = isEnemy ? 'rgba(40, 20, 30, 0.5)' : 'rgba(20, 40, 30, 0.5)';
                ctx.fillRect(centerX - rowWidth/2, row.y, rowWidth, rowHeight);
                
                // 边框
                ctx.strokeStyle = isEnemy ? 'rgba(200, 100, 100, 0.3)' : 'rgba(100, 200, 100, 0.3)';
                ctx.lineWidth = 1;
                ctx.strokeRect(centerX - rowWidth/2, row.y, rowWidth, rowHeight);
                
                // 行标签
                ctx.fillStyle = '#6a5a45';
                ctx.font = '12px Cinzel';
                ctx.textAlign = 'left';
                ctx.fillText(row.label, centerX - rowWidth/2 + 5, row.y + 15);
                
                // 行战力
                const rowPower = this.calculateRowPower(cards, gameState.weather, rowType);
                ctx.textAlign = 'right';
                ctx.fillStyle = isEnemy ? '#f87171' : '#4ade80';
                ctx.font = 'bold 16px Cinzel';
                ctx.fillText(rowPower, centerX + rowWidth/2 - 10, row.y + rowHeight - 10);
                
                // 渲染卡牌
                this.renderRowCards(ctx, cards, centerX, row.y, rowWidth, rowHeight, isEnemy);
            });
        }
        
        renderRowCards(ctx, cards, centerX, y, rowWidth, rowHeight, isEnemy) {
            const cardW = 50;
            const cardH = 70;
            const gap = 5;
            const totalWidth = cards.length * (cardW + gap) - gap;
            const startX = centerX - totalWidth / 2;
            
            cards.forEach((card, i) => {
                const x = startX + i * (cardW + gap);
                const cy = y + (rowHeight - cardH) / 2;
                
                this.renderCard(ctx, card, x, cy, cardW, cardH, false, isEnemy);
            });
        }
        
        renderCard(ctx, card, x, y, w, h, isHovered = false, isEnemy = false) {
            ctx.save();
            
            // 颜色配置
            let bgColor = '#1a1a20';
            let borderColor = '#4a4a55';
            let powerColor = '#a0a0a0';
            
            if (card.color === 'GOLD') {
                bgColor = '#2a2515';
                borderColor = '#c9a227';
                powerColor = '#f0d060';
            } else if (card.color === 'SPECIAL') {
                bgColor = '#151a25';
                borderColor = '#4a80a0';
                powerColor = '#80c0e0';
            } else if (card.color === 'WEATHER') {
                bgColor = '#1a1525';
                borderColor = '#8060a0';
                powerColor = '#a080c0';
            }
            
            // 悬停效果
            if (isHovered) {
                ctx.shadowColor = borderColor;
                ctx.shadowBlur = 15;
            }
            
            // 敌方卡牌暗化
            if (isEnemy && !isHovered) {
                ctx.globalAlpha = 0.85;
            }
            
            // 卡牌背景
            ctx.fillStyle = bgColor;
            ctx.fillRect(x, y, w, h);
            
            // 边框
            ctx.strokeStyle = borderColor;
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, w, h);
            
            ctx.shadowBlur = 0;
            ctx.globalAlpha = 1;
            
            // 名称
            ctx.fillStyle = '#d4c4a8';
            ctx.font = `${Math.min(9, w / 6)}px Cinzel`;
            ctx.textAlign = 'center';
            ctx.fillText(this.truncateText(ctx, card.name, w - 8), x + w/2, y + 16);
            
            // 战力
            if (card.type === 'UNIT') {
                ctx.fillStyle = powerColor;
                ctx.font = `bold ${Math.min(20, h / 4)}px Cinzel`;
                ctx.fillText(card.currentPower || card.power, x + w/2, y + h - 12);
            }
            
            // 能力图标
            if (card.abilities && card.abilities.length > 0) {
                ctx.fillStyle = '#80a0c0';
                ctx.font = '8px Arial';
                ctx.fillText(card.abilities[0].charAt(0), x + w - 10, y + h - 5);
            }
            
            ctx.restore();
        }
        
        renderHands(ctx, w, h, gameState) {
            const cardW = 60;
            const cardH = 85;
            const gap = 8;
            
            // 玩家手牌
            const playerHandWidth = gameState.playerHand.length * (cardW + gap) - gap;
            let startX = w / 2 - playerHandWidth / 2;
            const playerY = h - cardH - 30;
            
            gameState.playerHand.forEach((card, i) => {
                const x = startX + i * (cardW + gap);
                const isHovered = this.hoveredCard === card;
                const isSelected = this.selectedCard === card;
                
                let offsetY = 0;
                if (isHovered) offsetY = -15;
                if (isSelected) offsetY = -25;
                
                this.renderCard(ctx, card, x, playerY + offsetY, cardW, cardH, isHovered || isSelected, false);
                
                // 存储卡牌位置用于点击检测
                card._renderX = x;
                card._renderY = playerY + offsetY;
                card._renderW = cardW;
                card._renderH = cardH;
            });
            
            // AI手牌（背面）
            const aiHandWidth = gameState.aiHand.length * (cardW + gap) - gap;
            startX = w / 2 - aiHandWidth / 2;
            const aiY = 30;
            
            for (let i = 0; i < gameState.aiHand.length; i++) {
                const x = startX + i * (cardW + gap);
                
                ctx.fillStyle = '#1a1a20';
                ctx.fillRect(x, aiY, cardW, cardH);
                ctx.strokeStyle = '#3a3a45';
                ctx.lineWidth = 2;
                ctx.strokeRect(x, aiY, cardW, cardH);
                
                // 背面图案
                ctx.fillStyle = '#c9a227';
                ctx.font = '24px Cinzel';
                ctx.textAlign = 'center';
                ctx.fillText('?', x + cardW/2, aiY + cardH/2 + 8);
            }
        }
        
        renderPowerDisplay(ctx, w, h, gameState) {
            const playerPower = gameState.getPlayerPower();
            const aiPower = gameState.getAIPower();
            
            // 玩家战力
            ctx.fillStyle = '#4ade80';
            ctx.font = 'bold 36px Cinzel';
            ctx.textAlign = 'center';
            ctx.fillText(playerPower, w / 2, h - 130);
            ctx.font = '14px Cinzel';
            ctx.fillStyle = '#6a8a65';
            ctx.fillText('你的战力', w / 2, h - 110);
            
            // AI战力
            ctx.fillStyle = '#f87171';
            ctx.font = 'bold 36px Cinzel';
            ctx.fillText(aiPower, w / 2, 150);
            ctx.font = '14px Cinzel';
            ctx.fillStyle = '#8a6a65';
            ctx.fillText('敌方战力', w / 2, 170);
        }
        
        renderRoundInfo(ctx, w, h, gameState) {
            // 回合指示器
            ctx.fillStyle = '#c9a227';
            ctx.font = 'bold 18px Cinzel';
            ctx.textAlign = 'center';
            ctx.fillText(`第 ${gameState.round} 回合`, w / 2, 30);
            
            // 胜负标记
            const winsY = 50;
            
            // 玩家胜场
            for (let i = 0; i < 2; i++) {
                const x = w / 2 - 30 - i * 20;
                ctx.beginPath();
                ctx.arc(x, h - 95, 8, 0, Math.PI * 2);
                ctx.fillStyle = i < gameState.playerRoundWins ? '#4ade80' : '#2a3a2a';
                ctx.fill();
                ctx.strokeStyle = '#4ade80';
                ctx.lineWidth = 2;
                ctx.stroke();
            }
            
            // AI胜场
            for (let i = 0; i < 2; i++) {
                const x = w / 2 + 30 + i * 20;
                ctx.beginPath();
                ctx.arc(x, winsY + 30, 8, 0, Math.PI * 2);
                ctx.fillStyle = i < gameState.aiRoundWins ? '#f87171' : '#3a2a2a';
                ctx.fill();
                ctx.strokeStyle = '#f87171';
                ctx.lineWidth = 2;
                ctx.stroke();
            }
            
            // Pass状态
            if (gameState.playerPassed) {
                ctx.fillStyle = '#4ade80';
                ctx.font = '14px Cinzel';
                ctx.fillText('已放弃', w / 2 - 80, h - 155);
            }
            
            if (gameState.aiPassed) {
                ctx.fillStyle = '#f87171';
                ctx.font = '14px Cinzel';
                ctx.fillText('已放弃', w / 2 + 80, 200);
            }
            
            // 当前回合指示
            ctx.fillStyle = gameState.isPlayerTurn ? '#4ade80' : '#c080d0';
            ctx.font = '14px Cinzel';
            const turnText = gameState.isPlayerTurn ? '你的回合' : 'AI思考中...';
            ctx.fillText(turnText, w / 2, h / 2);
        }
        
        renderHighlights(ctx, w, h, gameState) {
            if (!this.selectedCard || this.selectedCard.type !== 'UNIT') return;
            
            const centerX = w / 2;
            const centerY = h / 2;
            const rowWidth = 500;
            const rowHeight = 80;
            const rowGap = 20;
            
            const rows = [
                { name: 'SIEGE', y: centerY - rowHeight - rowGap - rowHeight - rowGap },
                { name: 'RANGED', y: centerY - rowHeight - rowGap },
                { name: 'MELEE', y: centerY }
            ];
            
            const validRow = this.selectedCard.row;
            
            rows.forEach(row => {
                const isValid = !validRow || row.name === validRow;
                
                ctx.fillStyle = isValid ? 
                    'rgba(74, 222, 128, 0.15)' : 
                    'rgba(248, 113, 113, 0.1)';
                ctx.fillRect(centerX - rowWidth/2, row.y, rowWidth, rowHeight);
                
                if (isValid) {
                    ctx.strokeStyle = 'rgba(74, 222, 128, 0.5)';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(centerX - rowWidth/2, row.y, rowWidth, rowHeight);
                }
            });
        }
        
        calculateRowPower(cards, weather, rowType) {
            return cards.reduce((sum, card) => {
                if (card.type !== 'UNIT') return sum;
                let power = card.currentPower || card.power;
                
                if (weather === 'frost' && rowType === 'MELEE') power = 1;
                if (weather === 'fog' && rowType === 'RANGED') power = 1;
                if (weather === 'rain' && rowType === 'SIEGE') power = 1;
                
                return sum + power;
            }, 0);
        }
        
        truncateText(ctx, text, maxWidth) {
            if (ctx.measureText(text).width <= maxWidth) return text;
            
            while (ctx.measureText(text + '...').width > maxWidth && text.length > 0) {
                text = text.slice(0, -1);
            }
            return text + '...';
        }
        
        getClickedCard(gameState, x, y) {
            for (const card of gameState.playerHand) {
                if (card._renderX !== undefined &&
                    x >= card._renderX && x <= card._renderX + card._renderW &&
                    y >= card._renderY && y <= card._renderY + card._renderH) {
                    return card;
                }
            }
            return null;
        }
        
        getHoveredRow(w, h, x, y) {
            const centerX = w / 2;
            const centerY = h / 2;
            const rowWidth = 500;
            const rowHeight = 80;
            const rowGap = 20;
            
            const rows = [
                { name: 'SIEGE', y: centerY - rowHeight - rowGap - rowHeight - rowGap },
                { name: 'RANGED', y: centerY - rowHeight - rowGap },
                { name: 'MELEE', y: centerY }
            ];
            
            for (const row of rows) {
                if (x >= centerX - rowWidth/2 && x <= centerX + rowWidth/2 &&
                    y >= row.y && y <= row.y + rowHeight) {
                    return row.name;
                }
            }
            
            return null;
        }
    }
    
    // ==================== 主游戏类 ====================
    class GwentGame {
        constructor() {
            this.canvas = document.getElementById('gameCanvas');
            this.ctx = this.canvas.getContext('2d');
            
            this.gameState = new GameState();
            this.renderer = new GameRenderer(this.canvas, this.ctx);
            this.animationManager = new AnimationManager();
            this.aiSystem = new AIDecisionSystem('NORMAL');
            
            this.isAIThinking = false;
            
            this.setupEventListeners();
            this.resize();
            this.gameLoop();
        }
        
        setupEventListeners() {
            window.addEventListener('resize', () => this.resize());
            
            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.renderer.hoveredCard = this.renderer.getClickedCard(this.gameState, x, y);
                this.renderer.hoveredZone = this.renderer.getHoveredRow(
                    this.canvas.width, this.canvas.height, x, y
                );
            });
            
            this.canvas.addEventListener('click', (e) => {
                if (this.isAIThinking || !this.gameState.isPlayerTurn) return;
                
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const clickedCard = this.renderer.getClickedCard(this.gameState, x, y);
                
                if (clickedCard) {
                    if (this.renderer.selectedCard === clickedCard) {
                        // 双击打出
                        this.playCard(clickedCard);
                    } else {
                        this.renderer.selectedCard = clickedCard;
                    }
                } else if (this.renderer.selectedCard) {
                    // 检查是否点击了有效行
                    const clickedRow = this.renderer.getHoveredRow(
                        this.canvas.width, this.canvas.height, x, y
                    );
                    
                    if (clickedRow) {
                        this.playCard(this.renderer.selectedCard, clickedRow);
                    } else {
                        this.renderer.selectedCard = null;
                    }
                }
            });
            
            // 控制按钮
            document.getElementById('passBtn').addEventListener('click', () => {
                if (this.gameState.isPlayerTurn && !this.isAIThinking) {
                    this.playerPass();
                }
            });
            
            document.getElementById('leaderBtn').addEventListener('click', () => {
                if (this.gameState.isPlayerTurn && !this.gameState.playerLeaderUsed) {
                    this.useLeaderAbility('player');
                }
            });
            
            document.getElementById('newGameBtn').addEventListener('click', () => {
                this.gameState.reset();
                this.addLog('新游戏开始', 'system');
                this.updateTurnIndicator();
            });
            
            document.getElementById('forfeitBtn').addEventListener('click', () => {
                this.addLog('你认输了！', 'system');
                this.gameState.gamePhase = 'GAME_OVER';
            });
            
            // 难度选择
            document.querySelectorAll('.difficulty-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    const difficulty = e.target.dataset.difficulty;
                    this.aiSystem.setDifficulty(difficulty);
                    this.addLog(`AI难度设置为: ${difficulty}`, 'system');
                });
            });
            
            // 天气按钮
            document.querySelectorAll('.weather-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.weather-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    this.gameState.weather = e.target.dataset.weather;
                    this.addLog(`天气变更为: ${e.target.textContent}`, 'system');
                });
            });
        }
        
        resize() {
            this.renderer.resize();
        }
        
        playCard(card, targetRow = null) {
            if (!this.gameState.isPlayerTurn) return;
            if (this.gameState.playerPassed) return;
            
            const row = targetRow || card.row || 'MELEE';
            
            // 从手牌移除
            const index = this.gameState.playerHand.indexOf(card);
            if (index > -1) {
                this.gameState.playerHand.splice(index, 1);
            }
            
            // 特殊卡处理
            if (card.type === 'SPECIAL') {
                this.handleSpecialCard(card, 'player');
                this.addLog(`你打出了 ${card.name}`, 'player');
                this.renderer.selectedCard = null;
                this.endPlayerTurn();
                return;
            }
            
            // 天气卡
            if (card.type === 'WEATHER') {
                this.handleWeatherCard(card);
                this.addLog(`你打出了 ${card.name}`, 'player');
                this.renderer.selectedCard = null;
                this.endPlayerTurn();
                return;
            }
            
            // 间谍卡处理
            if (card.abilities && card.abilities.includes('SPY')) {
                this.gameState.aiBoard.push(card);
                // 抽2张牌
                for (let i = 0; i < 2; i++) {
                    if (this.gameState.playerDeck.length > 0) {
                        this.gameState.playerHand.push(this.gameState.playerDeck.pop());
                    }
                }
                this.addLog(`你打出了间谍 ${card.name}，抽了2张牌`, 'player');
            } else {
                this.gameState.playerBoard.push(card);
                this.addLog(`你打出了 ${card.name}`, 'player');
            }
            
            // 动画
            const cardPos = { x: card._renderX || this.canvas.width/2, y: card._renderY || this.canvas.height - 100 };
            const targetPos = this.getRowPosition(row, false);
            
            this.animationManager.playCardFly(
                card,
                cardPos.x,
                cardPos.y,
                targetPos.x,
                targetPos.y,
                card.color === 'GOLD'
            );
            
            this.animationManager.addPowerPopup(
                targetPos.x,
                targetPos.y - 30,
                card.power,
                true
            );
            
            this.renderer.selectedCard = null;
            this.endPlayerTurn();
        }
        
        handleSpecialCard(card, owner) {
            if (card.abilityType === 'SCORCH') {
                this.executeScorch(owner);
            } else if (card.abilityType === 'COMMANDERS_HORN') {
                // 简化处理：给最强一排加成
                const board = owner === 'player' ? this.gameState.playerBoard : this.gameState.aiBoard;
                let maxRow = 'MELEE';
                let maxPower = 0;
                
                ['MELEE', 'RANGED', 'SIEGE'].forEach(row => {
                    const power = board.filter(c => c.row === row)
                        .reduce((sum, c) => sum + (c.currentPower || c.power), 0);
                    if (power > maxPower) {
                        maxPower = power;
                        maxRow = row;
                    }
                });
                
                board.filter(c => c.row === maxRow).forEach(c => {
                    c.currentPower = (c.currentPower || c.power) * 2;
                });
                
                this.addLog(`指挥号角使 ${maxRow} 排战力翻倍`, 'system');
            }
        }
        
        executeScorch(caster) {
            const allUnits = [
                ...this.gameState.playerBoard.filter(c => c.type === 'UNIT'),
                ...this.gameState.aiBoard.filter(c => c.type === 'UNIT')
            ];
            
            if (allUnits.length === 0) return;
            
            const maxPower = Math.max(...allUnits.map(c => c.currentPower || c.power));
            const targets = allUnits.filter(c => (c.currentPower || c.power) === maxPower);
            
            targets.forEach(card => {
                // 从玩家战场移除
                const pIndex = this.gameState.playerBoard.indexOf(card);
                if (pIndex > -1) {
                    this.gameState.playerBoard.splice(pIndex, 1);
                    this.gameState.playerGrave.push(card);
                }
                
                // 从AI战场移除
                const aIndex = this.gameState.aiBoard.indexOf(card);
                if (aIndex > -1) {
                    this.gameState.aiBoard.splice(aIndex, 1);
                    this.gameState.aiGrave.push(card);
                }
            });
            
            this.addLog(`灼烧摧毁了 ${targets.length} 张战力 ${maxPower} 的单位`, 'system');
            
            // 特效
            this.animationManager.addShockwave(
                this.canvas.width / 2,
                this.canvas.height / 2,
                '#ff4444',
                200
            );
        }
        
        handleWeatherCard(card) {
            if (card.abilityType === 'BITING_FROST') {
                this.gameState.weather = 'frost';
                this.addLog('霜冻降临！近战单位战力变为1', 'system');
            } else if (card.abilityType === 'IMPENETRABLE_FOG') {
                this.gameState.weather = 'fog';
                this.addLog('浓雾弥漫！远程单位战力变为1', 'system');
            }
            
            // 更新天气按钮
            document.querySelectorAll('.weather-btn').forEach(btn => {
                btn.classList.remove('active');
                if ((card.abilityType === 'BITING_FROST' && btn.dataset.weather === 'frost') ||
                    (card.abilityType === 'IMPENETRABLE_FOG' && btn.dataset.weather === 'fog')) {
                    btn.classList.add('active');
                }
            });
        }
        
        playerPass() {
            this.gameState.playerPassed = true;
            this.addLog('你放弃了本回合', 'player');
            
            // 检查回合结束
            if (this.gameState.aiPassed) {
                this.endRound();
            } else {
                this.endPlayerTurn();
            }
        }
        
        endPlayerTurn() {
            this.gameState.isPlayerTurn = false;
            this.updateTurnIndicator();
            
            // 检查回合结束
            if (this.gameState.playerPassed && this.gameState.aiPassed) {
                this.endRound();
                return;
            }
            
            // AI回合
            setTimeout(() => this.aiTurn(), CONFIG.AI_THINK_TIME);
        }
        
        aiTurn() {
            if (this.gameState.aiPassed) {
                this.gameState.isPlayerTurn = true;
                this.updateTurnIndicator();
                return;
            }
            
            this.isAIThinking = true;
            document.getElementById('aiThinking').classList.add('visible');
            
            // 构建AI决策所需的游戏状态
            const aiGameState = {
                aiHand: this.gameState.aiHand,
                aiBoard: this.gameState.aiBoard,
                playerBoard: this.gameState.playerBoard,
                playerHand: this.gameState.playerHand,
                round: this.gameState.round,
                playerPassed: this.gameState.playerPassed,
                aiPassed: this.gameState.aiPassed,
                aiRoundWins: this.gameState.aiRoundWins,
                playerRoundWins: this.gameState.playerRoundWins,
                weather: this.gameState.weather,
                aiGrave: this.gameState.aiGrave,
                playerGrave: this.gameState.playerGrave
            };
            
            setTimeout(() => {
                const decision = this.aiSystem.makeDecision(aiGameState);
                
                if (decision.action === 'PASS') {
                    this.aiPass(decision.reason);
                } else {
                    this.aiPlayCard(decision.card, decision.row, decision.isSpy);
                }
                
                this.isAIThinking = false;
                document.getElementById('aiThinking').classList.remove('visible');
            }, this.aiSystem.config.thinkTime);
        }
        
        aiPass(reason) {
            this.gameState.aiPassed = true;
            this.addLog(`AI放弃了本回合 (${reason || '战术决策'})`, 'ai');
            
            if (this.gameState.playerPassed) {
                this.endRound();
            } else {
                this.gameState.isPlayerTurn = true;
                this.updateTurnIndicator();
            }
        }
        
        aiPlayCard(card, targetRow, isSpy = false) {
            // 从手牌移除
            const index = this.gameState.aiHand.indexOf(card);
            if (index > -1) {
                this.gameState.aiHand.splice(index, 1);
            }
            
            // 特殊卡处理
            if (card.type === 'SPECIAL') {
                this.handleSpecialCard(card, 'ai');
                this.addLog(`AI打出了 ${card.name}`, 'ai');
                this.endAITurn();
                return;
            }
            
            // 天气卡
            if (card.type === 'WEATHER') {
                this.handleWeatherCard(card);
                this.addLog(`AI打出了 ${card.name}`, 'ai');
                this.endAITurn();
                return;
            }
            
            const row = targetRow || card.row || 'MELEE';
            
            // 间谍卡给玩家
            if (isSpy || (card.abilities && card.abilities.includes('SPY'))) {
                this.gameState.playerBoard.push(card);
                // AI抽牌
                for (let i = 0; i < 2; i++) {
                    if (this.gameState.aiDeck.length > 0) {
                        this.gameState.aiHand.push(this.gameState.aiDeck.pop());
                    }
                }
                this.addLog(`AI打出间谍 ${card.name}`, 'ai');
            } else {
                this.gameState.aiBoard.push(card);
                this.addLog(`AI打出了 ${card.name}`, 'ai');
            }
            
            // 动画
            const startX = this.canvas.width / 2;
            const startY = 80;
            const targetPos = this.getRowPosition(row, true);
            
            this.animationManager.playCardFly(
                card,
                startX,
                startY,
                targetPos.x,
                targetPos.y,
                card.color === 'GOLD'
            );
            
            this.animationManager.addPowerPopup(
                targetPos.x,
                targetPos.y - 30,
                card.power,
                false
            );
            
            this.endAITurn();
        }
        
        endAITurn() {
            // 检查回合结束
            if (this.gameState.playerPassed && this.gameState.aiPassed) {
                this.endRound();
                return;
            }
            
            // 如果玩家已pass，AI继续打
            if (this.gameState.playerPassed && !this.gameState.aiPassed) {
                setTimeout(() => this.aiTurn(), CONFIG.AI_THINK_TIME);
                return;
            }
            
            this.gameState.isPlayerTurn = true;
            this.updateTurnIndicator();
        }
        
        endRound() {
            const playerPower = this.gameState.getPlayerPower();
            const aiPower = this.gameState.getAIPower();
            
            let resultText = '';
            
            if (playerPower > aiPower) {
                this.gameState.playerRoundWins++;
                resultText = `你赢得了第 ${this.gameState.round} 回合！ (${playerPower} vs ${aiPower})`;
            } else if (aiPower > playerPower) {
                this.gameState.aiRoundWins++;
                resultText = `AI赢得了第 ${this.gameState.round} 回合 (${aiPower} vs ${playerPower})`;
            } else {
                resultText = `第 ${this.gameState.round} 回合平局！ (${playerPower} vs ${aiPower})`;
            }
            
            this.addLog(resultText, 'system');
            
            // 冲击波特效
            this.animationManager.addShockwave(
                this.canvas.width / 2,
                this.canvas.height / 2,
                '#c9a227',
                300
            );
            
            // 检查游戏结束
            if (this.gameState.playerRoundWins >= 2) {
                this.addLog('恭喜！你赢得了比赛！', 'system');
                this.gameState.gamePhase = 'GAME_OVER';
                return;
            }
            
            if (this.gameState.aiRoundWins >= 2) {
                this.addLog('AI赢得了比赛！再接再厉！', 'system');
                this.gameState.gamePhase = 'GAME_OVER';
                return;
            }
            
            // 开始新回合
            setTimeout(() => {
                this.gameState.startNewRound();
                this.addLog(`第 ${this.gameState.round} 回合开始`, 'system');
                
                // 输掉上回合的先手
                this.gameState.isPlayerTurn = playerPower <= aiPower;
                this.updateTurnIndicator();
                
                if (!this.gameState.isPlayerTurn) {
                    setTimeout(() => this.aiTurn(), CONFIG.AI_THINK_TIME);
                }
            }, 1500);
        }
        
        useLeaderAbility(owner) {
            if (owner === 'player') {
                this.gameState.playerLeaderUsed = true;
                document.getElementById('leaderBtn').classList.add('used');
                this.addLog('你使用了领袖技能', 'player');
                
                // 简化效果：抽一张牌
                if (this.gameState.playerDeck.length > 0) {
                    this.gameState.playerHand.push(this.gameState.playerDeck.pop());
                    this.addLog('你抽了一张牌', 'player');
                }
            }
        }
        
        getRowPosition(rowName, isEnemy) {
            const centerX = this.canvas.width / 2;
            const centerY = this.canvas.height / 2;
            const rowHeight = 80;
            const rowGap = 20;
            
            const positions = {
                'MELEE': { y: isEnemy ? centerY + rowGap + rowHeight + rowHeight/2 : centerY + rowHeight/2 },
                'RANGED': { y: isEnemy ? centerY + (rowGap + rowHeight) * 2 + rowHeight/2 : centerY - rowHeight/2 - rowGap + rowHeight/2 },
                'SIEGE': { y: isEnemy ? centerY + (rowGap + rowHeight) * 3 + rowHeight/2 : centerY - rowHeight - rowGap - rowHeight/2 }
            };
            
            return {
                x: centerX + (Math.random() - 0.5) * 200,
                y: positions[rowName]?.y || centerY
            };
        }
        
        addLog(message, type = 'system') {
            const logContainer = document.getElementById('gameLog');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.textContent = message;
            logContainer.appendChild(entry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // 限制日志条数
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        updateTurnIndicator() {
            const indicator = document.getElementById('turnIndicator');
            if (this.gameState.isPlayerTurn) {
                indicator.textContent = '轮到你行动';
                indicator.style.color = '#4ade80';
            } else {
                indicator.textContent = 'AI正在思考...';
                indicator.style.color = '#c080d0';
            }
        }
        
        gameLoop() {
            // 更新动画
            this.animationManager.update();
            
            // 渲染
            this.renderer.render(this.gameState, this.animationManager);
            
            requestAnimationFrame(() => this.gameLoop());
        }
    }
    
    // ==================== 初始化游戏 ====================
    window.addEventListener('DOMContentLoaded', () => {
        const game = new GwentGame();
        game.addLog('欢迎来到昆特牌！选择卡牌后点击战场放置', 'system');
        game.addLog('提示：可以调整AI难度来挑战自己', 'system');
        game.updateTurnIndicator();
    });
    
})();
</script>
</body>
</html>
```

## 实现说明

### AI决策系统核心功能

1. **三档难度配置**
   - **简单 (EASY)**: 40%随机决策，高犯错率，短视策略
   - **普通 (NORMAL)**: 20%随机决策，中等策略深度
   - **困难 (HARD)**: 5%随机决策，深谋远虑，注重卡差

2. **战力差距评估**
   - 实时计算双方总战力差
   - 考虑天气对各单位排的影响
   - 评估卡牌能力带来的潜在战力变化

3. **卡牌价值排序**
   - 单位卡：基础战力 + 能力加成 + 天气影响
   - 间谍卡：根据当前局势动态评估（领先时价值高）
   - 灼烧卡：评估双方最高战力单位数量
   - 天气卡：评估对双方的损益比

4. **Pass策略**
   - 第一回合大比分领先时pass换取卡差
   - 落后太多时放弃保卡
   - 赛点回合谨慎pass
   - 考虑卡差优势的长期价值

5. **特殊卡牌时机判断**
   - 灼烧：确保消灭足够多的敌方单位且不伤及己方
   - 指挥号角：选择战力最高的一排使用
   - 天气卡：只在对方受损更大时使用