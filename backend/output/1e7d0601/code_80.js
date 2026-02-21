// 优化射击系统
class ResponsiveShooting {
  constructor(game) {
    this.game = game;
    this.canShoot = true;
    this.isCharging = false;
    this.chargeLevel = 0;
  }
  
  startCharge() {
    this.isCharging = true;
    this.chargeLevel = 0;
  }
  
  endCharge() {
    if (this.isCharging) {
      this.isCharging = false;
      if (this.chargeLevel > 30) { // 充能时间阈值
        this.fireSpecial();
      } else {
        this.fireNormal();
      }
      this.chargeLevel = 0;
    }
  }
  
  update() {
    if (this.isCharging) {
      this.chargeLevel++;
    }
  }
  
  fireNormal() {
    if (this.canShoot) {
      // 发射普通子弹
      this.game.createBullet(this.game.player.x, this.game.player.y);
      this.canShoot = false;
      setTimeout(() => this.canShoot = true, planeControls.shotCooldown);
    }
  }
  
  fireSpecial() {
    // 发射特殊武器
    this.game.createSpecialWeapon(this.game.player.x, this.game.player.y);
    this.canShoot = false;
    setTimeout(() => this.canShoot = true, planeControls.specialCooldown);
  }
}