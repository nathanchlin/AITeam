class GomokuGame {
    constructor(boardSize = 15) {
        this.boardSize = boardSize;
        this.board = [];
        this.currentPlayer = 1; // 1: 黑棋, 2: 白棋
        this.gameOver = false;
        this.moveHistory = [];
        this.winner = null;
        this.winningLine = [];
        
        this.initBoard();
    }
    
    // 初始化棋盘
    initBoard() {
        this.board = [];
        for (let i = 0; i < this.boardSize; i++) {
            this.board[i] = [];
            for (let j = 0; j < this.boardSize; j++) {
                this.board[i][j] = 0;
            }
        }
        this.currentPlayer = 1;
        this.gameOver = false;
        this.moveHistory = [];
        this.winner = null;
        this.winningLine = [];
    }
    
    // 落子
    placePiece(row, col) {
        // 检查游戏是否结束
        if (this.gameOver) {
            return { success: false, message: "游戏已结束" };
        }
        
        // 检查位置是否有效
        if (row < 0 || row >= this.boardSize || col < 0 || col >= this.boardSize) {
            return { success: false, message: "位置无效" };
        }
        
        // 检查位置是否已有棋子
        if (this.board[row][col] !== 0) {
            return { success: false, message: "该位置已有棋子" };
        }
        
        // 落子
        this.board[row][col] = this.currentPlayer;
        this.moveHistory.push({ row, col, player: this.currentPlayer });
        
        // 检查是否获胜
        const winResult = this.checkWin(row, col);
        if (winResult.win) {
            this.gameOver = true;
            this.winner = this.currentPlayer;
            this.winningLine = winResult.line;
            return { 
                success: true, 
                message: `玩家${this.currentPlayer === 1 ? "黑棋" : "白棋"}获胜！`,
                win: true,
                winningLine: winResult.line
            };
        }
        
        // 检查是否平局
        if (this.moveHistory.length === this.boardSize * this.boardSize) {
            this.gameOver = true;
            return { success: true, message: "平局！", draw: true };
        }
        
        // 切换玩家
        this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
        return { success: true, message: "落子成功" };
    }
    
    // 检查是否获胜
    checkWin(row, col) {
        const directions = [
            { dx: 1, dy: 0 },  // 横向
            { dx: 0, dy: 1 },  // 纵向
            { dx: 1, dy: 1 },  // 右下对角线
            { dx: 1, dy: -1 }  // 右上对角线
        ];
        
        for (const { dx, dy } of directions) {
            const line = this.checkDirection(row, col, dx, dy);
            if (line.length >= 5) {
                return { win: true, line };
            }
        }
        
        return { win: false };
    }
    
    // 检查特定方向是否有五子连珠
    checkDirection(row, col, dx, dy) {
        const player = this.board[row][col];
        const line = [{ row, col }];
        
        // 正向检查
        let r = row + dx;
        let c = col + dy;
        while (r >= 0 && r < this.boardSize && c >= 0 && c < this.boardSize && this.board[r][c] === player) {
            line.push({ row: r, col: c });
            r += dx;
            c += dy;
        }
        
        // 反向检查
        r = row - dx;
        c = col - dy;
        while (r >= 0 && r < this.boardSize && c >= 0 && c < this.boardSize && this.board[r][c] === player) {
            line.unshift({ row: r, col: c });
            r -= dx;
            c -= dy;
        }
        
        return line;
    }
    
    // 悔棋
    undo() {
        if (this.moveHistory.length === 0) {
            return { success: false, message: "没有可撤销的步骤" };
        }
        
        if (this.gameOver) {
            this.gameOver = false;
            this.winner = null;
            this.winningLine = [];
        }
        
        const lastMove = this.moveHistory.pop();
        this.board[lastMove.row][lastMove.col] = 0;
        this.currentPlayer = lastMove.player;
        
        return { success: true, message: "悔棋成功" };
    }
    
    // 重新开始
    restart() {
        this.initBoard();
        return { success: true, message: "游戏已重新开始" };
    }
    
    // 获取游戏状态
    getGameState() {
        return {
            board: this.board,
            currentPlayer: this.currentPlayer,
            gameOver: this.gameOver,
            winner: this.winner,
            moveHistory: this.moveHistory,
            winningLine: this.winningLine
        };
    }
}

// 渲染器类
class BoardRenderer {
    constructor(containerId, game) {
        this.container = document.getElementById(containerId);
        this.game = game;
        this.boardElement = null;
        this.statusElement = null;
        this.messageElement = null;
        
        this.init();
    }
    
