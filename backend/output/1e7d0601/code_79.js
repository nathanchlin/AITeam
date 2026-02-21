// 平滑移动实现
class SmoothMovement {
  constructor(plane) {
    this.plane = plane;
    this.velocity = { x: 0, y: 0 };
    this.targetPosition = { x: plane.x, y: plane.y };
  }
  
  update(targetX, targetY) {
    // 计算目标位置
    this.targetPosition.x = targetX;
    this.targetPosition.y = targetY;
    
    // 计算速度向量
    const dx = this.targetPosition.x - this.plane.x;
    const dy = this.targetPosition.y - this.plane.y;
    
    // 应用加速度
    this.velocity.x += dx * planeControls.acceleration;
    this.velocity.y += dy * planeControls.acceleration;
    
    // 限制最大速度
    const speed = Math.sqrt(this.velocity.x ** 2 + this.velocity.y ** 2);
    if (speed > planeControls.maxSpeed) {
      this.velocity.x = (this.velocity.x / speed) * planeControls.maxSpeed;
      this.velocity.y = (this.velocity.y / speed) * planeControls.maxSpeed;
    }
    
    // 应用摩擦力
    this.velocity.x *= planeControls.friction;
    this.velocity.y *= planeControls.friction;
    
    // 更新位置
    this.plane.x += this.velocity.x;
    this.plane.y += this.velocity.y;
  }
}