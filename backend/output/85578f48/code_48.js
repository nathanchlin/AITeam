// 客户端同步逻辑
class ClientSync {
    constructor(socket) {
        this.socket = socket;
        this.gameState = {};
        this.pendingInputs = [];
        this.lastServerState = null;
        this.lastUpdateTime = 0;
        this.latency = 0;
        
        // 监听服务器状态更新
        this.socket.on('gameState', (state) => {
            this.onServerState(state);
        });
    }
    
    // 发送输入到服务器
    sendInput(input) {
        this.pendingInputs.push(input);
        this.socket.emit('playerInput', input);
    }
    
    // 接收服务器状态
    onServerState(state) {
        // 计算延迟
        const now = Date.now();
        this.latency = now - state.timestamp;
        
        // 存储服务器状态
        this.lastServerState = state;
        this.lastUpdateTime = now;
        
        // 应用状态到游戏
        this.applyGameState(state);
    }
    
    // 应用游戏状态
    applyGameState(state) {
        // 更新玩家状态
        for (const player of state.players) {
            if (player.id === this.socket.id) {
                // 这是当前玩家，使用客户端预测的位置
                continue;
            }
            
            // 其他玩家使用服务器位置
            this.gameState.players[player.id] = player;
        }
        
        // 更新食物状态
        this.gameState.foods = state.foods;
        
        // 处理待处理的输入
        this.processPendingInputs();
    }
    
    // 处理待处理的输入
    processPendingInputs() {
        // 这里可以添加输入预测和回滚逻辑
    }
}