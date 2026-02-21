// 游戏常量
const BOARD_SIZE = 15;
const EMPTY = 0;
const BLACK = 1;
const WHITE = 2;

// 游戏状态变量
let board = [];
let currentPlayer = BLACK;
let gameOver = false;
let moveHistory = [];