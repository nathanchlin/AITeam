// 空间分区优化 - 使用四叉树(2D)或网格分区
class SpatialGrid {
private:
    std::vector<std::vector<Entity*>> grid;
    float cellSize;
    
public:
    void updateEntityPosition(Entity* entity) {
        // 从旧网格单元格移除
        // 计算新网格单元格
        // 添加到新单元格
    }
    
    std::vector<Entity*> getNearbyEntities(const Entity* entity) {
        // 只检查周围9个单元格的实体
    }
};

// 使用示例
SpatialGrid spatialGrid(50.0f); // 50单位大小的单元格

void updatePhysics() {
    // 1. 更新空间网格
    for (auto& entity : entities) {
        spatialGrid.updateEntityPosition(&entity);
    }
    
    // 2. 只检查附近的碰撞
    for (auto& player : players) {
        auto nearbyEntities = spatialGrid.getNearbyEntities(&player);
        for (auto& entity : nearbyEntities) {
            if (checkCollision(player, *entity)) {
                handleCollision(player, *entity);
            }
        }
    }
}