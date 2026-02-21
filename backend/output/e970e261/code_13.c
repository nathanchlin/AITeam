// 地图块类型枚举
typedef enum {
    BLOCK_EMPTY = 0,
    BLOCK_GROUND,
    BLOCK_BRICK,
    BLOCK_QUESTION,
    BLOCK_COIN,
    BLOCK_PIPE,
    BLOCK_FLAGPOLE,
    BLOCK_CASTLE
} BlockType;

// 地图块结构
typedef struct {
    BlockType type;
    int x;
    int y;
    int is_visible;
    int has_item;
    int is_passable;
} Block;

// 地图结构
typedef struct {
    Block** grid;
    int width;
    int height;
    int camera_x;
    int camera_y;
} GameMap;