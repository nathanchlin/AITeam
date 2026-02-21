class BulletPool {
     constructor() {
       this.pool = [];
       this.active = [];
     }
     
     getBullet() {
       if (this.pool.length > 0) {
         const bullet = this.pool.pop();
         this.active.push(bullet);
         return bullet;
       }
       return new Bullet();
     }
     
     releaseBullet(bullet) {
       const index = this.active.indexOf(bullet);
       if (index > -1) {
         this.active.splice(index, 1);
         bullet.reset();
         this.pool.push(bullet);
       }
     }
   }