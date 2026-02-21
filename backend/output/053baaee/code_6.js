// 碰撞检测系统
class CollisionSystem {
    constructor(game) {
        this.game = game;
        this.quadTree = null;
    }
    
    // 更新四叉树
    updateQuadTree() {
        const boundary = {
            x: 0,
            y: 0,
            width: this.game.canvas.width,
            height: this.game.canvas.height
        };
        
        this.quadTree = new QuadTree(boundary, 4);
        
        // 插入所有游戏对象
        this.game.tanks.forEach(tank => this.quadTree.insert(tank));
        this.game.bullets.forEach(bullet => this.quadTree.insert(bullet));
        this.game.obstacles.forEach(obstacle => this.quadTree.insert(obstacle));
    }
    
    // 检测所有碰撞
    checkCollisions() {
        this.updateQuadTree();
        
        // 子弹碰撞检测
        this.checkBulletCollisions();
        
        // 坦克碰撞检测
        this.checkTankCollisions();
        
        // 坦克与障碍物碰撞检测
        this.checkTankObstacleCollisions();
    }
    
    // 子弹碰撞检测
    checkBulletCollisions() {
        for (let i = 0; i < this.game.bullets.length; i++) {
            const bullet = this.game.bullets[i];
            
            // 查询可能碰撞的对象
            const potentialTargets = this.quadTree.query({
                x: bullet.x - bullet.radius,
                y: bullet.y - bullet.radius,
                width: bullet.radius * 2,
                height: bullet.radius * 2
            });
            
            for (const target of potentialTargets) {
                if (bullet.owner === target) continue; // 子弹不会击中发射者
                
                if (checkBulletTargetCollision(bullet, target)) {
                    // 处理碰撞
                    if (target.type === 'tank') {
                        this.handleTankHit(target, bullet);
                    } else if (target.type === 'obstacle') {
                        this.handleObstacleHit(target, bullet);
                    }
                    
                    // 移除子弹
                    this.game.bullets.splice(i, 1);
                    i--;
                    break;
                }
            }
        }
    }
    
    // 坦克碰撞检测
    checkTankCollisions() {
        for (let i = 0; i < this.game.tanks.length; i++) {
            for (let j = i + 1; j < this.game.tanks.length; j++) {
                const tank1 = this.game.tanks[i];
                const tank2 = this.game.tanks[j];
                
                if (checkTankCollision(tank1, tank2)) {
                    this.handleTankTankCollision(tank1, tank2);
                }
            }
        }
    }
    
    // 坦克与障碍物碰撞检测
    checkTankObstacleCollisions() {
        for (const tank of this.game.tanks) {
            for (const obstacle of this.game.obstacles) {
                if (checkTankObstacleCollision(tank, obstacle)) {
                    this.handleTankObstacleCollision(tank, obstacle);
                }
            }
        }
    }
    
    // 处理坦克被击中
    handleTankHit(tank, bullet) {
        tank.health -= bullet.damage;
        
        if (tank.health <= 0) {
            // 坦克被摧毁
            if (tank.type === 'enemy') {
                this.game.score += 100;
            } else {
                this.game.gameOver = true;
            }
            
            // 移除坦克
            const index = this.game.tanks.indexOf(tank);
            if (index !== -1) {
                this.game.tanks.splice(index, 1);
            }
        }
    }
    
    // 处理障碍物被击中
    handleObstacleHit(obstacle, bullet) {
        obstacle.health -= bullet.damage;
        
        if (obstacle.health <= 0) {
            // 移除障碍物
            const index = this.game.obstacles.indexOf(obstacle);
            if (index !== -1) {
                this.game.obstacles.splice(index, 1);
            }
        }
    }
    
    // 处理坦克间碰撞
    handleTankTankCollision(tank1, tank2) {
        // 计算碰撞响应
        const dx = tank2.x - tank1.x;
        const dy = tank2.y - tank1.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance === 0) return; // 避免除以零
        
        // 归一化方向向量
        const nx = dx / distance;
        const ny = dy / distance;
        
        // 计算相对速度
        const dvx = tank2.vx - tank1.vx;
        const dvy = tank2.vy - tank1.vy;
        
        // 计算相对速度在碰撞法线上的分量
        const velocityAlongNormal = dvx * nx + dvy * ny;
        
        // 如果物体正在分离，不处理
        if (velocityAlongNormal > 0) return;
        
        // 计算冲量
        const restitution = 0.5; // 弹性系数
        const impulse = 2 * velocityAlongNormal / (1/tank1.mass + 1/tank2.mass);
        
        // 应用冲量
        tank1.vx += impulse * nx / tank1.mass * restitution;
        tank1.vy += impulse * ny / tank1.mass * restitution;
        tank2.vx -= impulse * nx / tank2.mass * restitution;
        tank2.vy -= impulse * ny / tank2.mass * restitution;
        
        // 分离物体，防止重叠
        const overlap = tank1.radius + tank2.radius - distance;
        const separationX = nx * overlap * 0.5;
        const separationY = ny * overlap * 0.5;
        
