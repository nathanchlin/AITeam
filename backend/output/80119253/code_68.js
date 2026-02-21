// 初始化游戏
const game = new Game();

// 开始新游戏
game.start();

// 获取当前玩家
game.getCurrentPlayer();

// 落子
game.makeMove(row, col);

// 悔棋
game.undo();

// 结束游戏
game.end();