    init() {
        // 创建棋盘容器
        this.boardElement = document.createElement('div');
        this.boardElement.className = 'gomoku-board';
        this.container.appendChild(this.boardElement);
        
        // 创建状态显示区域
        const statusContainer = document.createElement('div');
        statusContainer.className = 'game-status';
        this.container.appendChild(statusContainer);
        
        // 当前玩家显示
        this.statusElement = document.createElement('div');
        this.statusElement.className = 'current-player';
        statusContainer.appendChild(this.statusElement);
        
        // 消息显示区域
        this.messageElement = document.createElement('div');
        this.messageElement.className = 'game-message';
        statusContainer.appendChild(this.messageElement);
        
        // 控制按钮
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'game-controls';
        
        const undoButton = document.createElement('button');
        undoButton.textContent = '悔棋';
        undoButton.addEventListener('click', () => this.handleUndo());
        buttonContainer.appendChild(undoButton);
        
        const restartButton = document.createElement('button');
        restartButton.textContent = '重新开始';
        restartButton.addEventListener('click', () => this.handleRestart());
        buttonContainer.appendChild(restartButton);
        
        statusContainer.appendChild(buttonContainer);
        
        // 初始化渲染
        this.render();
    }
    
    render() {
        // 清空棋盘
        this.boardElement.innerHTML = '';
        
        // 创建棋盘网格
        for (let i = 0; i < this.game.boardSize; i++) {
            for (let j = 0; j < this.game.boardSize; j++) {
                const cell = document.createElement('div');
                cell.className = 'board-cell';
                cell.dataset.row = i;
                cell.dataset.col = j;
                
                // 添加点击事件
                cell.addEventListener('click', () => this.handleCellClick(i, j));
                
                // 添加棋子
                if (this.game.board[i][j] !== 0) {
                    const piece = document.createElement('div');
                    piece.className = `piece ${this.game.board[i][j] === 1 ? 'black' : 'white'}`;
                    
                    // 如果是获胜棋子，添加特殊标记
                    if (this.game.gameOver && this.game.winningLine.some(pos => pos.row === i && pos.col === j)) {
                        piece.classList.add('winning');
                    }
                    
                    cell.appendChild(piece);
                }
                
                this.boardElement.appendChild(cell);
            }
        }
        
        // 更新状态显示
        this.updateStatus();
    }
    
    updateStatus() {
        const state = this.game.getGameState();
        
        if (state.gameOver) {
            if (state.winner) {
                this.statusElement.textContent = `游戏结束 - ${state.winner === 1 ? "黑棋" : "白棋"}获胜！`;
            } else {
                this.statusElement.textContent = "游戏结束 - 平局！";
            }
        } else {
            this.statusElement.textContent = `当前玩家: ${state.currentPlayer === 1 ? "黑棋" : "白棋"}`;
        }
    }
    
    handleCellClick(row, col) {
        const result = this.game.placePiece(row, col);
        this.showMessage(result.message);
        
        if (result.success) {
            this.render();
            
            if (result.win) {
                this.highlightWinningLine(result.winningLine);
            }
        }
    }
    
    handleUndo() {
        const result = this.game.undo();
        this.showMessage(result.message);
        this.render();
    }
    
    handleRestart() {
        const result = this.game.restart();
        this.showMessage(result.message);
        this.render();
    }
    
    showMessage(message) {
        this.messageElement.textContent = message;
        setTimeout(() => {
            this.messageElement.textContent = '';
        }, 3000);
    }
    
    highlightWinningLine(line) {
        line.forEach(pos => {
            const cell = this.boardElement.querySelector(`[data-row="${pos.row}"][data-col="${pos.col}"]`);
            if (cell) {
                cell.classList.add('winning-cell');
            }
        });
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    const game = new GomokuGame(15);
    const renderer = new BoardRenderer('game-container', game);
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .gomoku-board {
            display: grid;
            grid-template-columns: repeat(15, 30px);
            grid-template-rows: repeat(15, 30px);
            gap: 1px;
            background-color: #dcb35c;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .board-cell {
            width: 30px;
            height: 30px;
            background-color: #dcb35c;
            position: relative;
            cursor: pointer;
        }
        
        .board-cell::before, .board-cell::after {
            content: '';
            position: absolute;
            background-color: #000;
        }
        
        .board-cell::before {
            width: 100%;
            height: 1px;
            top: 50%;
            left: 0;
            transform: translateY(-50%);
        }
        
        .board-cell::after {
            width: 1px;
            height: 100%;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
        }
        
        .piece {
            position: absolute;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1;
        }
        
        .piece.black {
            background: radial-gradient(circle at 30% 30%, #666, #000);
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
        }
        
        .piece.white {
            background: radial-gradient(circle at 30% 30%, #fff, #ccc);
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        .piece.winning {
            animation: pulse 1s infinite;
        }
        
        .winning-cell {
            background-color: rgba(255, 215, 0, 0.5);
        }
        
        .game-status {
            margin-top: 20px;
            text-align: center;
        }
        
        .current-player {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .game-message {
            min-height: 24px;
            color: #d9534f;
            font-weight: bold;
        }
        
        .game-controls {
            margin-top: 15px;
        }
        
        .game-controls button {
            margin: 0 5px;
            padding: 8px 15px;
            background-color: #5cb85c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        .game-controls button:hover {
            background-color: #4cae4c;
        }
        
        @keyframes pulse {
            0% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.1); }
            100% { transform: translate(-50%, -50%) scale(1); }
        }
    `;
    document.head.appendChild(style);
});