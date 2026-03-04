let lastBoardState = null;

function drawBoard() {
  if (lastBoardState === null || lastBoardState !== board) {
    lastBoardState = board;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // 绘制棋盘和棋子
    // ...
  }
}