class Renderer {
public:
    void initialize(int screenWidth, int screenHeight);
    void clear();
    void render(const GameObject& object);
    void renderText(const std::string& text, int x, int y, int fontSize);
    void present();
    
    // 纹理和资源管理
    Texture* loadTexture(const std::string& path);
    void unloadTexture(Texture* texture);
    
private:
    SDL_Renderer* renderer;
    std::unordered_map<std::string, std::unique_ptr<Texture>> textures;
};