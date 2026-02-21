// server.js - 球球大作战游戏服务器

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const mongoose = require('mongoose');
const redis = require('redis');
const jwt = require('jsonwebtoken');

// 配置常量
const PORT = process.env.PORT || 3001;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/balls-game';
const REDIS_URI = process.env.REDIS_URI || 'redis://localhost:6379';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const MAX_PLAYERS_PER_ROOM = 10;
const MAP_WIDTH = 3000;
const MAP_HEIGHT = 3000;
const FOOD_COUNT = 500;
const MIN_BALL_SIZE = 10;
const MAX_BALL_SIZE = 100;

// 初始化 Express 应用
const app = express();
app.use(cors());
app.use(express.json());

// 创建 HTTP 服务器
const server = http.createServer(app);

// 初始化 Socket.IO
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// 初始化 Redis 客户端
const redisClient = redis.createClient(REDIS_URI);
redisClient.on('error', (err) => {
    console.error('Redis 连接错误:', err);
});

// 连接 MongoDB
mongoose.connect(MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => {
    console.log('MongoDB 连接成功');
}).catch(err => {
    console.error('MongoDB 连接失败:', err);
});

// 定义 MongoDB 模型
const PlayerSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    score: { type: Number, default: 0 },
    totalGames: { type: Number, default: 0 },
    wins: { type: Number, default: 0 },
    createdAt: { type: Date, default: Date.now }
});

const Player = mongoose.model('Player', PlayerSchema);

// 游戏状态管理
class GameState {
    constructor() {
        this.players = new Map();
        this.foods = [];
        this.rooms = new Map();
        this.initializeFoods();
    }

    // 初始化食物
    initializeFoods() {
        this.foods = [];
        for (let i = 0; i < FOOD_COUNT; i++) {
            this.foods.push({
                id: i,
                x: Math.random() * MAP_WIDTH,
                y: Math.random() * MAP_HEIGHT,
                size: Math.random() * 5 + 2,
                color: this.getRandomColor()
            });
        }
    }

    // 生成随机颜色
    getRandomColor() {
        const colors = ['#FF5252', '#FF4081', '#E040FB', '#7C4DFF', '#536DFE', 
                        '#448AFF', '#40C4FF', '#18FFFF', '#64FFDA', '#69F0AE',
                        '#B2FF59', '#EEFF41', '#FFFF00', '#FFD740', '#FFAB40',
                        '#FF6E40'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    // 添加玩家
    addPlayer(playerId, username, socket) {
        const player = {
            id: playerId,
            username: username,
            x: Math.random() * MAP_WIDTH,
            y: Math.random() * MAP_HEIGHT,
            size: MIN_BALL_SIZE,
            color: this.getRandomColor(),
            socket: socket,
            score: 0,
            isAlive: true
        };
        
        this.players.set(playerId, player);
        return player;
    }

    // 移动玩家
    movePlayer(playerId, x, y) {
        const player = this.players.get(playerId);
        if (player) {
            // 限制在地图范围内
            player.x = Math.max(player.size, Math.min(MAP_WIDTH - player.size, x));
            player.y = Math.max(player.size, Math.min(MAP_HEIGHT - player.size, y));
        }
    }

    // 更新玩家大小
    updatePlayerSize(playerId, size) {
        const player = this.players.get(playerId);
        if (player) {
            player.size = Math.max(MIN_BALL_SIZE, Math.min(MAX_BALL_SIZE, size));
        }
    }

    // 检查碰撞
    checkCollisions(playerId) {
        const player = this.players.get(playerId);
        if (!player || !player.isAlive) return;

        // 检查与食物的碰撞
        for (let i = 0; i < this.foods.length; i++) {
            const food = this.foods[i];
            const dx = player.x - food.x;
            const dy = player.y - food.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < player.size + food.size) {
                // 吃掉食物
                player.size += food.size * 0.1;
                player.score += Math.floor(food.size);
                
                // 移除被吃掉的食物，生成新的食物
                this.foods.splice(i, 1);
                this.foods.push({
                    id: this.foods.length,
                    x: Math.random() * MAP_WIDTH,
                    y: Math.random() * MAP_HEIGHT,
                    size: Math.random() * 5 + 2,
                    color: this.getRandomColor()
                });
                
                i--;
            }
        }

        // 检查与其他玩家的碰撞
        for (const [otherId, otherPlayer] of this.players) {
            if (playerId !== otherId && otherPlayer.isAlive) {
                const dx = player.x - otherPlayer.x;
                const dy = player.y - otherPlayer.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < player.size + otherPlayer.size) {
                    // 大的球吃掉小的球
                    if (player.size > otherPlayer.size * 1.1) {
                        player.size += otherPlayer.size * 0.5;
                        player.score += Math.floor(otherPlayer.size * 10);
                        otherPlayer.isAlive = false;
                        
                        // 通知其他玩家
                        this.broadcastToRoom(otherPlayer.roomId, 'playerEaten', {
                            eatenPlayerId: otherId,
                            eatenByPlayerId: playerId
                        });
                    } else if (otherPlayer.size > player.size * 1.1) {
                        otherPlayer.size += player.size * 0.5;
                        otherPlayer.score += Math.floor(player.size * 10);
                        player.isAlive = false;
                        
                        // 通知其他玩家
                        this.broadcastToRoom(player.roomId, 'playerEaten', {
                            eatenPlayerId: playerId,
                            eatenByPlayerId: otherId
                        });
                    }
                }
            }
        }
    }

