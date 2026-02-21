/**
 * 五子棋游戏状态管理模块
 */

// 游戏状态常量
const GameStatus = {
    PLAYING: 'playing',
    WIN: 'win',
    DRAW: 'draw'
};

// 玩家常量
const Player = {
    BLACK: 'black',
    WHITE: 'white'
};

/**
 * 游戏状态管理类
 */
class GameStateManager {
    /**
     * 构造函数
     * @param {number} boardSize - 棋盘大小，默认为15
     */
    constructor(boardSize = 15) {
        this.boardSize = boardSize;
        this.reset();
    }
    
    /**
     * 重置游戏状态
     */
    reset() {
        // 初始化棋盘，0表示空，1表示黑子，2表示白子
        this.board = Array(this.boardSize).fill(null).map(() => Array(this.boardSize).fill(0));
        this.currentPlayer = Player.BLACK;
        this.gameStatus = GameStatus.PLAYING;
        this.moveHistory = [];
        this.winningLine = [];
    }
    
    /**
     * 获取当前玩家
     * @returns {string} 当前玩家
     */
    getCurrentPlayer() {
        return this.currentPlayer;
    }
    
    /**
     * 获取游戏状态
     * @returns {string} 游戏状态
     */
    getGameStatus() {
        return this.gameStatus;
    }
    
    /**
     * 获取棋盘状态
     * @returns {number[][]} 棋盘状态
     */
    getBoard() {
        return this.board;
    }
    
    /**
     * 获取移动历史
     * @returns {Array} 移动历史
     */
    getMoveHistory() {
        return this.moveHistory;
    }
    
    /**
     * 获取获胜线
     * @returns {Array} 获胜线坐标
     */
    getWinningLine() {
        return this.winningLine;
    }
    
    /**
     * 尝试落子
     * @param {number} row - 行索引
     * @param {number} col - 列索引
     * @returns {boolean} 是否成功落子
     */
    placePiece(row, col) {
        // 检查游戏是否已结束
        if (this.gameStatus !== GameStatus.PLAYING) {
            return false;
        }
        
        // 检查位置是否有效
        if (row < 0 || row >= this.boardSize || col < 0 || col >= this.boardSize) {
            return false;
        }
        
        // 检查位置是否已有棋子
        if (this.board[row][col] !== 0) {
            return false;
        }
        
        // 记录移动
        this.moveHistory.push({
            row,
            col,
            player: this.currentPlayer
        });
        
        // 放置棋子
        this.board[row][col] = this.currentPlayer === Player.BLACK ? 1 : 2;
        
        // 检查是否获胜
        if (this.checkWin(row, col)) {
            this.gameStatus = GameStatus.WIN;
            return true;
        }
        
        // 检查是否平局
        if (this.checkDraw()) {
            this.gameStatus = GameStatus.DRAW;
            return true;
        }
        
        // 切换玩家
        this.currentPlayer = this.currentPlayer === Player.BLACK ? Player.WHITE : Player.BLACK;
        return true;
    }
    
