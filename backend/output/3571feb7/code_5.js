// 移动组件
class MovementComponent {
  constructor(speed = 100) {
    this.speed = speed;
    this.velocity = { x: 0, y: 0 };
  }

  update(deltaTime) {
    const entity = this.entity;
    entity.x += this.velocity.x * deltaTime;
    entity.y += this.velocity.y * deltaTime;
  }
}

// 碰撞检测组件
class CollisionComponent {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }

  checkCollision(other) {
    const a = this.entity;
    const b = other.entity;
    
    return a.x < b.x + b.width &&
           a.x + this.width > b.x &&
           a.y < b.y + b.height &&
           a.y + this.height > b.y;
  }
}

// 豆子组件
class DotComponent {
  constructor(value = 10) {
    this.value = value;
    this.collected = false;
  }
}

// 敌人AI组件
class EnemyAIComponent {
  constructor(speed = 80, chaseRadius = 200) {
    this.speed = speed;
    this.chaseRadius = chaseRadius;
    this.patrolDirection = { x: 1, y: 0 };
    this.patrolTimer = 0;
  }

  update(deltaTime) {
    const entity = this.entity;
    const player = this.stateMachine.game.player;
    
    // 计算到玩家的距离
    const dx = player.x - entity.x;
    const dy = player.y - entity.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance < this.chaseRadius) {
      // 追逐玩家
      const movement = entity.getComponent('Movement');
      if (movement) {
        movement.velocity.x = (dx / distance) * this.speed;
        movement.velocity.y = (dy / distance) * this.speed;
      }
    } else {
      // 巡逻行为
      this.patrolTimer += deltaTime;
      if (this.patrolTimer > 2) {
        this.patrolDirection.x = Math.random() * 2 - 1;
        this.patrolDirection.y = Math.random() * 2 - 1;
        this.patrolTimer = 0;
      }
      
      const movement = entity.getComponent('Movement');
      if (movement) {
        movement.velocity.x = this.patrolDirection.x * this.speed;
        movement.velocity.y = this.patrolDirection.y * this.speed;
      }
    }
  }
}