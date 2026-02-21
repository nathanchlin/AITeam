// 简单的网格空间分区
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