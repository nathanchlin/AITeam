// 引擎核心结构
typedef struct {
    // 渲染系统
    RenderSystem render;
    
    // 物理引擎
    PhysicsSystem physics;
    
    // 游戏对象管理
    GameObject* objects[MAX_OBJECTS];
    int object_count;
    
    // 输入处理
    InputState input;
    
    // 游戏状态
    GameState state;
} GameEngine;