    /**
     * 检查是否获胜
     * @param {number} row - 最后落子的行索引
     * @param {number} col - 最后落子的列索引
     * @returns {boolean} 是否获胜
     */
    checkWin(row, col) {
        const directions = [
            [0, 1],   // 水平
            [1, 0],   // 垂直
            [1, 1],   // 对角线 \
            [1, -1]   // 对角线 /
        ];
        
        const playerValue = this.board[row][col];
        
        for (const [dx, dy] of directions) {
            let count = 1;
            const line = [[row, col]];
            
            // 正向检查
            for (let i = 1; i < 5; i++) {
                const newRow = row + dx * i;
                const newCol = col + dy * i;
                
                if (newRow < 0 || newRow >= this.boardSize || 
                    newCol < 0 || newCol >= this.boardSize || 
                    this.board[newRow][newCol] !== playerValue) {
                    break;
                }
                
                count++;
                line.push([newRow, newCol]);
            }
            
            // 反向检查
            for (let i = 1; i < 5; i++) {
                const newRow = row - dx * i;
                const newCol = col - dy * i;
                
                if (newRow < 0 || newRow >= this.boardSize || 
                    newCol < 0 || newCol >= this.boardSize || 
                    this.board[newRow][newCol] !== playerValue) {
                    break;
                }
                
                count++;
                line.unshift([newRow, newCol]);
            }
            
            // 如果有5个或更多连续棋子，则获胜
            if (count >= 5) {
                this.winningLine = line.slice(0, 5);
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * 检查是否平局
     * @returns {boolean} 是否平局
     */
    checkDraw() {
        // 检查棋盘是否已满
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                if (this.board[row][col] === 0) {
                    return false;
                }
            }
        }
        return true;
    }
    
    /**
     * 悔棋
     * @returns {boolean} 是否成功悔棋
     */
    undo() {
        // 如果没有移动历史或游戏已结束，不能悔棋
        if (this.moveHistory.length === 0 || this.gameStatus !== GameStatus.PLAYING) {
            return false;
        }
        
        // 获取最后一步
        const lastMove = this.moveHistory.pop();
        
        // 恢复棋盘状态
        this.board[lastMove.row][lastMove.col] = 0;
        
        // 切换回上一个玩家
        this.currentPlayer = lastMove.player;
        
        return true;
    }
    
    /**
     * 重新开始游戏
     */
    restart() {
        this.reset();
    }
}

/**
 * 棋盘渲染类
 */
class BoardRenderer {
    /**
     * 构造函数
     * @param {HTMLElement} container - 容器元素
     * @param {GameStateManager} gameStateManager - 游戏状态管理器
     */
    constructor(container, gameStateManager) {
        this.container = container;
        this.gameStateManager = gameStateManager;
        this.cellSize = 30; // 每个格子的大小
        this.boardElement = null;
        this.statusElement = null;
        this.init();
    }
    
    /**
     * 初始化UI
     */
    init() {
        // 创建棋盘容器
        this.boardElement = document.createElement('div');
        this.boardElement.className = 'board';
        this.boardElement.style.position = 'relative';
        this.boardElement.style.width = `${this.gameStateManager.boardSize * this.cellSize}px`;
        this.boardElement.style.height = `${this.gameStateManager.boardSize * this.cellSize}px`;
        
        // 创建网格线
        for (let i = 0; i < this.gameStateManager.boardSize; i++) {
            // 横线
            const hLine = document.createElement('div');
            hLine.style.position = 'absolute';
            hLine.style.width = '100%';
            hLine.style.height = '1px';
            hLine.style.backgroundColor = '#000';
            hLine.style.top = `${i * this.cellSize}px`;
            this.boardElement.appendChild(hLine);
            
            // 竖线
            const vLine = document.createElement('div');
            vLine.style.position = 'absolute';
            vLine.style.width = '1px';
            vLine.style.height = '100%';
            vLine.style.backgroundColor = '#000';
            vLine.style.left = `${i * this.cellSize}px`;
            this.boardElement.appendChild(vLine);
        }
        
        // 创建状态显示
        this.statusElement = document.createElement('div');
        this.statusElement.className = 'status';
        this.statusElement.style.marginTop = '20px';
        this.statusElement.style.textAlign = 'center';
        this.statusElement.style.fontSize = '18px';
        
        // 添加到容器
        this.container.appendChild(this.boardElement);
        this.container.appendChild(this.statusElement);
        
        // 添加点击事件
        this.boardElement.addEventListener('click', (e) => this.handleClick(e));
        
        // 添加按钮
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '20px';
        buttonContainer.style.textAlign = 'center';
        
        const undoButton = document.createElement('button');
        undoButton.textContent = '悔棋';
        undoButton.style.marginRight = '10px';
        undoButton.addEventListener('click', () => this.undo());
        
        const restartButton = document.createElement('button');
        restartButton.textContent = '重新开始';
        restartButton.addEventListener('click', () => this.restart());
        
        buttonContainer.appendChild(undoButton);
        buttonContainer.appendChild(restartButton);
        this.container.appendChild(buttonContainer);
        
        // 初始渲染
        this.render();
    }
    
