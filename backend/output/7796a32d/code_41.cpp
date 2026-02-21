// LOD系统实现
class LODSystem {
private:
    struct LODLevel {
        float distance;
        std::string modelPath;
        int complexity; // 0-1, 1为最高细节
    };
    
    std::vector<LODLevel> lodLevels;
    
public:
    std::string getModelForDistance(float distance) {
        // 返回适合当前距离的模型
        for (int i = lodLevels.size() - 1; i >= 0; i--) {
            if (distance > lodLevels[i].distance) {
                return lodLevels[i].modelPath;
            }
        }
        return lodLevels[0].modelPath; // 最近距离的最高细节模型
    }
};

// 在渲染循环中使用
void renderEntity(Entity& entity) {
    float distance = calculateDistance(entity.position, camera.position);
    std::string modelPath = lodSystem.getModelForDistance(distance);
    
    loadAndRenderModel(modelPath, entity.position);
}