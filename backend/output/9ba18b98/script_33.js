const tetrominoPool = [];

function getTetromino() {
  if (tetrominoPool.length > 0) {
    return tetrominoPool.pop();
  }
  return new Tetromino();
}

function releaseTetromino(tetromino) {
  tetromino.reset();
  tetrominoPool.push(tetromino);
}