        tank1.x -= separationX;
        tank1.y -= separationY;
        tank2.x += separationX;
        tank2.y += separationY;
    }
    
    // 处理坦克与障碍物碰撞
    handleTankObstacleCollision(tank, obstacle) {
        // 找到坦克中心到矩形最近点的向量
        const closestX = Math.max(obstacle.x, Math.min(tank.x, obstacle.x + obstacle.width));
        const closestY = Math.max(obstacle.y, Math.min(tank.y, obstacle.y + obstacle.height));
        
        const dx = tank.x - closestX;
        const dy = tank.y - closestY;
        
        // 计算碰撞法线
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance === 0) return; // 避免除以零
        
        const nx = dx / distance;
        const ny = dy / distance;
        
        // 计算相对速度在法线上的分量
        const velocityAlongNormal = tank.vx * nx + tank.vy * ny;
        
        // 如果物体正在分离，不处理
        if (velocityAlongNormal > 0) return;
        
        // 计算冲量
        const restitution = 0.5;
        const impulse = -velocityAlongNormal * (1 + restitution);
        
        // 应用冲量
        tank.vx += impulse * nx;
        tank.vy += impulse * ny;
        
        // 分离物体
        const overlap = tank.radius - distance;
        tank.x += nx * overlap;
        tank.y += ny * overlap;
    }
}

// 辅助函数：圆形与圆形碰撞检测
function checkTankCollision(tank1, tank2) {
    const dx = tank1.x - tank2.x;
    const dy = tank1.y - tank2.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const minDistance = tank1.radius + tank2.radius;
    
    return distance < minDistance;
}

// 辅助函数：圆形与矩形碰撞检测
function checkTankObstacleCollision(tank, obstacle) {
    const closestX = Math.max(obstacle.x, Math.min(tank.x, obstacle.x + obstacle.width));
    const closestY = Math.max(obstacle.y, Math.min(tank.y, obstacle.y + obstacle.height));
    
    const dx = tank.x - closestX;
    const dy = tank.y - closestY;
    
    return (dx * dx + dy * dy) < (tank.radius * tank.radius);
}

// 辅助函数：子弹与目标碰撞检测
function checkBulletTargetCollision(bullet, target) {
    if (target.type === 'tank') {
        // 圆形碰撞检测
        const dx = bullet.x - target.x;
        const dy = bullet.y - target.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < target.radius;
    } else if (target.type === 'obstacle') {
        // 矩形碰撞检测
        return bullet.x > target.x && 
               bullet.x < target.x + target.width &&
               bullet.y > target.y && 
               bullet.y < target.y + target.height;
    }
    return false;
}

// 四叉树实现
class QuadTree {
    constructor(boundary, capacity = 4) {
        this.boundary = boundary; // {x, y, width, height}
        this.capacity = capacity;
        this.objects = [];
        this.divided = false;
    }
    
    insert(object) {
        if (!this.contains(object)) {
            return false;
        }
        
        if (this.objects.length < this.capacity) {
            this.objects.push(object);
            return true;
        } else {
            if (!this.divided) {
                this.subdivide();
            }
            
            return (this.northeast.insert(object) ||
                    this.northwest.insert(object) ||
                    this.southeast.insert(object) ||
                    this.southwest.insert(object));
        }
    }
    
    contains(object) {
        return (object.x >= this.boundary.x - object.radius &&
                object.x <= this.boundary.x + this.boundary.width + object.radius &&
                object.y >= this.boundary.y - object.radius &&
                object.y <= this.boundary.y + this.boundary.height + object.radius);
    }
    
    subdivide() {
        const x = this.boundary.x;
        const y = this.boundary.y;
        const w = this.boundary.width / 2;
        const h = this.boundary.height / 2;
        
        const ne = {x: x + w, y: y, width: w, height: h};
        const nw = {x: x, y: y, width: w, height: h};
        const se = {x: x + w, y: y + h, width: w, height: h};
        const sw = {x: x, y: y + h, width: w, height: h};
        
        this.northeast = new QuadTree(ne, this.capacity);
        this.northwest = new QuadTree(nw, this.capacity);
        this.southeast = new QuadTree(se, this.capacity);
        this.southwest = new QuadTree(sw, this.capacity);
        
        this.divided = true;
    }
    
    query(range, found = []) {
        if (!this.intersects(range)) {
            return found;
        }
        
        for (const object of this.objects) {
            if (this.rangeContains(range, object)) {
                found.push(object);
            }
        }
        
        if (this.divided) {
            this.northeast.query(range, found);
            this.northwest.query(range, found);
            this.southeast.query(range, found);
            this.southwest.query(range, found);
        }
        
        return found;
    }
    
    intersects(range) {
        return !(range.x > this.boundary.x + this.boundary.width ||
                range.x + range.width < this.boundary.x ||
                range.y > this.boundary.y + this.boundary.height ||
                range.y + range.height < this.boundary.y);
    }
    
    rangeContains(range, object) {
        return (object.x >= range.x &&
                object.x <= range.x + range.width &&
                object.y >= range.y &&
                object.y <= range.y + range.height);
    }
}