    /**
     * 处理点击事件
     * @param {MouseEvent} e - 点击事件
     */
    handleClick(e) {
        const rect = this.boardElement.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const col = Math.round(x / this.cellSize) - 1;
        const row = Math.round(y / this.cellSize) - 1;
        
        // 落子
        if (this.gameStateManager.placePiece(row, col)) {
            this.render();
        }
    }
    
    /**
     * 渲染棋盘
     */
    render() {
        // 清除所有棋子
        const pieces = this.boardElement.querySelectorAll('.piece');
        pieces.forEach(piece => piece.remove());
        
        // 渲染棋子
        const board = this.gameStateManager.getBoard();
        for (let row = 0; row < this.gameStateManager.boardSize; row++) {
            for (let col = 0; col < this.gameStateManager.boardSize; col++) {
                if (board[row][col] !== 0) {
                    const piece = document.createElement('div');
                    piece.className = 'piece';
                    piece.style.position = 'absolute';
                    piece.style.width = `${this.cellSize * 0.8}px`;
                    piece.style.height = `${this.cellSize * 0.8}px`;
                    piece.style.borderRadius = '50%';
                    piece.style.left = `${col * this.cellSize - this.cellSize * 0.4}px`;
                    piece.style.top = `${row * this.cellSize - this.cellSize * 0.4}px`;
                    piece.style.backgroundColor = board[row][col] === 1 ? '#000' : '#fff';
                    piece.style.border = board[row][col] === 2 ? '1px solid #000' : 'none';
                    this.boardElement.appendChild(piece);
                }
            }
        }
        
        // 渲染获胜线
        if (this.gameStateManager.getGameStatus() === GameStatus.WIN) {
            const winningLine = this.gameStateManager.getWinningLine();
            for (const [row, col] of winningLine) {
                const mark = document.createElement('div');
                mark.className = 'win-mark';
                mark.style.position = 'absolute';
                mark.style.width = `${this.cellSize * 0.8}px`;
                mark.style.height = `${this.cellSize * 0.8}px`;
                mark.style.borderRadius = '50%';
                mark.style.left = `${col * this.cellSize - this.cellSize * 0.4}px`;
                mark.style.top = `${row * this.cellSize - this.cellSize * 0.4}px`;
                mark.style.border = '2px solid red';
                mark.style.pointerEvents = 'none';
                this.boardElement.appendChild(mark);
            }
        }
        
        // 更新状态显示
        this.updateStatus();
    }
    
    /**
     * 更新状态显示
     */
    updateStatus() {
        const status = this.gameStateManager.getGameStatus();
        const currentPlayer = this.gameStateManager.getCurrentPlayer();
        
        if (status === GameStatus.PLAYING) {
            this.statusElement.textContent = `当前玩家: ${currentPlayer === Player.BLACK ? '黑子' : '白子'}`;
        } else if (status === GameStatus.WIN) {
            const winner = currentPlayer === Player.BLACK ? '白子' : '黑子';
            this.statusElement.textContent = `游戏结束! ${winner}获胜!`;
        } else if (status === GameStatus.DRAW) {
            this.statusElement.textContent = '游戏结束! 平局!';
        }
    }
    
    /**
     * 悔棋
     */
    undo() {
        if (this.gameStateManager.undo()) {
            this.render();
        }
    }
    
    /**
     * 重新开始
     */
    restart() {
        this.gameStateManager.restart();
        this.render();
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('game-container');
    const gameStateManager = new GameStateManager();
    const boardRenderer = new BoardRenderer(container, gameStateManager);
});