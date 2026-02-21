class Renderer {
private:
    SDL_Window* window;
    SDL_Renderer* renderer;
    
    // 资源管理
    std::map<std::string, SDL_Texture*> textures;
    std::map<std::string, TTF_Font*> fonts;
    
public:
    bool init(int width, int height);
    void shutdown();
    
    // 渲染方法
    void render(const Paddle& paddle);
    void render(const Ball& ball);
    void render(const std::vector<std::shared_ptr<Brick>>& bricks);
    void renderUI(int score, int lives, GameState state);
    
    // 清屏和显示
    void clear();
    void present();
    
    // 资源管理
    SDL_Texture* loadTexture(const std::string& path);
    TTF_Font* loadFont(const std::string& path, int size);
};