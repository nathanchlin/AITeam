class Player extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, x, y) {
    super(scene, x, y, 'player');
    
    scene.add.existing(this);
    scene.physics.add.existing(this);
    
    this.setBounce(0.2);
    this.setCollideWorldBounds(true);
    this.setGravityY(1500);
    
    this.cursors = scene.input.keyboard.createCursorKeys();
    this.isJumping = false;
    this.jumpPower = -400;
  }
  
  update() {
    // 左右移动
    if (this.cursors.left.isDown) {
      this.setVelocityX(-200);
    } else if (this.cursors.right.isDown) {
      this.setVelocityX(200);
    } else {
      this.setVelocityX(0);
    }
    
    // 跳跃
    if (this.cursors.up.isDown && this.body.touching.down) {
      this.setVelocityY(this.jumpPower);
      this.isJumping = true;
    }
  }
}