    // 创建房间
    createRoom(roomId) {
        if (!this.rooms.has(roomId)) {
            this.rooms.set(roomId, {
                id: roomId,
                players: new Map(),
                maxPlayers: MAX_PLAYERS_PER_ROOM,
                gameState: 'waiting' // waiting, playing, ended
            });
        }
        return this.rooms.get(roomId);
    }

    // 加入房间
    joinRoom(roomId, playerId) {
        let room = this.rooms.get(roomId);
        
        // 如果房间不存在，创建新房间
        if (!room) {
            room = this.createRoom(roomId);
        }
        
        // 如果房间已满，创建新房间
        if (room.players.size >= room.maxPlayers) {
            const newRoomId = `room-${Date.now()}`;
            room = this.createRoom(newRoomId);
            roomId = newRoomId;
        }
        
        // 添加玩家到房间
        const player = this.players.get(playerId);
        if (player) {
            player.roomId = roomId;
            room.players.set(playerId, player);
            
            // 如果房间人数达到要求，开始游戏
            if (room.players.size >= 2 && room.gameState === 'waiting') {
                room.gameState = 'playing';
                this.broadcastToRoom(roomId, 'gameStart', {
                    players: Array.from(room.players.values()).map(p => ({
                        id: p.id,
                        username: p.username,
                        x: p.x,
                        y: p.y,
                        size: p.size,
                        color: p.color
                    }))
                });
            }
        }
        
        return room;
    }

    // 离开房间
    leaveRoom(roomId, playerId) {
        const room = this.rooms.get(roomId);
        if (room) {
            room.players.delete(playerId);
            
            // 如果房间为空，删除房间
            if (room.players.size === 0) {
                this.rooms.delete(roomId);
            }
            // 如果游戏进行中，检查是否结束
            else if (room.gameState === 'playing') {
                const alivePlayers = Array.from(room.players.values()).filter(p => p.isAlive);
                
                // 如果只剩一个玩家，游戏结束
                if (alivePlayers.length === 1) {
                    room.gameState = 'ended';
                    this.broadcastToRoom(roomId, 'gameEnd', {
                        winner: alivePlayers[0]
                    });
                }
            }
        }
    }

    // 广播消息到房间
    broadcastToRoom(roomId, event, data) {
        const room = this.rooms.get(roomId);
        if (room) {
            room.players.forEach(player => {
                if (player.socket && player.socket.connected) {
                    player.socket.emit(event, data);
                }
            });
        }
    }

    // 获取房间状态
    getRoomState(roomId) {
        const room = this.rooms.get(roomId);
        if (room) {
            return {
                id: room.id,
                players: Array.from(room.players.values()).map(p => ({
                    id: p.id,
                    username: p.username,
                    x: p.x,
                    y: p.y,
                    size: p.size,
                    color: p.color,
                    isAlive: p.isAlive,
                    score: p.score
                })),
                gameState: room.gameState
            };
        }
        return null;
    }
}

// 创建游戏实例
const gameState = new GameState();

// API 路由
// 注册
app.post('/api/register', async (req, res) => {
    try {
        const { username, password } = req.body;
        
        // 检查用户名是否已存在
        const existingUser = await Player.findOne({ username });
        if (existingUser) {
            return res.status(400).json({ message: '用户名已存在' });
        }
        
        // 创建新用户
        const player = new Player({
            username,
            password: password // 在实际应用中应该使用 bcrypt 加密
        });
        
        await player.save();
        
        // 生成 JWT token
        const token = jwt.sign({ playerId: player._id }, JWT_SECRET, { expiresIn: '7d' });
        
        res.status(201).json({
            message: '注册成功',
            token,
            player: {
                id: player._id,
                username: player.username,
                score: player.score
            }
        });
    } catch (error) {
        console.error('注册错误:', error);
        res.status(500).json({ message: '服务器错误' });
    }
});

// 登录
app.post('/api/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        
        // 查找用户
        const player = await Player.findOne({ username });
        if (!player) {
            return res.status(401).json({ message: '用户名或密码错误' });
        }
        
        // 验证密码 (在实际应用中应该使用 bcrypt 验证)
        if (player.password !== password) {
            return res.status(401).json({ message: '用户名或密码错误' });
        }
        
        // 生成 JWT token
        const token = jwt.sign({ playerId: player._id }, JWT_SECRET, { expiresIn: '7d' });
        
        res.json({
            message: '登录成功',
            token,
            player: {
                id: player._id,
                username: player.username,
                score: player.score
            }
        });
    } catch (error) {
        console.error('登录错误:', error);
        res.status(500).json({ message: '服务器错误' });
    }
});

