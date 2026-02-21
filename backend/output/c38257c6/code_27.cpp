class SpatialHash {
public:
    void add(const Brick& brick) {
        // 根据砖块位置计算哈希值
        int cellX = static_cast<int>(brick.left / cellSize);
        int cellY = static_cast<int>(brick.top / cellSize);
        
        spatialHash[std::make_pair(cellX, cellY)].push_back(&brick);
    }
    
    std::vector<Brick*> getNearbyBricks(const Ball& ball) {
        std::vector<Brick*> nearbyBricks;
        
        // 计算球可能所在的网格单元
        int minCellX = static_cast<int>((ball.position.x - ball.radius) / cellSize);
        int maxCellX = static_cast<int>((ball.position.x + ball.radius) / cellSize);
        int minCellY = static_cast<int>((ball.position.y - ball.radius) / cellSize);
        int maxCellY = static_cast<int>((ball.position.y + ball.radius) / cellSize);
        
        // 检查所有可能包含碰撞砖块的网格单元
        for (int x = minCellX; x <= maxCellX; ++x) {
            for (int y = minCellY; y <= maxCellY; ++y) {
                auto it = spatialHash.find(std::make_pair(x, y));
                if (it != spatialHash.end()) {
                    nearbyBricks.insert(nearbyBricks.end(), it->second.begin(), it->second.end());
                }
            }
        }
        
        return nearbyBricks;
    }
    
private:
    std::unordered_map<std::pair<int, int>, std::vector<Brick*>> spatialHash;
    float cellSize = 50.0f; // 网格单元大小
};