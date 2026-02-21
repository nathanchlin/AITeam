// 在游戏主循环中
   function gameLoop() {
     // 更新游戏状态
     game.update();
     
     // 更新所有组件
     game.components.forEach(component => {
       if (component.update) component.update();
     });
     
     // 渲染
     game.render();
     
     requestAnimationFrame(gameLoop);
   }