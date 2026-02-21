// 视锥体剔除实现
class FrustumCulling {
private:
    glm::vec4 planes[6]; // 6个视锥体平面
    
public:
    void updateFromCamera(const Camera& camera) {
        // 根据相机位置和方向计算视锥体平面
    }
    
    bool isInFrustum(const BoundingBox& box) {
        // 检查包围盒是否在视锥体内
        for (int i = 0; i < 6; i++) {
            if (!box.isOnPositiveSide(planes[i])) {
                return false;
            }
        }
        return true;
    }
};

// 渲染循环优化
void renderScene() {
    frustum.updateFromCamera(camera);
    
    for (auto& layer : layers) {
        // 只渲染视锥体内的层
        if (frustum.isInFrustum(layer.boundingBox)) {
            layer.render();
        }
    }
}