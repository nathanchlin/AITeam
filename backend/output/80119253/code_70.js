// 监听游戏事件
game.on('move', (data) => {
  console.log(`玩家 ${data.player} 在 (${data.row}, ${data.col}) 落子`);
});

game.on('win', (data) => {
  console.log(`玩家 ${data.player} 获胜！`);
});