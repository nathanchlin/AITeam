// 宝石类型枚举
enum GemType {
    RED = 'red',
    BLUE = 'blue',
    GREEN = 'green',
    YELLOW = 'yellow',
    PURPLE = 'purple',
    ORANGE = 'orange'
}

// 宝石接口
interface Gem {
    id: string;
    type: GemType;
    row: number;
    col: number;
    isMatched: boolean;
    scale: number; // 用于动画效果
}

// 游戏网格接口
interface GameGrid {
    rows: number;
    cols: number;
    gems: Gem[][];
}