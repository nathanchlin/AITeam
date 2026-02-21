// 处理玩家输入
   function handleInput(event) {
     switch(event.type) {
       case 'keydown':
         if (event.key === ' ') {
           game.shooting.startCharge();
         }
         break;
       case 'keyup':
         if (event.key === ' ') {
           game.shooting.endCharge();
         }
         break;
     }
   }