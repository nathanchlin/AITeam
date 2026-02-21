// 创建宝石对象池
   class GemPool {
     constructor() {
       this.pool = [];
       this.maxSize = 64; // 8x8网格最大宝石数
     }
     
     acquire() {
       if (this.pool.length > 0) {
         return this.pool.pop();
       }
       return document.createElement('div');
     }
     
     release(gem) {
       if (this.pool.length < this.maxSize) {
         gem.className = '';
         gem.style.transform = '';
         gem.style.opacity = '';
         this.pool.push(gem);
       } else {
         gem.remove();
       }
     }
   }