#include <vector>
#include <algorithm>
#include <cmath>
#include <unordered_set>

// 前面定义的Vector2, Ball, Paddle, Brick结构体...

// 边界碰撞检测
bool checkBoundaryCollision(Ball& ball, float screenWidth, float screenHeight) {
    // 左右边界碰撞
    if (ball.position.x - ball.radius <= 0) {
        ball.position.x = ball.radius;
        ball.velocity.x = -ball.velocity.x;
    } else if (ball.position.x + ball.radius >= screenWidth) {
        ball.position.x = screenWidth - ball.radius;
        ball.velocity.x = -ball.velocity.x;
    }
    
    // 上边界碰撞
    if (ball.position.y - ball.radius <= 0) {
        ball.position.y = ball.radius;
        ball.velocity.y = -ball.velocity.y;
    }
    
    // 下边界碰撞（游戏结束条件）
    if (ball.position.y + ball.radius >= screenHeight) {
        return false; // 游戏结束
    }
    
    return true; // 游戏继续
}

// 挡板碰撞检测
bool checkPaddleCollision(Ball& ball, const Paddle& paddle) {
    // 找到挡板上最接近球的点
    float closestX = std::max(paddle.position.x, 
                             std::min(ball.position.x, paddle.position.x + paddle.width));
    float closestY = std::max(paddle.position.y, 
                             std::min(ball.position.y, paddle.position.y + paddle.height));
    
    // 计算球心到最近点的距离
    float distanceX = ball.position.x - closestX;
    float distanceY = ball.position.y - closestY;
    float distanceSquared = distanceX * distanceX + distanceY * distanceY;
    
    // 如果距离小于球的半径，则发生碰撞
    if (distanceSquared < ball.radius * ball.radius) {
        // 计算碰撞法线
        float distance = sqrt(distanceSquared);
        Vector2 normal = {distanceX / distance, distanceY / distance};
        
        // 将球移出挡板
        ball.position.x = closestX + normal.x * ball.radius;
        ball.position.y = closestY + normal.y * ball.radius;
        
        // 计算反射向量
        float dotProduct = ball.velocity.x * normal.x + ball.velocity.y * normal.y;
        ball.velocity.x = ball.velocity.x - 2 * dotProduct * normal.x;
        ball.velocity.y = ball.velocity.y - 2 * dotProduct * normal.y;
        
        // 根据碰撞位置调整反弹角度
        float hitPosition = (ball.position.x - paddle.position.x) / paddle.width;
        ball.velocity.x = (hitPosition - 0.5f) * 10.0f;
        
        return true;
    }
    
    return false;
}

// 砖块碰撞检测
bool checkBrickCollision(Ball& ball, Brick& brick) {
    if (!brick.active) return false;
    
    // 找到砖块上最接近球的点
    float closestX = std::max(brick.position.x, 
                             std::min(ball.position.x, brick.position.x + brick.width));
    float closestY = std::max(brick.position.y, 
                             std::min(ball.position.y, brick.position.y + brick.height));
    
    // 计算球心到最近点的距离
    float distanceX = ball.position.x - closestX;
    float distanceY = ball.position.y - closestY;
    float distanceSquared = distanceX * distanceX + distanceY * distanceY;
    
    // 如果距离小于球的半径，则发生碰撞
    if (distanceSquared < ball.radius * ball.radius) {
        // 计算碰撞法线
        float distance = sqrt(distanceSquared);
        Vector2 normal = {distanceX / distance, distanceY / distance};
        
        // 将球移出砖块
        ball.position.x = closestX + normal.x * ball.radius;
        ball.position.y = closestY + normal.y * ball.radius;
        
        // 计算反射向量
        float dotProduct = ball.velocity.x * normal.x + ball.velocity.y * normal.y;
        ball.velocity.x = ball.velocity.x - 2 * dotProduct * normal.x;
        ball.velocity.y = ball.velocity.y - 2 * dotProduct * normal.y;
        
        // 标记砖块为不活跃
        brick.active = false;
        
        return true;
    }
    
    return false;
}

// 空间网格实现
struct SpatialGrid {
    std::vector<std::vector<Brick*>> grid;
    float cellSize;
    int gridWidth, gridHeight;
    
    SpatialGrid(float cellSize, int width, int height) 
        : cellSize(cellSize), gridWidth(width / cellSize), gridHeight(height / cellSize) {
        grid.resize(gridWidth * gridHeight);
    }
    
    void clear() {
        for (auto& cell : grid) {
            cell.clear();
        }
    }
    
    void add(Brick& brick) {
        int minX = std::max(0, (int)(brick.position.x / cellSize));
        int maxX = std::min(gridWidth - 1, (int)((brick.position.x + brick.width) / cellSize));
        int minY = std::max(0, (int)(brick.position.y / cellSize));
        int maxY = std::min(gridHeight - 1, (int)((brick.position.y + brick.height) / cellSize));
        
        for (int y = minY; y <= maxY; ++y) {
            for (int x = minX; x <= maxX; ++x) {
                grid[y * gridWidth + x].push_back(&brick);
            }
        }
    }
    
    std::vector<Brick*> getNearbyBricks(const Ball& ball) {
        int minX = std::max(0, (int)((ball.position.x - ball.radius) / cellSize));
        int maxX = std::min(gridWidth - 1, (int)((ball.position.x + ball.radius) / cellSize));
        int minY = std::max(0, (int)((ball.position.y - ball.radius) / cellSize));
        int maxY = std::min(gridHeight - 1, (int)((ball.position.y + ball.radius) / cellSize));
        
        std::vector<Brick*> nearbyBricks;
        std::unordered_set<Brick*> uniqueBricks;
        
        for (int y = minY; y <= maxY; ++y) {
            for (int x = minX; x <= maxX; ++x) {
                for (Brick* brick : grid[y * gridWidth + x]) {
                    if (uniqueBricks.find(brick) == uniqueBricks.end()) {
                        uniqueBricks.insert(brick);
                        nearbyBricks.push_back(brick);
                    }
                }
            }
        }
        
        return nearbyBricks;
    }
};

// 主更新函数
void updateCollisions(Ball& ball, Paddle& paddle, std::vector<Brick>& bricks, 
                     SpatialGrid& spatialGrid, float screenWidth, float screenHeight) {
    // 检查边界碰撞
    if (!checkBoundaryCollision(ball, screenWidth, screenHeight)) {
        // 游戏结束
        return;
    }
    
    // 检查挡板碰撞
    checkPaddleCollision(ball, paddle);
    
    // 更新空间分区
    spatialGrid.clear();
    for (Brick& brick : bricks) {
        if (brick.active) {
            spatialGrid.add(brick);
        }
    }
    
    // 获取附近的砖块并检测碰撞
    std::vector<Brick*> nearbyBricks = spatialGrid.getNearbyBricks(ball);
    for (Brick* brick : nearbyBricks) {
        if (checkBrickCollision(ball, *brick)) {
            // 碰撞处理
        }
    }
}