// 获取排行榜
app.get('/api/leaderboard', async (req, res) => {
    try {
        const players = await Player.find()
            .sort({ score: -1 })
            .limit(10)
            .select('username score wins');
            
        res.json(players);
    } catch (error) {
        console.error('获取排行榜错误:', error);
        res.status(500).json({ message: '服务器错误' });
    }
});

// Socket.IO 连接处理
io.on('connection', (socket) => {
    console.log('用户连接:', socket.id);
    
    // 解析 JWT token
    let playerId = null;
    let playerUsername = null;
    
    socket.on('authenticate', async (token) => {
        try {
            const decoded = jwt.verify(token, JWT_SECRET);
            playerId = decoded.playerId;
            
            // 从数据库获取用户信息
            const player = await Player.findById(playerId);
            if (player) {
                playerUsername = player.username;
                
                // 添加玩家到游戏状态
                const playerData = gameState.addPlayer(playerId, playerUsername, socket);
                
                // 创建或加入房间
                const roomId = `room-${Date.now()}`;
                const room = gameState.joinRoom(roomId, playerId);
                
                // 发送初始游戏状态
                socket.emit('authenticated', {
                    playerId,
                    player: {
                        id: playerData.id,
                        username: playerData.username,
                        x: playerData.x,
                        y: playerData.y,
                        size: playerData.size,
                        color: playerData.color
                    },
                    roomId: room.id,
                    gameState: gameState.getRoomState(room.id)
                });
                
                console.log(`用户 ${playerUsername} 认证成功，加入房间 ${roomId}`);
            } else {
                throw new Error('用户不存在');
            }
        } catch (error) {
            console.error('认证错误:', error);
            socket.emit('authError', { message: '认证失败' });
        }
    });
    
    // 玩家移动
    socket.on('playerMove', (data) => {
        if (playerId) {
            gameState.movePlayer(playerId, data.x, data.y);
        }
    });
    
    // 玩家更新大小（用于吃球增长）
    socket.on('playerUpdateSize', (data) => {
        if (playerId) {
            gameState.updatePlayerSize(playerId, data.size);
        }
    });
    
    // 加入房间
    socket.on('joinRoom', async (data) => {
        if (playerId) {
            try {
                const room = gameState.joinRoom(data.roomId, playerId);
                socket.join(data.roomId);
                
                // 发送房间状态
                socket.emit('roomJoined', {
                    roomId: room.id,
                    gameState: gameState.getRoomState(room.id)
                });
                
                // 通知房间内其他玩家
                socket.to(data.roomId).emit('playerJoined', {
                    player: {
                        id: playerId,
                        username: playerUsername,
                        x: gameState.players.get(playerId).x,
                        y: gameState.players.get(playerId).y,
                        size: gameState.players.get(playerId).size,
                        color: gameState.players.get(playerId).color
                    }
                });
                
                console.log(`用户 ${playerUsername} 加入房间 ${data.roomId}`);
            } catch (error) {
                console.error('加入房间错误:', error);
                socket.emit('roomError', { message: '加入房间失败' });
            }
        }
    });
    
    // 创建房间
    socket.on('createRoom', () => {
        if (playerId) {
            const roomId = `room-${Date.now()}`;
            const room = gameState.createRoom(roomId);
            socket.join(roomId);
            
            socket.emit('roomCreated', {
                roomId: room.id
            });
            
            console.log(`用户 ${playerUsername} 创建房间 ${roomId}`);
        }
    });
    
    // 离开房间
    socket.on('leaveRoom', (data) => {
        if (playerId && data.roomId) {
            gameState.leaveRoom(data.roomId, playerId);
            socket.leave(data.roomId);
            
            // 通知房间内其他玩家
            socket.to(data.roomId).emit('playerLeft', {
                playerId
            });
            
            console.log(`用户 ${playerUsername} 离开房间 ${data.roomId}`);
        }
    });
    
    // 断开连接
    socket.on('disconnect', () => {
        if (playerId) {
            const player = gameState.players.get(playerId);
            if (player && player.roomId) {
                gameState.leaveRoom(player.roomId, playerId);
                
                // 通知房间内其他玩家
                socket.to(player.roomId).emit('playerDisconnected', {
                    playerId
                });
            }
            
            gameState.players.delete(playerId);
            console.log(`用户 ${playerUsername} 断开连接`);
        }
    });
});

// 游戏循环
setInterval(() => {
    // 检查所有玩家的碰撞
    for (const [playerId] of gameState.players) {
        gameState.checkCollisions(playerId);
    }
    
    // 广播游戏状态到所有房间
    for (const [roomId, room] of gameState.rooms) {
        if (room.gameState === 'playing') {
            const roomState = gameState.getRoomState(roomId);
            gameState.broadcastToRoom(roomId, 'gameUpdate', roomState);
        }
    }
}, 100); // 每100毫秒更新一次游戏状态

// 启动服务器
server.listen(PORT, () => {
    console.log(`服务器运行在端口 ${PORT}`);
});