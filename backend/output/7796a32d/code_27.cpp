// 简单的网格空间分区示例
class SpatialGrid {
private:
    std::vector<std::vector<std::vector<GameObject*>>> grid;
    int cellSize;
    int cols, rows;
    
public:
    void insert(GameObject* obj) {
        // 根据对象位置确定所属网格单元
        int cellX = obj->getBoundingBox().x / cellSize;
        int cellY = obj->getBoundingBox().y / cellSize;
        
        // 确保在网格范围内
        cellX = std::max(0, std::min(cellX, cols - 1));
        cellY = std::max(0, std::min(cellY, rows - 1));
        
        grid[cellY][cellX].push_back(obj);
    }
    
    std::vector<GameObject*> query(const Rect& area) {
        std::vector<GameObject*> result;
        
        // 计算查询区域覆盖的网格单元
        int startX = area.x / cellSize;
        int endX = (area.x + area.width) / cellSize;
        int startY = area.y / cellSize;
        int endY = (area.y + area.height) / cellSize;
        
        // 遍历相关网格单元
        for (int y = startY; y <= endY; ++y) {
            for (int x = startX; x <= endX; ++x) {
                if (y >= 0 && y < rows && x >= 0 && x < cols) {
                    result.insert(result.end(), grid[y][x].begin(), grid[y][x].end());
                }
            }
        }
        
        return result;
    }
};