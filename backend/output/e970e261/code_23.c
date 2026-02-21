// 定义碰撞盒结构
typedef struct {
    int x;      // 左上角x坐标
    int y;      // 左上角y坐标
    int width;  // 宽度
    int height; // 高度
} CollisionBox;

// 定义实体类型
typedef enum {
    ENTITY_MARIO,
    ENTITY_ENEMY,
    ENTITY_BLOCK,
    ENTITY_COIN,
    ENTITY_PIPE
} EntityType;

// 定义实体结构
typedef struct {
    int x;
    int y;
    int width;
    int height;
    EntityType type;
    int isSolid; // 是否可碰撞
    int isAlive;
} Entity;