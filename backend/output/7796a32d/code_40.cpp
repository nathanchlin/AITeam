// 批量渲染实现
class BatchRenderer {
private:
    std::vector<RenderBatch> batches;
    
public:
    void addSprite(const Sprite& sprite) {
        // 检查是否可以添加到现有批次
        // 否则创建新批次
    }
    
    void render() {
        // 一次性渲染所有批次
        for (auto& batch : batches) {
            batch.render();
        }
        batches.clear();
    }
};

// 纹理图集使用
class TextureAtlas {
private:
    GLuint textureId;
    std::map<std::string, glm::vec4> uvRects; // 纹理名称到UV坐标的映射
    
public:
    glm::vec4 getUVRect(const std::string& textureName) {
        return uvRects[textureName];
    }
    
    void bind() {
        glBindTexture(GL_TEXTURE_2D, textureId);
    }
};

// 使用示例
void renderPlayer(Player& player) {
    TextureAtlas atlas;
    atlas.bind();
    
    glm::vec4 uvRect = atlas.getUVRect("player");
    
    // 使用单个批次渲染所有玩家精灵
    batchRenderer.addSprite(Sprite(player.position, player.size, uvRect));
}