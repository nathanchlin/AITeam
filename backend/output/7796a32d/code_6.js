class InputController {
  constructor(scene) {
    this.scene = scene;
    this.setupKeyboardControls();
    this.setupTouchControls();
  }
  
  setupKeyboardControls() {
    this.cursors = this.scene.input.keyboard.createCursorKeys();
  }
  
  setupTouchControls() {
    // 左右按钮
    const leftButton = this.scene.add.rectangle(50, 500, 80, 80, 0x888888);
    const rightButton = this.scene.add.rectangle(150, 500, 80, 80, 0x888888);
    const jumpButton = this.scene.add.rectangle(350, 500, 80, 80, 0x888888);
    
    leftButton.setInteractive();
    rightButton.setInteractive();
    jumpButton.setInteractive();
    
    leftButton.on('pointerdown', () => this.leftPressed = true);
    leftButton.on('pointerup', () => this.leftPressed = false);
    
    rightButton.on('pointerdown', () => this.rightPressed = true);
    rightButton.on('pointerup', () => this.rightPressed = false);
    
    jumpButton.on('pointerdown', () => this.jumpPressed = true);
    jumpButton.on('pointerup', () => this.jumpPressed = false);
  }
  
  isLeftPressed() {
    return this.cursors.left.isDown || this.leftPressed;
  }
  
  isRightPressed() {
    return this.cursors.right.isDown || this.rightPressed;
  }
  
  isJumpPressed() {
    return this.cursors.up.isDown || this.jumpPressed;
  }
}