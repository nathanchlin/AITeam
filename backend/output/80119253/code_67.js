// 初始化棋盘
const board = new Board();

// 获取棋盘状态
board.getState();

// 在指定位置落子
board.placePiece(row, col, player);

// 检查是否获胜
board.checkWin(row, col, player);

// 重置棋盘
board.reset();